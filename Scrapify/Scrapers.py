from bs4 import BeautifulSoup
import random
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from .user_agents import user_agents_list

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
					   
	def __soupify(text):
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
