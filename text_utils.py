# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 09:11:33 2020

@author: tan185
"""

# process the text file

import re
import urllib
from config import *
from bs4 import BeautifulSoup
import tldextract

def read_text(file_dir):
    with open(file_dir, 'r',errors='ignore') as text:
        text = text.read()
    return text

def split_text(text):
    title_re = r'\n\nFrom .* [\d\d\d\d|\d\d\d\d +0000]'
    text_part = re.split(title_re, text)
    text_part_new = []
    for t in text_part:
        t = re.sub(r'^.*',"",t)
#        t = re.sub(r'\n\s\s\s\s*.*\n',"",t)
        if t == "":
            continue
        text_part_new.append(t)
    
    return text_part_new

def is_multipart(text):
    mul_re = r'Content-Type: multipart/'
    mul_find = re.findall(mul_re, text)
    if mul_find:
        return True
    return False

def find_boundary(text):
    find_re = r'\nContent-Type: multipart/.*; boundary="(.*)"'
    find_part = re.findall(find_re, text)
    if find_part:
        return find_part
    else:
        find_re2 = r'\n*Content-Type: multipart/.*;*\s*\n*\W*boundary="*(.*)"*\n'
        find_part = re.findall(find_re2, text)
        return find_part
    return find_part

def get_num_dots(domain):
    return len(re.findall(r'\.',domain))

def get_content_type(text):
    cont_type_re = r'Content-Type: (.*);'
    cont_type = re.findall(cont_type_re, text)
    return str(cont_type)

def get_content_encoding(text):
    cont_encod_re = r'Content-Transfer-Encoding: (.*)'
    cont_encod = re.findall(cont_encod_re, text)
    return cont_encod

def body_split(msg, is_multipart):
    if is_multipart:    
        code = find_boundary(msg)
        print(code)
        print(msg)
        split_re = f'--{code[0]}'
        split_find = re.split(split_re, msg)
        split_find = split_find[1:]
        split_find = split_find[:-1]
    else:
        body_re = r'.*: .*\n.*: .*\n\n'
        body = re.split(body_re, msg)
        if len(body) == 1:
            return ""
        split_find = body[1]
        split_find = f"Content-transfer-encoding: {get_content_encoding(msg)};\nContent-Type: {(get_content_type(msg))[2:-2]};\n {split_find}"
    return split_find


def getpayload(msg):
    return __getpayload_rec__(msg, payloadresult=[])

def __getpayload_rec__(msg, payloadresult):
    if is_multipart(msg):
        part = body_split(msg, True)
        for p in part:
            if is_multipart(p):
               __getpayload_rec__(p, payloadresult)
            else:
                payloadresult.append(p)
                
    else:
        payloadresult.append(body_split(msg,False))
    return payloadresult

def getAttachmentCount(msg):
    part = getpayload(msg)
    att_count = 0
    for p in part:
        att_re = 'Content-Disposition: attachment'
        att_find = re.findall(att_re, p)
        if att_find:
            att_count += 1
    return att_count

def comb_all(message):
    combine = ""
    for p in getpayload(message):
        combine = combine + str(p)
    return combine

def isurl(link):
    return re.compile(URLREGEX, re.IGNORECASE).search(link) is not None

def geturls_string(string):
    result = []
    
    cleanPayload = re.sub(r'\s+', ' ', string)  # removes innecesary spaces
    cleanPayload = re.sub(r'\n', '', string)  # removes innecesary return
    linkregex = re.compile(HREFREGEX, re.IGNORECASE) #HREF is hyperlink
    links = linkregex.findall(cleanPayload)
    for link in links:
        print(link)
        if len(re.findall('http',link))>1:
            print(link)
            continue
        if isurl(link):
            
            result.append(link)
    
    urlregex = re.compile(URLREGEX_NOT_ALONE, re.IGNORECASE)
    links = urlregex.findall(cleanPayload)
    for link in links:
        if len(re.findall('http',link))>1:
            sublinks = re.split('[<>]',link)
            for sublink in sublinks:
                if sublink not in result and sublink !="":
                    result.append(sublink)
        elif link not in result:
            result.append(link)
    return result


def getIPHrefs(message):
    urls = geturls_string(message)
    iphref = re.compile(IPREGEX, re.IGNORECASE)
    result = []
    for url in urls:
        if iphref.search(url) and iphref.search(url).group(1) is not None:
            result.append(iphref.search(url).group(1))
    return result

def getjavascriptusage(message):
    """
    :param message: message
    :return: url list-
    """
    result = []
    payload = getpayload(message)
    for part in payload:
        if get_content_type(part) == "['text/html']":
            part = re.sub(r'Content-.*:.*\n',"",part)
#            part = re.sub(r'\n', "", part)
            htmlcontent = part
            soup = BeautifulSoup(htmlcontent, features="lxml")
            scripts = soup.findAll("script")
            for script in scripts:
                result.append(script)
    return result

def getcssusage(message):
    """
    :param message: message
    :return: url list-
    """
    result = []
    payload = getpayload(message)
    for part in payload:
        if  get_content_type(part) == "['text/html']":
            part = re.sub(r'Content-.*:.*\n',"",part)
#            part = re.sub(r'\n', "", part)
            htmlcontent = part
            soup = BeautifulSoup(htmlcontent, features="lxml")
            csslinks = soup.findAll("link")
            for css in csslinks:
                result.append(css)
    return result

def getexternalresources(message):
    """
    :param message: message
    :return: url list-
    """
    result = []

    for script in getjavascriptusage(message):
        if "src" in str(script) and "src" in script and isurl(script["src"]):
            result.append(script["src"])
    for css in getcssusage(message):
        if "href" in str(css) and isurl(css["href"]):
            result.append(css["href"])

    return result

def get_alexa_rank(url):
    xml = urllib.urlopen('http://data.alexa.com/data?cli=10&dat=s&url=%s' % url).read()
    try:
        rank = int(re.search(r'RANK="(\d+)"', xml).groups()[0])
    except:
        rank = -1
    return rank

def extract_registered_domain(url):
    return tldextract.extract(url).registered_domain

def ishtml(message):
    result = ("text/html" in get_content_type(message))
    return result
    

#Testing/troubleshooting
##a = read_text('fradulent_emails.txt')
#a = read_text('monkey_phishing_2018.txt')   
##a = read_text('short.txt')
#hey= split_text(a)
##see1 = getpayload(hey[5])
##see = getAttachmentCount(hey[5])
##comb= geturls_string(hey[5])
##IPHrefs = getIPHrefs(hey[5])