import win32com.client
import os
import fnmatch
import time
import random
import zlib 

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

doc_type = ".doc"
# Tumblr username and password
username = "myusername"
password = "mypassword"

public_key = ""

def wait_for_browser(browser):
    # Wait for the browser to finish loading a page
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return



