"""
Matt Shadish

This script scrapes Kiplinger's stock watch page
http://www.kiplinger.com/fronts/archive/column/index.html?column_id=8&si=1

Below are a few of the relevent functions defined in this script

1) extractLinks(url)
    - extracts links to individual articles
    - from a page (assumed to be the kiplinger url constant)

2) extractArticleText((date, url))
    - extracts the text from the links returned from the previous function
    
3) saveArticle
    - Saves articles found in the links
    extracted from the previous two functions
"""

import time
import re
import random
import os
from utils import attemptUrl
from utils import soupify

# let's define the kiplinger url as a constant
kip_url = 'http://www.kiplinger.com/fronts/archive/column/index.html?column_id=8&si=1'

    
def extractLinks(url):
    """
    This function takes in the kiplinger url
    and returns a list of tuples
    Each tuple has the (date, url) for a given article
    """
    page = attemptUrl(kip_url)
    
    # read the page, sub out newlines    
    soup = soupify(page)
    
    list_of_articles = soup.find_all('div',
                                     {'id': re.compile(r'recent\[\d*\]')})
                                     
    list_of_links = []
    url_prefix = 'http://www.kiplinger.com'
    
    for article in list_of_articles:
        
        # grab the link to the article as well as the date
        article_link = article.findChild('h3').findChild('a').get('href')
        article_link = url_prefix + article_link
        article_date = article.findChild('h4').get_text()
        
        # some of the dates have 'From Kiplinger's Personal Finance, '
        article_date = re.sub(r'From Kiplinger\'s Personal Finance, ',
                              '', article_date)
        
        # add to our list
        list_of_links.append((article_date, article_link))
        
        
    return list_of_links    
    
    
    
def saveArticle(date, page_text, url):
    """
    This function takes in a string that represents the date of an article
    as well as the article's text and the title we want to call the file
    Writes a file in the current working directory with the page text
    """
    # First check if directory exists, make directory if necessary
    if not os.path.exists('kip_scrape_files'):
        os.makedirs('kip_scrape_files')
    
    page_title = re.findall(
        r'(?<=\w\d{3}\-)(?!\w\d{3})[0-9a-zA-Z\-]+(?=\.html)',
        url)[0]
        
    in_date = re.sub(r'\W', '_', date)
        
    outfile = open('kip_scrape_files/' + in_date + '_' + page_title + '.txt',
                   'w')
    outfile.write(page_text.encode('utf8'))
    outfile.close()
    
    return
    
    
    
def extractArticleText(list_of_tuples):
    """
    Takes in a list of tuples returned by extractLinks
    Returns the text body of each article
    """
    
    # loop through list of tuples
    for (date, url) in list_of_tuples:
        
        # read the page
        try:
            page = attemptUrl(url)
        except:
            print 'unable to open: ' + url
            continue
        
        # if we succeeded in opening the url, then read the page
        soup = soupify(page)
        
        # search for the content body
        list_of_contents = soup.find_all('div',
                                         {'class':
                                         re.compile(r'kip\-column\-content')})
                                         
        # if we couldn't find anything, continue
        if not list_of_contents:
            print 'could not extract content'
            print 'url: ' + url
            continue
                                         
        page_text = ''
        
        # in case there are multiple pages for a given article
        for content_page in list_of_contents:
            
            # getting a strange error...with 'call-me-manny-the-arb'
            # will skip
            try:
                for paragraph in content_page.find_all('p'):
                    page_text = page_text + paragraph.get_text() + ' '
            except:
                print 'issue with ' + url
                continue
                
        
        print 'saving ' + url
        saveArticle(date, page_text, url)
        print 'save complete'
        print '\n'
        
        
        # wait before we start with the next link
        wait_time = round(max(0, random.gauss(0, 0.5)), 2)
        time.sleep(wait_time)
        
    return
    
        
        
if __name__ == '__main__':
    links = extractLinks(kip_url)
    extractArticleText(links)