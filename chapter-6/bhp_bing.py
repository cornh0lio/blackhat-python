from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import socket
import urllib
import json
import re
import base64
# added this to resolv the "Extensions should not make HTTP 
# requests in the swing event dispatch thread" error on Burp
import threading
# insert here the Bing API Key
bing_api_key="MYKEY"

# extending the IContextMenuFactory allow us to provide a context menu 
# when a user right-clicks a request in Burp 
class BurpExtender(IBurpExtender, IContextMenuFactory):
    
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        # we set up our extension
        callbacks.setExtensionName("BHP Bing")
        # we register our menu handler so that we can determine which site
        # the user clicked, which then enable us to construct our Bing queries
        callbacks.registerContextMenuFactory(self)
        return
    
    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        # we set our bing_menu function to handle the click event
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        return menu_list


    def bing_menu(self, event):
        
        # we retrieve all of the HTTP requests that were highlighted
        http_traffic = self.context.getSelectedMessages()
        print "%d requests highlighted" % len(http_traffic)
        
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            # and then we retrieve the host portion of the request for each one
            host = http_service.getHost()
            
            print "user selected host: %s" % host
            # we send the host portion to our bing_search function for further processing
            self.bing_search(host)

        return

    def bing_search(self, host):
        
        # check if we have an IP or hostname
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)
        
        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True

        # we query Bing for all virtual hosts that have the same IP address 
        bing_query_string = "'ip:%s'" % ip_address
        # MODIFIED - we need to start a new thread because the call can't be executed
        # on the Swing interface thread. This is forbiden to prevent the UI freezing
        thread = threading.Thread(target=self.bing_query, args=(bing_query_string,))
        thread.start()
    
        if domain: 
            # if a domain was passed, we perform a subdomain search on Bing
            bing_query_string = "'domain:%s'" % host
            # MODIFIED - we need to start a new thread because the call can't be executed
            # on the Swing interface thread. This is forbiden to prevent the UI freezing
            thread = threading.Thread(target=self.bing_query, args=(bing_query_string,))
            thread.start()

    
    def bing_query(self, bing_query_string):
        
        print "Performing Bing Search: %s" % bing_query_string

        # we encode our query
        quoted_query = urllib.quote(bing_query_string)

        # we need to build up the entire HTTP reuqest as a string before
        # sending it off
        http_request = "GET https://api.datamarket.azure.com/Bing/Search/Web?$format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        http_request += "Host: api.datamarket.azure.com\r\n"
        http_request += "Connection: close\r\n"
        http_request += "Authorization: Basic %s\r\n" % base64.b64encode(":%s" % bing_api_key)
        http_request += "User-Agent: Blackhat Python \r\n\r\n"
        # we send our HTTP request to the Microsoft servers
        json_body = self._callbacks.makeHttpRequest("api.datamarket.azure.com", 443, True, http_request).tostring()  
        # we strip out the headers from the response
        json_body = json_body.split("\r\n\r\n",1)[1]
        try:
            # we pass it to our json parser
            r = json.loads(json_body)
      
            # we check if there are results
            if len(r["d"]["results"]):
                # for each set of results, we output some information about the
                # site that we discovered
                for site in r["d"]["results"]:
                    print "*" * 100    
                    print site['Title']
                    print site['Url']
                    print site['Description']
                    print "*" * 100    

                    j_url = URL(site['Url'])
                # if the site discovered was not in Burp's target scope we add it automatically
                if not self._callbacks.isInScope(j_url):
                    print "Adding to Burp scope"
                    self._callbacks.includeInScope(j_url)
        except:
            print "No results from Bing"
            pass
        return


                     
    










