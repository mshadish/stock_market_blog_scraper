"""
Matt Shadish

This script defines several utility functions
used to scrape financial blog websites

1) attemptUrl
    - will attempt opening a URL a specified number of times
    
2) soupify
    - reads in a page and returns a Beautiful Soup object
"""
# imports
from bs4 import BeautifulSoup
import time
import re
import urllib2
import random


def attemptUrl(url, in_attempts = 5, interval = 3):
    """
    This function will attempt to open a URL a specific number of times
    before exiting
    
    Returns the instance returned from urllib2.urlopen()
    """
    # Initialize variables
    attempts = in_attempts
    request = urllib2.Request(url)
    page = None

    # try to open the URL
    while attempts > 0:
        
        try:
            page = urllib2.urlopen(request)
            return page
        except urllib2.URLError, e:
            # catch the error, we may try again
            if hasattr(e, 'reason'):
                print e.reason
            
                # if the error is 'service unavailable', keep trying the url
                if str(e.reason).strip() == 'Service Unavailable':
                    print 'Trying ' + str(attempts-1) + ' more times'
                    print 'Waiting ' + str(interval) + ' sec, give or take'
                    # pause
                    wait = round(max(0, interval + random.gauss(0,0.5)), 2)
                    time.sleep(wait)
                
            elif hasattr(e, 'code'):
                print 'Error: ' + str(e.code)
                break
            
        attempts -= 1
    # end while loop
        
    # if we've made it out of the loop, we failed to open the page
    print 'Failed to open the url'
    return None
    
    
    
def soupify(page):
    """
    Takes in a page object
    Reads the page, returns a Beautiful Soup object
    with newlines subbed out
    """
    content = page.read()
    content = re.sub('\n', '', content)
    content = re.sub('\t', '', content)
    soup = BeautifulSoup(content, 'html5lib')
    
    return soup