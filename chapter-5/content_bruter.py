import urllib2
import threading
import Queue
import urllib

threads         = 20
target_url      = "http://127.0.0.1/index.php"
wordlist_file   = "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt"
resume          = None
user_agent      = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
extensions      = [".php",".bak",".orig",".inc"]

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
   
 
def dir_bruter(word_queue, extensions=None):
    
    while not word_queue.empty():
        # we grab the word from the queue
        attempt = word_queue.get()

        attempt_list = []
        
        # we check if the word has already an extension, 
        # if not we can test if it is a directory
        if "." not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)
        
        # if we set some extensions to set we add them after our word
        # and we put them in the attempt list
        if extensions:
            for extension in extensions:
                attempt_list.append("/%s%s" % (attempt, extension))

        # iterate over our list of attemps
        for brute in attempt_list:
            # we build the URL replacing special characters with their HEX value 
            url = "%s%s" % (target_url, urllib.quote(brute))

            try:
                headers = {}
                # we set the user agent
                headers["User-Agent"] = user_agent
                
                # we can create the request and call the urlopen function
                # to perform the request and get the response
                r = urllib2.Request(url, headers=headers)
                response = urllib2.urlopen(r)
        
                # if we do not receive an URLError it means that we found something
                # we wanna print that
                if len(response.read()):
                    print "[%d] => %s" % (response.code, url)

            except urllib2.URLError, e:
                print "[!!!] %d => %s" % (e.code, url)
                # if we received an error that is not a 404 we wanna 
                # output that, because there could be something interesting 
                if hasattr(e, 'code') and e.code != 404:
                    print "[!!!] %d => %s" % (e.code, url)
                    
                pass


word_queue = build_wordlist(wordlist_file)

# we need to start our threads and pass the the function dir_bruter
for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue,extensions))
    t.start()








