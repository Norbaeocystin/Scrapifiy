from bs4 import BeautifulSoup
import random
import requests
from selenium import webdriver

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
		self.HEADER = {'User-Agent': random.choice(user_agents_list)
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
	
	def get_text(self, url, proxies = {})
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
