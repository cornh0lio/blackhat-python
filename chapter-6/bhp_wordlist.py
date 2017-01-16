from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import re
from datetime import datetime
from HTMLParser import HTMLParser

class TagStripper(HTMLParser):
        
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_text = []
    
    # this function stores the page text in a member variable
    def handle_data(self, data):
        self.page_text.append(data)
    
    # we also grab the comments left by the developers
    def handle_comment(self, data):
        self.handle_data(data)

    # this function feeds HTML code to the base class HTMLParser and
    # returns the resulting page text
    def strip(self, html):
        self.feed(html)
        return " ".join(self.page_text)


class BurpExtender(IBurpExtender, IContextMenuFactory):
    
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None
        self.hosts = set()

        # start with something we know is common
        # this time we store our wordlist in a set to avoid duplicates
        self.wordlist = set(["password"])

        # we set up our extension
        callbacks.setExtensionName("BHP Wordlist")
        callbacks.registerContextMenuFactory(self)

        return
    
    def createMenuItem(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Create Wordlist", actionPerformed=self.wordlist_menu))

        return menu_list

# this function is our menu-click handler
def wordlist_menu(self, event):

    # grab the details of what the user clicked
    http_traffic = self.context.getSelectedMessages()

    for traffic in http_traffic:
        http_service = traffic.getHttpService()
        host = http_service.getHost()
        # we save the host for later uses
        self.hosts.add(host)
        # method is used to retrieve the HTTP response associated with the current message
        http_response.getResponse()
        
        if http_response:   
            # we feed our get_words function with the content of the response
            self.get_words(http_response)
    
        self.display_wordlist()
        return

    
def get_words(self, http_response):
    
    # split out the header from the message body
    headers, body = http_response.tostring().split('\r\n\r\n', 1)

    # skip non-text response
    if headers.lower().find("content-type: text") == -1:
        return

    # remove the HTML code from the rest of the page text
    tag_stripper = TagStripper()
    page_text = tag.stripper.strip(body)

    # we use a regular expression to find all words starting with an alphabetic
    # character followed by two or more "word" characters
    words = re.findall("[a-zA-Z\w{2,}", page_text}

    for word in words:      
        # filter out long strings
        if len(word) <= 12:
            self.wordlist.add(word.lower())

    return



        
        
        



    
