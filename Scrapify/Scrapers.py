'''
date: January 2019
purpose: classes to help with scraping tasks
version: 1.0.0
'''
from bs4 import BeautifulSoup
import random
import re
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin

from user_agents import user_agents_list

#this still can scrap also some .png, jpeg and so on, needs to be filtered
email_pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?" )

class Scraper:
    '''
    Class which use requests library to scrap data
    '''
    def __init__(self):
        self.data = []
        self.urls = []
        self.soup_objects = []
    
    def __get(self, url, proxies = {}):
        '''
        return get request
        
        args:
            url: <string>, example: 'https://github.com/Norbaeocystin'
            proxies: <dict>, example: proxies: {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080'}
        '''
        self.HEADER = {'User-Agent': random.choice(user_agents_list)}
        if proxies:
            r = requests.get(url, proxies = proxies, headers = self.HEADER)
            return r
        else:
            r = requests.get(url, headers = self.HEADER)
            return r
                       
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
    
    def get_emails(self, url):
	'''
	scrap emails from url and from contact website
	'''
        soup = self.get_soup(url)
        #emails = list(set(re.findall(email_pattern, str(soup))))
        emails = list(set(re.findall(email_pattern, soup.text)))
        contact_emails = self.get_emails_from_contact(url, soup)
        if contact_emails:
            emails.extend(contact_emails)
        if emails:
            return list({item for item in emails if not item.rsplit('.',1)[1] in ['gif','jpg','png']})
        else: 
            None
    
    def get_contact(self, soup):
	'''
	will try to find contact website, in most languages is contact, kontakt or kontakta or similar 
	that is reason why is it filtering by list comprehension, btw this can be done in beautiful soup
	by 
	contact = re.compile('onta')
	soup.find('a', {'href': contact})
	'''
        links = soup.findAll('a')
        return list({item['href'] for item in links if 'onta' in item.text.lower() and not 'mailto:' in item['href']})
    
    def get_emails_from_contact(self, url, soup):
		'''
		will try to scrap emails from contact website, if there are not emails return none
		'''
        contact_url = self.get_contact(soup)
        if contact_url:
            html = self.get_soup(urljoin(url, contact_url[0]))
            #res =  list(set(re.findall(email_pattern, str(html))))
            res =  list(set(re.findall(email_pattern, html.text)))
            return res
        else:
            return None
                   
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
        self.driver.get(self.url.format(year, web))
        
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
        
    def get_urls(self):
        '''
        returns found captures on webarchive
        '''
        captures = self.driver.find_elements_by_class_name('captures')
        if captures:
            return [item.find_element_by_tag_name('a').get_attribute('href') for item in captures]
        else:
            return []
    
    def scan(self, url = 'https://www.oglaf.com/', since = 2005, until = 2018):
        '''
        returns archive webs for url from since to until, it goes from until to since, if there are no points to 2014, it stops
        
        args:
            url: <string>, example 'https://www.oglaf.com/'
            since: <int>, example 2005, it needs to be lower than since
            until: <int>, example 2018, it needs to be higher than until
        '''
        links = []
        for i in range(until,since, -1):
            self.open_url(year = i, web = web)
            time.sleep(3)
            urls = self.get_urls()
            if urls:
                links.extend(urls)
            if i == 2014 and not links:
                break
        return links

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
        
    def get_urls(self):
        '''
        returns found captures on webarchive
        '''
        captures = self.driver.find_elements_by_class_name('captures')
        if captures:
            return [item.find_element_by_tag_name('a').get_attribute('href') for item in captures]
        else:
            return []
    
    def scan(self, url = 'https://www.oglaf.com/', since = 2005, until = 2018):
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
            urls = self.get_urls()
            if urls:
                links.extend(urls)
            if i == 2014 and not links:
                break
        return links
