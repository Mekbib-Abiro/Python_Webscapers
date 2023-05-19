''' A simple program that crawl an entire site.'''

import requests
from bs4 import BeautifulSoup

from tld import get_tld
from tld import get_fld

import time

from collections import Counter

from urllib import robotparser

# Normalize a link.
def get_normalized_url(link):
    
    link_tld = get_tld(link, as_object= True)
    path_list = [char for char in link_tld.parsed_url.path]
    
    # If there is no path in the link, the scheme and the netloc of the link will be enough.
    if len(path_list) == 0:
        final_url = link_tld.parsed_url.scheme + '://' + link_tld.parsed_url.netloc
    
    # If the path ends with / remove it.
    elif path_list[-1] == '/':
        link_string = ''.join(path_list[-1])
        final_url = link_tld.parsed_url.scheme  + '://' +  link_tld.parsed_url.netloc + link_string
    
    # Else the link is already normalized.
    else:
        final_url = link

    return final_url

# Parse the robot.txt file and fetch the crawl_delay parameter.
def get_robot_url(url):
    link_tld = get_tld(url, as_object= True)
    final_url = link_tld.parsed_url.scheme + '://' + link_tld.parsed_url.netloc + '/robots.txt'
    
    return final_url

def get_rb_object(url):
    robot_url = get_robot_url(url)
    
    parsed_robot = robotparser.RobotFileParser()
    parsed_robot.set_url(robot_url)
    parsed_robot.read()
    
    return parsed_robot

def parse_robot(url, rb_object):
    flag = rb_object.can_fetch('*', url)
    try:
        crawl_delay = rb_object.crawl_delay('*')
    except Exception as E:
        crawl_delay = None
    
    return flag, crawl_delay

def site_crawler(seed_url, max_links = 5000):
    
    my_headers = {'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    
    initial_url_set = set()
    initial_url_list = []
    seen_url_set = set()
    base_url = 'http://www.' + get_fld(seed_url)#(returns the name of the website)
    
    link_tld = get_tld(seed_url, as_object= True)
    domain_name = link_tld.fld
    
    initial_url_set.add(seed_url)
    initial_url_list.append(seed_url)
    
    # get the flag and the delay_time and return if crawling is not permitted.
    robot_object = get_rb_object(seed_url)
    flag, delay_time = parse_robot(seed_url, robot_object)
    
    if delay_time == None:
        delay_time = 0.1
    
    if flag is False:
        print('Crawlinkg not permitted.')
        return(initial_url_set, seen_url_set)
    
    
    while len(initial_url_set) != 0 and len(seen_url_set) < max_links:
        temp_url = initial_url_set.pop()
        # Check if the link is seen before proceeding.
        if temp_url in seen_url_set:
            continue
        else:
            seen_url_set.add(temp_url)
            
            time.sleep(delay_time)
            
            # Fetch all the links on the page.
            res = requests.get(url= temp_url, headers= my_headers)
            st_code = res.status_code
            
            if st_code != 200:
                time.sleep(delay_time)
                res = requests.get(url= temp_url, headers= my_headers)
                if res.status_code != 200:
                    continue
            
            html_res = res.text
            soup = BeautifulSoup(html_res, 'html.parser')
            links = soup.find_all('a', href= True)
            
            # Make sure all the links are absolute link and add them to the initial_set_url.
            for link in links:
                if 'http' in link['href']:
                    if domain_name in link['href']: # Absolute_links
                        final_url = link['href']
                    else: 
                        continue
                elif [char for char in link['href']][0] == '/': # Relative links
                    final_url  = seed_url + link['href']
                
                # Insert URL Normalizatin.
                final_url = get_normalized_url(final_url)
                # Check the robot file flag
                flag, delay = parse_robot(seed_url, robot_object)
                if flag is True:
                    
                    initial_url_set.add(final_url.strip())
                    initial_url_list.append(final_url.strip())
    
    
    counted_dict = Counter(initial_url_list)

    return (initial_url_set, counted_dict)

seed_url = 'Paste Your site here.'

print(site_crawler(seed_url= seed_url))
        