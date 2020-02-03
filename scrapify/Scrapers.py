'''
date: January 2019
purpose: classes to help with scraping tasks
version: 1.1.9
'''
from bs4 import BeautifulSoup
import difflib
import random
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor
import os
import re
import time
import urllib3
urllib3.disable_warnings()
#from queue import Queue

from .user_agents import user_agents_list

#social networks
SOCIALNETWORKS = ['facebook', 'youtube', 'instagram', 'twitter', 'linkedin']
SOCIALNETWORKSFILTER = ['adform', '/p/']
#emails
PATTERN = r"\"?([-a-zA-Z0-9.`?{}]+@[-a-zA-Z0-9.`?{}]+[\.\w+]+)\"?"
EMAILFINDER = re.compile(PATTERN)
FILTER  = ['png', 'jpg', 'jpeg', '@gif', '@lg.x', '@md.x', '@sm.x', 'fontSize', '\d[.]\d', 'your@', 'mozilla',
           'javascript','\dpx', 'textAligncenter', 'marginTop', 'name@', 'wixpress.com','yourname', 'youraddress','example',
           'xs-only.x', 'com.avon.gi.rep.core.resman.vprov.ObjProvApplicationResource', 'template.', 'layout.', '.gif'
           ,'beeketing']
#regex to find some crap in from abc@abc
to_be_corrected =  '/@[A-Za-z]+$/'

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
        return text from html content of BeautifulSoup Object

        args:
            soup: <BeautifulSoup object>
        '''
        for script in soup.findAll('script'):
            script.decompose()
        for style in soup.findAll('style'):
            style.decompose()
        return soup.text
    
    def get_clean_text_from_url(self, url, proxies = {}):
        '''
        return text from html content of GET request

        args:
            url: <string>, example: 'https://github.com/Norbaeocystin'
        '''
        soup = self.get_soup(url, proxies = proxies)
        for script in soup.findAll('script'):
            script.decompose()
        for style in soup.findAll('style'):
            style.decompose()
        return soup.text
    
    def process_tag(self, tag, command = "str"):
        """
        command possible values: "str","text","href"
        """
        if command == "str":
            return str(tag)
        elif command == "href":
            return tag['href']
        elif command == "text":
            return tag.text
        return str(tag)

    def get_data_from_soup(self, soup_object, tags):
        '''
        Example of usage
        tags = {'Name':{'tag':['h2',{'itemprop':'name'}], 'format':str'}, 'Street':{'tag':['span',{'itemprop':'streetAddress'}], 'format':href'},
                'City':{'tag':['span',{'itemprop':'addressLocality'}], 'format':'text'}}
        self.get_from_tag(soup, tags)
        >>>{'Name': '4leveldesign.com','Street': 'Branickiego 9L/25',City': '02-972, Warszawa','Country': 'Polen'}


        args::
            tag_soup_object:
            dict_identificators:
        '''
        data = {}
        for key in tags.keys():
            value = tags[key]
            try:
                tag = soup_object.find(*value['tag'])
                data[key] = self.process_tag(tag, value['format'])
            except (AttributeError, KeyError):
                pass
        return data
    
    def get_data_from_soup_for_list_of_tags(self, soup_object, tags):
        '''
        Example of usage
        >>scraper = Scraper()
        >>>url = 'https://www.bbb.org/us/ny/new-york/category/fashion-consultant'
        >>>class_name = "MuiPaper-root MuiPaper-elevation1 MuiCard-root styles__ResultItem-sc-7wrkzl-0 fbHYdT MuiPaper-rounded"
        >>>soup = scraper.get_soup(url)
        >>>data = scraper.get_data_from_soup_for_list_of_tags(soup, tags = {'Source':{'tag':['a'], 'format':'text'},'ListOfTags':['div',{'class':class_name}]})
        >>>print(data)
        >>>[{'Source': 'Carolyn Gustafson, Inc.'}, {'Source': 'CB Atelier'}, {'Source': 'International fashion Stylists Association'}, {'Source': 'Gilt Groupe, Inc.'}, {'Source': 'Brink212 Showroom'}, {'Source': 'Keaton Row'}, {'Source': 'You Need to Succeed, Inc.'}, {'Source': 'Designers and Agents'}, {'Source': 'Milk Studios'}, {'Source': 'Gilt Groupe, Inc.'}, {'Source': 'You Need to Succeed, Inc.'}, {'Source': 'Capital Impressions'}, {'Source': 'Rage Enterprises'}, {'Source': 'Rage Enterprises'}, {'Source': 'Making of a Mogul, LLC'}]

        args::
            tag_soup_object:
            dict_identificators:
        '''
        listOfTags = tags.get('ListOfTags')
        if listOfTags:
            main_tags = soup_object.findAll(*listOfTags)
            tags.pop('ListOfTags')
            result = []
            for main_tag in main_tags:
                data = self.get_data_from_soup(main_tag, tags)
                result.append(data)
            return result
        else:
            return self.get_data_from_soup(soup_object, tags)
        
    def get_data_from_url_for_list_of_tags(self, url, tags, proxies = {}):
        '''
        Example of usage
        >>scraper = Scraper()
        >>>url = 'https://www.bbb.org/us/ny/new-york/category/fashion-consultant'
        >>>class_name = "MuiPaper-root MuiPaper-elevation1 MuiCard-root styles__ResultItem-sc-7wrkzl-0 fbHYdT MuiPaper-rounded"
        >>>data = scraper.get_data_from_url_for_list_of_tags(url, tags = {'Source':{'tag':['a'], 'format':'text'},'ListOfTags':['div',{'class':class_name}]})
        >>>print(data)
        >>>[{'Source': 'Carolyn Gustafson, Inc.'}, {'Source': 'CB Atelier'}, {'Source': 'International fashion Stylists Association'}, {'Source': 'Gilt Groupe, Inc.'}, {'Source': 'Brink212 Showroom'}, {'Source': 'Keaton Row'}, {'Source': 'You Need to Succeed, Inc.'}, {'Source': 'Designers and Agents'}, {'Source': 'Milk Studios'}, {'Source': 'Gilt Groupe, Inc.'}, {'Source': 'You Need to Succeed, Inc.'}, {'Source': 'Capital Impressions'}, {'Source': 'Rage Enterprises'}, {'Source': 'Rage Enterprises'}, {'Source': 'Making of a Mogul, LLC'}]

        args::
            url:
            tag:
            proxies
        '''
        soup = self.get_soup(url, proxies= proxies)
        listOfTags = tags.get('ListOfTags')
        if listOfTags:
            main_tags = soup.findAll(*listOfTags)
            tags.pop('ListOfTags')
            result = []
            for main_tag in main_tags:
                data = self.get_data_from_soup(main_tag, tags)
                result.append(data)
            return result
        else:
            return self.get_data_from_soup(soup, tags)

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
            except (Exception, BaseException) as error:
                error_name = error.__class__.__name__
                print(error_name)
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

    def get_links_from_soup(self, soup):
        
        a = soup.findAll('a')
        links = [item for item in a if item.get('href')]
        return list(set(links))
    
    def find_contact_webpage_from_soup(self, soup):
        '''
        in soup object try to find hyperlink for contact
        for most languages it will be something like
        kontakt, contact and so on
        '''
        links = soup.findAll('a', {"href":re.compile('[a-zA-Z]')})
        return list({item['href'] for item in links if 'onta' in item.text.lower()})
    
    def get_emails_from_soup(self, soup_object):
        '''
        returns list of found emails from soup 
        args:
            soup_object: <bs4.BeautifulSoup>
        returns:	
            list
        '''
        emails = re.findall(EMAILFINDER, str(soup_object))
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
            emails = [item[:-1] if item[-1] =='.' else item for item in emails]
        if emails:
            emails = [item.replace('NOSPM','') for item in emails]
        return list(set([email.split('?',1)[0] for email in emails]))
    
    def apply_filter(self, x, filter_list = SOCIALNETWORKSFILTER ):
        """
        returns False if item in filter_list is in x else True
        """
        for item in filter_list:
            if item in x:
                return False
        return True
    
    def get_social_networks_from_soup(self, soup):
        '''
        returns list of dictfound social links
        args:
            soup_object: <bs4.BeautifulSoup>
        returns:
            dict
        '''
        links = self.get_links_from_soup(soup)
        result = dict()
        links = [link['href'] for link in links]
        for social_network in SOCIALNETWORKS:
            sn_links = set([item for item in links if social_network in item.rsplit('www.',1)[-1].split('.',1)[0]])
            sn_links = list(filter(lambda x: self.apply_filter(x), sn_links))
            result[social_network] = sn_link
        return result
    
    def get_the_most_similar(self, url, links):
        '''
        sometimes you can get more than one social network link, this function
        will compute ratio of similarity between part of original url and choose 
        the most similar link, it is based than for example company https://www.interflora.co.uk/ (just interflora is used in 
        computing similarity score)
        will be the most similar instagram account https://www.instagram.com/interflorauk/ not https://www.instagram.com/admob
        '''
        name = url.replace('www.','').split('//')[-1].split('.')[0]
        result = []
        for idx, link in enumerate(links):
            clean_link = link.replace('www.','').split('//')[-1].replace('user','').replace('/','')
            res = difflib.SequenceMatcher(None, name, clean_link)
            result.append((res.ratio(), idx))
        return links[sorted(result)[-1][1]]
          
    def get_social_networks_from_url(self, url, proxies= {}):
        '''
        return dictionary with social networks links ( if they exists on main or contact page)
        returned Social Networks are defined in SOCIALNETWORKS list
        '''
        soup = self.get_soup(url, proxies = {})
        links = self.get_links_from_soup(soup)
        contact = self.find_contact_webpage_from_soup(soup)
        if contact:
            contact_url = contact[0]
            if not 'http' in contact_url and contact_url[0] == '/':
                contact_url = url + contact_url
            if not 'http' in contact_url and contact_url[0] != '/':
                contact_url = url + '/' + contact_url
            soup = self.get_soup(contact_url, proxies = {})
            links_2 = self.get_links_from_soup(soup)
            links.extend(links_2)
        result = dict()
        links = [link['href'] for link in links]
        for social_network in SOCIALNETWORKS:
            sn_links = set([item for item in links if social_network in item.rsplit('www.',1)[-1].split('.',1)[0]])
            sn_links = list(filter(lambda x: self.apply_filter(x), sn_links))
            if sn_links and len(sn_links) == 1:
                result[social_network] = sn_links[0]
            elif sn_links and len(sn_links) > 1:
                most_similar_link = self.get_the_most_similar(url, sn_links)
                result[social_network] = most_similar_link
        return result
    
    def get_emails_and_social_networks_from_url(self, url, proxies = {}):
        '''
        returns email_and_social_networks as dict
        '''
        soup = self.get_soup(url, proxies = {})
        links = self.get_links_from_soup(soup)
        contact = self.find_contact_webpage_from_soup(soup)
        emails = re.findall(EMAILFINDER, str(soup))
        if contact:
            contact_url = contact[0]
            if not 'http' in contact_url and contact_url[0] == '/':
                contact_url = url + contact_url
            if not 'http' in contact_url and contact_url[0] != '/':
                contact_url = url + '/' + contact_url
            soup = self.get_soup(contact_url, proxies = {})
            links_2 = self.get_links_from_soup(soup)
            links.extend(links_2)
            emails2 = re.findall(EMAILFINDER, str(soup))
            emails += emails2
        result = dict()
        links = [link['href'] for link in links]
        for social_network in SOCIALNETWORKS:
            sn_links = set([item for item in links if social_network in item.rsplit('www.',1)[-1].split('.',1)[0]])
            sn_links = list(filter(lambda x: self.apply_filter(x), sn_links))
            if sn_links and len(sn_links) == 1:
                result[social_network] = sn_links[0]
            elif sn_links and len(sn_links) > 1:
                most_similar_link = self.get_the_most_similar(url, sn_links)
                result[social_network] = most_similar_link
        emails = [item.replace('mailto:','') for item in emails]
        if emails:
            emails = [item for item in emails if '.' in item]
        if emails:
            emails = [item for item in emails if not re.search('|'.join(FILTER), item, re.IGNORECASE)]
        if emails:
            emails = [item for item in emails if not '}' in item]
        if emails:
            emails = [item for item in emails if not '{' in item]
        if emails:
            emails = [item[:-1] if item[-1] =='.' else item for item in emails]
        if emails:
            emails = [item.replace('NOSPM','') for item in emails]
        result['Emails'] = list(set([email.split('?',1)[0] for email in emails]))
        return result
    
    def get_emails_from_url(self, url, proxies = {}):
        soup = self.get_soup(url, proxies = {})
        emails = re.findall(EMAILFINDER, str(soup))
        contact = self.find_contact_webpage_from_soup(soup)
        if contact:
            u = contact[0]
            if not 'http' in u and u[0] == '/':
                u = url + u
            if not 'http' in u and u[0] != '/':
                u = url + '/' + u
            soup = self.get_soup(u, proxies = {})
            emails2 = re.findall(EMAILFINDER, str(soup))
            emails.extend(emails2)
        emails = [item.replace('mailto:','') for item in emails]
        if emails:
            emails = [item for item in emails if '.' in item]
        if emails:
            emails = [item for item in emails if not re.search('|'.join(FILTER), item, re.IGNORECASE)]
        if emails:
            emails = [item for item in emails if not '}' in item]
        if emails:
            emails = [item for item in emails if not '{' in item]
        if emails:
            emails = [item[:-1] if item[-1] =='.' else item for item in emails]
        if emails:
            emails = [item.replace('NOSPM','') for item in emails]
        return list(set([email.split('?',1)[0] for email in emails]))

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
