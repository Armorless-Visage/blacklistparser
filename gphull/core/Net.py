#!/usr/bin/env python3

# Liam Nolan 2018 (c) ISC
# Full licence terms located in LICENCE file

 
from urllib.request import ProxyHandler, build_opener
from urllib.error import URLError
from gphull.core import Exceptions

def get_webpage(url, proxy=False, fake_user_agent=True, last_modified=None):
    '''
    - open a webpage and return the result using urllib2
    - use proxy=True to let urllib2 detect system proxy
    - fake_user_agent is on by default because some blacklists reject
      urllib user agents (spoofs a windows/ff ua)
    - last_modified should be exact string returned in server header
      for Last-Modified header
    '''
    # if proxy is set establish proxy handler
    # NOTE: python3 docs say urllib looks for proxy anyway
    # so this may still proxy even if proxy is set to False
    if proxy:
        proxy = ProxyHandler()
        opener = build_opener(proxy)
    else:
        opener = build_opener()
    
    # spoof the user agent
    # TODO: add more user agents
    agent = "Mozilla/5.0 (Windows NT 6.2; rv:10.0) Gecko/20100101 Firefox/33.0)"
    headers = []
    if fake_user_agent:
        headers.append(('User-Agent', agent))
    if last_modified:
        headers.append(('If-Modified-Since', last_modified)) # VALIDATE

    opener.addheaders = headers
    
    # try and get the webpage
    page = opener.open(url)

    # check the page is something
    if not page:
        raise Exceptions.NetError('Unknown problem opening webpage')
    # return the result
    return page

