'''
date: January 2019
purpose: classes to help with scraping tasks
version: 1.1.5
'''
from bs4 import BeautifulSoup
import random
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor
import os
import re
import time
#from queue import Queue

from .user_agents import user_agents_list

class Scraper:
    '''
    Class which use requests library to scrap data
    '''
    def __init__(self, driver = False, timeout = 4, verify = False):
        self.data = []
        self.urls = []
        self.soup_objects = []
        self.verify = verify
        self.timeout = timeout
        # self.driver = webdriver.Chrome()
        self.driver = False
        if driver:
            self.driver = driver

    def __get(self, url, proxies = {}):
        '''
        return get request

        args:
            url: <string>, example: 'https://github.com/Norbaeocystin'
            proxies: <dict>, example: proxies: {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080'}
        '''
        self.HEADER = {'User-Agent': random.choice(user_agents_list)}
        if not self.driver:
            if proxies:
                r = requests.get(url, proxies = proxies, headers = self.HEADER, timeout = self.timeout, verify = self.verify)
                return r
            else:
                r = requests.get(url, headers = self.HEADER, timeout = self.timeout, verify = self.verify)
                return r
        else:
            return driver.get(url).page_source

    def __soupify(self, text):
        '''
        return BeautifulSoup object

        args:
            text: <string>, html_content
        '''
        return BeautifulSoup(text, 'lxml')

    def get_text(self, url, proxies = {}):
        '''
        return text content of GET request as string ( html_content)

        args:
            url: <string>, example: 'https://github.com/Norbaeocystin'
            proxies: <dict>, example: proxies: {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080'}
        '''
        if self.driver:
            return self.driver.page_source
        else:
            return self.__get(url, proxies = proxies).text

    def get_soup(self, url, proxies = {}):
        '''
        return BeautifulSoup object from html content of GET request

        args:
            url: <string>, example: 'https://github.com/Norbaeocystin'
            proxies: <dict>, example: proxies: {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080'}
        '''
        if self.driver:
            text = self.driver.page_source
        else:
            text = self.__get(url, proxies = proxies).text
        #it creates attribute soup with BeautifulSoup object stored in the variable
        self.soup = self.__soupify(text)
        return self.soup

    def get_clean_text(self, soup):
        '''
        return text from html content of GET request

        args:
            soup: <BeautifulSoup object>
        '''
        for script in soup.findAll('script'):
            script.decompose()
        for style in soup.findAll('style'):
            style.decompose()
        return soup.text

    def get_from_tag(self, tag_soup_object, dict_identificators):
        '''
        Example of usage
        tags = {'Name':['h2',{'itemprop':'name'}], 'Street':['span',{'itemprop':'streetAddress'}],
                'City':['span',{'itemprop':'addressLocality'}],
                'Country':['span',{'itemprop':'addressCountry'}]}
        self.get_from_tag(soup, tags)
        >>>{'Name': '4leveldesign.com','Street': 'Branickiego 9L/25',City': '02-972, Warszawa','Country': 'Polen'}


        args::
            tag_soup_object:
            dict_identificators:
        '''
        data = {}
        for item in dict_identificators.keys():
            try:
                data[item] = tag_soup_object.find(*tags[item]).text
            except AttributeError:
                pass
        return data

    def get_data(self, soup_object):
        '''
        returns dict of values from BeautifulSoup object
        need to write your own method to scrap data
        args:
            soup_object: <bs4.BeautifulSoup>
        '''
        return {}

    def get_data_for_urls(self, urls, proxies):
        '''
        returns list of dictionaries of scraped values

        args:
            urls: <list>, example: ['https://github.com/Norbaeocystin']
            proxies: <dict>, example: proxies: {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080'}
        '''
        self.urls = urls
        self.data =  [self.get_data(self.get_soup(item, proxies)) for item in self.urls]
        return self.data

    def map_urls(self, urls, function):
        '''
	also possibility to improve it to higher level with asyncio and aiohttp
        apply function over list of urls

        args:
            urls: <list>, example: ['https://github.com/Norbaeocystin']
            function: <function>, example: self.get_data
        Example:
        from requests.exceptions import ConnectionError, ContentDecodingError, ReadTimeout, InvalidURL, TooManyRedirects
        from pymongo import MongoClient

        CON = MongoClient('localhost')
        collection = CON['DB']['Collection']

        es = EmailScraper()
        data = collection.find({'Website':{'$regex':'www'}},{'Website'})
	data = list(data)
        data = data[2200:]
        def get_data(item):
            try:
                web = 'http://' + item['Website'].replace(' ', '')
                emails = es.get_emails(web)
                if emails:
                    collection.update_one({"_id":item['_id']},{"$set":{'Emails':emails}})
            except (ConnectionError, ContentDecodingError, ReadTimeout, InvalidURL,IndexError, TooManyRedirects):
                pass
            ind = data.index(item)
            if ind % 100 == 0:
                print(ind)

        es.map_urls(data, get_data)
        '''
        cpus = os.cpu_count()
        threads = cpus * 4
        #q = Queue()
        #q.extend(items)
        with ThreadPoolExecutor(max_workers = threads) as executor:
            executor.map(function, urls)
            #for item in executor.map(function, urls):
             #   data.update(item)

    def __soupify(self, text):
        '''
        return BeautifulSoup object

        args:
            text: <string>, html_content
        '''
        return BeautifulSoup(text, 'lxml')

    def get_text(self, url, proxies = {}):
        '''
        return text content of GET request as string ( html_content)

        args:
            url: <string>, example: 'https://github.com/Norbaeocystin'
            proxies: <dict>, example: proxies: {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080'}
        '''
        return self.__get(url, proxies = proxies).text

    def get_soup(self, url, proxies = {}):
        '''
        return BeautifulSoup object from html content of GET request

        args:
            url: <string>, example: 'https://github.com/Norbaeocystin'
            proxies: <dict>, example: proxies: {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080'}
        '''
        text = self.__get(url, proxies = proxies).text
        #it creates attribute soup with BeautifulSoup object stored in the variable
        self.soup = self.__soupify(text)
        return self.soup

    def get_from_tag(self, tag_soup_object, dict_identificators):
        '''
        Example of usage
        tags = {'Name':['h2',{'itemprop':'name'}], 'Street':['span',{'itemprop':'streetAddress'}],
                'City':['span',{'itemprop':'addressLocality'}],
                'Country':['span',{'itemprop':'addressCountry'}]}
        self.get_from_tag(soup, tags)
        >>>{'Name': '4leveldesign.com','Street': 'Branickiego 9L/25',City': '02-972, Warszawa','Country': 'Polen'}


        args::
            tag_soup_object:
            dict_identificators:
        '''
        data = {}
        for item in dict_identificators.keys():
            try:
                data[item] = tag_soup_object.find(*tags[item]).text
            except AttributeError:
                pass
        return data

    def get_data(self, soup_object):
        '''
        returns dict of values from BeautifulSoup object
        need to write your own method to scrap data
        args:
            soup_object: <bs4.BeautifulSoup>
        '''
        return {}

class Wayback:
    '''
    Scraps archived version from web.archive.org
    Example of usage:

    scraper = Wayback()
    scraper.open_chrome()
    archived = []
    for item in list_of_urls:
        try:
            archive = scraper.scan(item)
            length = 0
            if archive:
                length = len(archive))
                archived.append(archive)
        except TimeoutException:
            print('Error')
    scraper.close_chrome()
    '''
    def __init__(self):
        self.url = 'https://web.archive.org/web/{}*/{}'

    def open_chrome(self):
        '''
        opens chrome driver
        '''
        self.driver = webdriver.Chrome()

    def open_url(self,year = 2018, url = 'https://web.archive.org/web/{}*/{}'):
        '''
        opens website on web.archive.org

        args:
            year: <int>: example 2018
            url: <string>: 'https://www.oglaf.com/'
        '''
        self.driver.get(self.url.format(year, url))

    def get_text(self):
        '''
        returns website html content as string
        '''
        return self.driver.page_source

    def close_chrome(self):
        '''
        close chrome driver
        '''
        self.driver.close()

    def get_urls(self, year, url):
        '''
        returns found captures on webarchive
        '''
        soup = BeautifulSoup(self.driver.page_source)
        pattern = re.compile('web/' + str(year) +  '\d{1,}/' + url)
        links = soup.findAll('a',{"href":pattern})
        if links:
            return ['https://web.archive.org' + item['href'] for item in links]
        else:
            []

    def scan(self, url = 'https://www.oglaf.com/', since = 2005, until = 2019):
        '''
        returns archive webs for url from since to until, it goes from until to since, if there are no points to 2014, it stops

        args:
            url: <string>, example 'https://www.oglaf.com/'
            since: <int>, example 2005, it needs to be lower than since
            until: <int>, example 2018, it needs to be higher than until
        '''
        links = []
        for i in range(until,since, -1):
            self.open_url(year = i, url = url)
            time.sleep(3)
            urls = self.get_urls(i, url)
            if urls:
                links.extend(urls)
        return links


PATTERN = r"\"?([-a-zA-Z0-9.`?{}]+@[-a-zA-Z0-9.`?{}]+[\.\w+]+)\"?"
EMAILFINDER = re.compile(PATTERN)
FILTER  = ['png', 'jpg', 'jpeg', '@gif', '@lg.x', '@md.x', '@sm.x', 'fontSize', '\d[.]\d', 'your@', 'mozilla',
	   'javascript','\dpx', 'textAligncenter', 'marginTop', 'name@', 'wixpress.com','@yourname',
	   'xs-only.x', 'com.avon.gi.rep.core.resman.vprov.ObjProvApplicationResource']
#regex to find some crap in from abc@abc
to_be_corrected =  '/@[A-Za-z]+$/'


class EmailScraper(Scraper):
    '''
    this will try to scrap emails, of course there is some balast and it needs to be improved:
    remove .png, .gif
    replace NOSPM and so on
    '''
    def get_emails(self, url):
        soup = self.get_soup(url)
        a = soup.findAll('a')
        a = [item for item in a if item.get('href')]
        emails = re.findall(EMAILFINDER, str(soup))
        contact = self.find_contact_webpage(soup)
        if contact:
            u = contact[0]
            if not 'http' in u and u[0] == '/':
                u = url + u
            if not 'http' in u and u[0] != '/':
                u = url + '/' + u
            soup = self.get_soup(u)
            a = soup.findAll('a')
            a = [item for item in a if item.get('href')]
            emails2 = re.findall(EMAILFINDER, str(soup))
            emails.extend(emails2)
        [item.replace('mailto:','') for item in emails]
        if emails:
            emails = [item for item in emails if '.' in item]
        if emails:
            emails = [item for item in emails if not re.search('|'.join(FILTER), item, re.IGNORECASE)]
        if emails:
            emails = [item for item in emails if not '}' in item]
        if emails:
            emails = [item for item in emails if not '{' in item]
        if emails:
            emails = [item for item in emails if not 'example' in item]
        if emails:
            emails = [item.replace('NOSPM','') for item in emails]
        return list(set([email.split('?',1)[0] for email in emails]))

    def find_contact_webpage(self, soup):
        '''
        in soup object try to find hyperlink for contact
	for most languages it will be something like
	kontakt, contact and so on
        '''
        links = soup.findAll('a', {"href":re.compile('[a-zA-Z]')})
        return list({item['href'] for item in links if 'onta' in item.text.lower()})
