# Matt Shadish
# MSAN 692

# Scraping insidermonkey
# http://www.insidermonkey.com/blog/


from bs4 import BeautifulSoup
import time
import re
import urllib2
import random
import os
from kiplinger_scrape import attemptUrl
from kiplinger_scrape import soupify
import argparse

insidermonkey_url = 'http://www.insidermonkey.com/blog/'


def extractBlogLinks(url):
    """
    This function takes in a url
    of the form from insidermonkey.com/blog
    And extracts the blog links
    Also extracts the next page link
    
    Returns a tuple (blog_link_list, next_page_link)
    """
    page = attemptUrl(url)
    soup = soupify(page)
    
    # grab list of blog links
    content_list = soup.find_all('div', {'class': 'post'})
    
    blog_link_list = [x.findChild('h2').findChild('a').get('href')
                        for x in content_list]
                            
    # also grab the link to the next page
    try:
        next_tag = soup.find_all('div', {'class': 'navigation'})[0]
    except:
        print 'could not find next link'
        return (blog_link_list, None)
        
    # grab the link
    next_page_link = next_tag.findChild('a').get('href')
    
    return (blog_link_list, next_page_link)
    
    
def extractArticleContents(page_url):
    """
    This function takes the url of a article
    and extracts the title, date, and content
    
    Returns in the form of a tuple
    (title, date, content)
    """
    page = attemptUrl(page_url)
    soup = soupify(page)
    # First, we need to check if there is a "see all" option for the post
    if soup.find_all('div', {'class': 'see-all'}):
        
        # we found a 'see-all' tag, so grab the link
        see_all_tag = soup.find_all('div', {'class': 'see-all'})[0]
        see_all_link = see_all_tag.findChild('a').get('href')
        
        # and we will extract the full contents from that pages
        return extractArticleContents(see_all_link)
        
    else:
        
        # grab the text
        try:
            # find where the text is in the doc
            content_obj = soup.find_all('div',
                                {'class': 'blog-content-container clearfix'})[0]
            content_child = content_obj.findChild('div', {'class': 'post'})
            content_gchild = content_child.findChild('div', {'class': re.compile(r'content\-with.*-wrap')})
            # grab the text
            content_text = content_gchild.get_text()
        except:
            print 'could not extract text: ' + page_url
            content_text = None
        
        # grab the title
        try:
            title_obj = soup.find_all('div', {'class': 'single-post-title'})[0]
            title = title_obj.findChild('h1').get_text()
        except:
            print 'could not extract title: ' + page_url
            title = None
            
        # grab the date
        try:
            date_obj = soup.find_all('h6', {'class': 'date-line'})[0]
            date = date_obj.get_text()
            # strip out 'published' and timestamp
            date = re.sub(r'Published\:\s?', '', date)
            date = re.sub(r'\sat.*', '', date)
            date = re.sub(r'\W', '_', date)
        except IndexError:
            print 'could not extract the date: ' + page_url
            date = None
            
        
        return (title, date, content_text)
        
        
def saveArticle(tuple_obj):
    """
    Takes in a tuple with the following fields
    (title, date, content_text)
    And saves a file in the subdirectory 'insidermonkey_scrape_files'
    date_title.txt
    
    If no title is given, we will use the first 50 chars of the article
    If no date is given, we can still use this in our training set
    """
    title = tuple_obj[0]
    date = tuple_obj[1]
    
    # make sure we have a date or a title
    if date is None:
        if title is None:
            # title and date are None
            try:
                file_name = re.sub(r'\s+', '_', tuple_obj[2][:50])
                file_name = re.sub(r'\W', '', file_name)
            except:
                print 'Nothing to save'
                return None
        else:
            # title is not None, date is None
            file_name = re.sub(r'\s+', '_', title)
            file_name = re.sub(r'\W', '', file_name)
    else:
        if title is None:
            # title is None, date is not None
            file_name = date + str(tuple_obj[2][:50])
            file_name = re.sub(r'\s+', '_', file_name)
            file_name = re.sub(r'\W', '', file_name)
        else:
            # title is not None, date is not None
            file_name = date + '_' + title
            file_name = re.sub(r'\s+', '_', file_name)
            file_name = re.sub(r'\W', '', file_name)
            
    if not os.path.exists('insidermonkey_scrape_files'):
        os.makedirs('insidermonkey_scrape_files')
        
    # open the file to write to
    outfile = open('insidermonkey_scrape_files/' + file_name + '.txt', 'w')
    try:
        outfile.write(tuple_obj[2].encode('utf8'))
        print 'saved: ' + file_name + '.txt'
    except:
        print 'could not write the file: ' + file_name + '.txt'
    outfile.close()
    
    return None


def main(url = insidermonkey_url):
    # grab the links from the first page
    (blog_links, next_link) = extractBlogLinks(url)
    
    count_pages = 1
    
    while next_link is not None:
        # continue to dig through articles until we cannot find a 'next' link
    
        # loop through blog links
        for blog in blog_links:
            # extract the title, date, and contents
            # but first, pause
            time.sleep(round(max(0, random.gauss(0, 0.5)), 2))
            article_tuple = extractArticleContents(blog)
            
            # save
            saveArticle(article_tuple)
            
        print 'completed page ' + str(count_pages)
        count_pages += 1
        
        (blog_links, next_link) = extractBlogLinks(next_link)
        
    return None
    
    
def parseArgument():
    """                                                                         
    Code for parsing arguments                                                  
    """
    parser = argparse.ArgumentParser(description='Parsing a file.')
    parser.add_argument('-u', nargs=1, required=False)
    args = vars(parser.parse_args())
    return args

if __name__ == '__main__':
    args = parseArgument()
    try:
        arg1 = args['u'][0]
        main(arg1)
    except TypeError:
        main()