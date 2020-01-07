# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 09:09:11 2020

@author: tan185
"""
# process the text file

# coding=utf-8
import mailbox
import text_utils
import pandas as pd
import re
import csv
from config import *
from bs4 import BeautifulSoup
from abc import ABCMeta, abstractmethod

# Internal features

# HTML content  DONE
# HTML form    DONE
# iFrames      DONE
# Attachments  DONE
# Potential XSS calls
# Flash content  DONE
# External resources in HTML header (css, js) DONE
# Javascript usage to hide URL link
# Using “@” in URLS
# Using hexadecimal characters in URLS
# Nonmatching URLS
# URL lengths
# Hostname lengths
# HREFs to IPs DONE

class FeatureFinder:
    __metaclass__ = ABCMeta

    @abstractmethod
    def getFeatureTitle(self):
        pass

    @abstractmethod
    def getFeature(self, message):
        pass
    
class HTMLFormFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "Html Form"

    def getFeature(self, message):
        import re
        super(HTMLFormFinder, self).getFeature(message)    
        payload = text_utils.comb_all(message).lower()
        return re.compile(r'<\s?\/?\s?form\s?>', re.IGNORECASE).search(payload) != None

class IFrameFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "Html iFrame"

    def getFeature(self, message):
        import re
        super(IFrameFinder, self).getFeature(message)
        payload = text_utils.comb_all(message).lower()
        return re.compile(r'<\s?\/?\s?iframe\s?>', re.IGNORECASE).search(payload) != None

class FlashFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "Flash content"

    def getFeature(self, message):
        import re
        super(FlashFinder, self).getFeature(message)
        payload = text_utils.comb_all(message).lower()

        swflinks = re.compile(FLASH_LINKED_CONTENT, re.IGNORECASE).findall(payload)
        flashObject = re.compile(r'embed\s*src\s*=\s*\".*\.swf\"', re.IGNORECASE).search(payload);
        return (swflinks != None and len(swflinks) > 0) or \
               (flashObject != None)

class AttachmentFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "Attachments"

    def getFeature(self, message):
        return text_utils.getAttachmentCount(message)

class HTMLContentFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "HTML content"

    def getFeature(self, message):
        return text_utils.ishtml(message)

class URLsFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "URLs"

    def getFeature(self, message):
        return len(text_utils.geturls_payload(message))
    
class ExternalResourcesFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "External Resources"

    def getFeature(self, message):
        return len(text_utils.getexternalresources(message))
    
class JavascriptFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "Javascript"

    def getFeature(self, message):
        return len(text_utils.getjavascriptusage(message))

class CssFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "Css"

    def getFeature(self, message):
        return len(text_utils.getcssusage(message))

class IPsInURLs(FeatureFinder):
    def getFeatureTitle(self):
        return "IPs in URLs"

    def getFeature(self, message):
        return len(text_utils.getIPHrefs(message)) > 0
    
class AtInURLs(FeatureFinder):
    def getFeatureTitle(self):
        return "@ in URLs"

    def getFeature(self, message):
        emailPattern = re.compile(EMAILREGEX, re.IGNORECASE)
        for url in text_utils.geturls_payload(message):
            if (url.lower().startswith("mailto:") or (
                    emailPattern.search(url) != None and emailPattern.search(url).group() != None)):
                continue
#            print(url)
            atvalue = url.find("@")
            athexvalue = url.find("%40")

            if (atvalue != -1 and athexvalue != -1):
                atvalue = min(athexvalue, atvalue)
            else:
                atvalue = max(atvalue, athexvalue)

            paramindex = url.find("?")

            if paramindex != -1:  # url has parameters, an email can be a parameter
                if (atvalue != -1) and (paramindex > atvalue):
                    return True
            else:
                # There are no parameters in the url. if there is an @, then return true
                if (atvalue != -1):
                    return True
        return False

class EncodingFinder(FeatureFinder):
    def getFeatureTitle(self):
        return "Encoding"

    def getFeature(self, message):
        encod = text_utils.get_content_encoding(message)
        return encod

def processTextFile(filepath, phishy=True, limit=500):
    text = text_utils.read_text(filepath)
    i = 1
    data = []

    finders = [HTMLFormFinder(), AttachmentFinder(), FlashFinder(),
               IFrameFinder(), HTMLContentFinder(), URLsFinder(),
               ExternalResourcesFinder(), JavascriptFinder(),
               CssFinder(), IPsInURLs(), AtInURLs(), EncodingFinder()]
    text = text_utils.split_text(text)
    for message in text:
        dict = {}

        for finder in finders:
            dict[finder.getFeatureTitle()] = finder.getFeature(message)
        dict["Phishy"] = phishy
        data.append(dict)
        i += 1
        print(i)
        if limit and i >= limit:
            break

        

    df = pd.DataFrame(data)
#    df.to_csv(filepath + "-export.csv")

#    emails = pd.DataFrame(email_index)
#    emails.to_csv(filepath + "-export-index.csv")
    
    return data
    


#dd=processFile('fradulent_emails.txt',100000)    
#dd=processFile('short.txt')
#dd=processFile('monkey_phishing_2015.txt') 

