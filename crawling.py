'''
This script crawls an entire site for a specific keyword and prints links conatining that keyword.

The script requires a url as a command line argument to run. 
It also accepts the keyword to be searched using the -p flag. 
Default keyword is python.

usage -> py ./crawling.py http://www.example.com -p keyword

you will need to install the following libraries for this script
    - pip install selenium
    - pip install bs4
    - pip install chromedriver-autoinstaller
'''


import re
from urllib.parse import urljoin, urlparse
import logging
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from bs4 import BeautifulSoup
import argparse

logging.basicConfig(level=logging.INFO)
#Declare the default phrase
DEFAULT_PHRASE = 'python'

# Search for all elements on a page containing the text, 
# and print the link containing the element and the whole element.
def search_text(source_link, page, text):
    for element in page.find_all(string= re.compile(text, re.IGNORECASE))[1:]:
        print(f'Link {source_link}: --> {element.text}')


# Find all the links on a page and return them
def get_links(parsed_source, page):
    links = []
    for element in page.find_all('a', href=True):
        link = element['href']
        # If element has no href attribute continue
        if not link:
            continue
        
        # Avoid internal links
        if link.startswith('#'):
            continue
        
        # Only append links with the same domain
        if parsed_source.netloc not in link:
            continue
        
        # Make sure to append local links
        if not link.startswith('http'):
            netloc = parsed_source.netloc
            scheme = parsed_source.scheme
            path = urljoin(parsed_source.path, link)
            link = f'{scheme}://{netloc}{path}'
            
        links.append(link)
    return links

# Search the text in the page and in every link in that page
def process_link(source_link, text):
    print(f'Extracting links from {source_link}:')
    
    # parse the source link on to its 6 building components,
    # for local hosts and domain checking
    parsed_source = urlparse(source_link)
    
    # Download the page
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(source_link)
        html_content = driver.page_source
        driver.execute_script('adsbygoogle.push();')
    except JavascriptException as e:
        pass
    finally:
        if 'driver' in locals():
            driver.quit()
    
    # Parse the page
    page = BeautifulSoup(html_content, 'html.parser')
    
    # Search the text in that page
    search_text(source_link, page, text)
    
    # Return all the links on that page
    return get_links(parsed_source, page)


# Define the main function which will crawl through the website
def Main(base_url, to_search):
    checked_links = set()
    to_check = [base_url]
    max_checks = 10
    
    # Loop until max checks = 0 or all the links are checked(no more links in to to_check list)
    while to_check and max_checks:
        # Catch the most recent link in the to_check list and remove it from to check
        link = to_check.pop(0)
        
        # Search the text on that page and return all the links in that page
        links = process_link(link, text=to_search)
        
        # Add the link to checked_linsks
        checked_links.add(link)
        
        # Make sure the link is checked and if not add it to to_check,
        # and also added to checked_links to make sure it is not checked more than once
        for link in links:
            if link not in checked_links:
                checked_links.add(link)
                to_check.append(link)
        
        # Decrement the max_checks in each while loop
        max_checks -= 1
        
    
# Make sure the whole script can not be imported    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type= str, \
                        help= 'Site base url')
    parser.add_argument('-p', '--phrase', type= str, default= DEFAULT_PHRASE, \
                        help= 'Phrase to search for.')
    args = parser.parse_args()
    
    Main(args.url, args.phrase)
