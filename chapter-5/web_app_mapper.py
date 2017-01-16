import Queue
import threading
import os
import urllib2

threads = 10

# website to test
target = "http://www.TEST_SITE_TEST.com"
# the local directory into which we have extracted the web application that
# we want comapre with the remote application
directory = "/LOCAL_WEBAPP_PATH/
# extensions that we do not want to test
filters = [".jpg",".gif",".png",".css"]

os.chdir(directory)

# this Queue will store all the files that we will attempt to locate on the 
# remote server
web_paths = Queue.Queue()

# walk through all of the files of the local web application folder and get all
# the directories and all the file names
for r,d,f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        # if the remote path starts with . we strip the dot off
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        # split the extensions and check it aganist the filters
        # if it is not in the filtered extensions we put it on the Queue
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)
            
def test_remote():
    # keep going untill the Queue is empty
    while not web_paths.empty():
        path = web_paths.get()
        # this memorizes:
        # www.example.com/directory1/directory2/file.extension
        url = "%s%s" % (target, path)
        # create our Request Object
        request = urllib2.Request(url)
        try:
            # we pass our Request Object to the urlopen function call
            response = urllib2.urlopen(request)
            content = response.read()
            # if we do not receive an error we can print out the file we just located
            print "[%d] ==> %s" % (response.code, path)
            response.close()
        except:
            # debug:
            #print "Failed %s" % error.code

            # if the file is not present we will receive an error as response
            # we can skip this error and we can keep going with the tests
            pass

# we spawn #threads that call the test_remote function
for i in range(threads):
    print "Spawning thread: %d" % i
    t = threading.Thread(target=test_remote)
    t.start()


