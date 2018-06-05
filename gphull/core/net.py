#!/usr/bin/env python3

# (c) Liam Nolan 2016
# BSD 2-Clause
# Full licence terms located in LICENCE file

 
from urllib.request import ProxyHandler, build_opener
from urllib.error import URLError
from gphull.core import Exceptions

def get_webpage(url, proxy=False, fake_user_agent=True):
    '''
    - open a webpage and return the result using urllib2
    - use proxy=True to let urllib2 detect system proxy
    - fake_user_agent is on by default because some blacklists reject
      urllib user agents (spoofs a windows/ff ua)
    '''
    # if proxy is set establish proxy handler
    # NOTE: python3 docs say urllib looks for proxy anyway
    # so this may still proxy even if proxy is set to False
    if proxy is True:
        proxy = ProxyHandler()
        opener = build_opener(proxy)
    else:
        opener = build_opener()
    
    # spoof the user agent
    # TODO: add more user agents
    agent = "Mozilla/5.0 (Windows NT 5.1; rv:13.0) Gecko/20100101 Firefox/13.0.1)"
    if fake_user_agent is True:
        opener.addheaders = [('User-Agent', agent)]
    
    # try and get the webpage
    try:
        page = opener.open(url)
    except URLError:
        raise

    # check the page is something
    if page is None:
        raise Exceptions.NetError('Unknown problem opening webpage')
    # return the result
    return page

