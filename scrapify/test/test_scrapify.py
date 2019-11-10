import unittest
from .. import Scraper
from bs4 import BeautifulSoup

class ScrapifyTest(unittest.TestCase):
    
    def setUp(self):
        self.scraper = Scraper()
        self.soup = self.scraper.get_soup('https://www.baralaboratory.com/')
        
    def test_get_text_should_be_string(self):
        txt = self.scraper.get_text('http://topky.sk')
        self.assertIsInstance(txt, str)
        
    def test_get_soup_should_be_string(self):
        soup = self.scraper.get_soup('http://topky.sk')
        self.assertIsInstance(soup, BeautifulSoup)
        
    def test_get_clean_text_should_be_without_script_and_style_tags(self):
        soup = self.scraper.get_soup('http://topky.sk')
        text = self.scraper.get_clean_text(soup)
        self.assertNotIn('getElements', text)
        
    def test_get_clean_text_from_url_should_be_without_script_and_style_tags(self):
        text = self.scraper.get_clean_text_from_url('http://topky.sk')
        self.assertNotIn('getElements', text)

    def test_process_tag(self):
        tag = self.soup.a
        result_str = self.scraper.process_tag(tag, 'str')
        string_str = '<a href="http://www.baralaboratory.com/android"><img src="android.png" width="100"/></a>'
        result_text = self.scraper.process_tag(tag, 'text')
        result_href = self.scraper.process_tag(tag, 'href')
        string_href = 'http://www.baralaboratory.com/android'
        self.assertEqual(result_str, string_str)
        self.assertEqual(result_text, '')
        self.assertEqual(result_href, string_href)
        
    def test_get_data_from_tag(self):
        url = "https://www.zlatestranky.sk/firmy/Borsk%C3%BD+Mikul%C3%A1%C5%A1/H696682/MIESTNY+PODNIK+SLU%C5%BDIEB+-+BM+s.r.o./"
        soup = self.scraper.get_soup(url)
        tags = {"Phone":{"tag":['span',{"class":"tag-phone-main"}], 'format':'text'}}
        phone = self.scraper.get_data_from_soup(soup, tags)
        phone = phone['Phone']
        self.assertEqual(phone, '+421346595225')
        
    def test_get_data_from_soup_for_list_of_tags(self):
        url = 'https://www.bbb.org/us/ny/new-york/category/fashion-consultant'
        class_name = "MuiPaper-root MuiPaper-elevation1 MuiCard-root styles__ResultItem-sc-7wrkzl-0 fbHYdT MuiPaper-rounded"
        soup = self.scraper.get_soup(url)
        data_list = self.scraper.get_data_from_soup_for_list_of_tags(soup, tags = {'Source':{'tag':['a'], 'format':'text'},'ListOfTags':['div',{'class':class_name}]})
        self.assertGreater(len(data_list), 1)
        self.assertIsInstance(data_list, list)
        data_dict = self.scraper.get_data_from_soup_for_list_of_tags(soup, tags = {'Source':{'tag':['a'], 'format':'text'}})
        self.assertIsInstance(data_dict, dict)
        
    def test_get_data_from_url_for_list_of_tags(self):
        url = 'https://www.bbb.org/us/ny/new-york/category/fashion-consultant'
        class_name = "MuiPaper-root MuiPaper-elevation1 MuiCard-root styles__ResultItem-sc-7wrkzl-0 fbHYdT MuiPaper-rounded"
        data_list = self.scraper.get_data_from_url_for_list_of_tags(url, tags = {'Source':{'tag':['a'], 'format':'text'},'ListOfTags':['div',{'class':class_name}]})
        self.assertGreater(len(data_list), 1)
        self.assertIsInstance(data_list, list)
        
    def test_get_emails_and_social_networks_from_url(self):
        url = "http://impacthub.sk/"
        data = self.scraper.get_emails_and_social_networks_from_url(url)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['Emails'], list)
        keys = ['facebook','youtube','instagram','twitter','linkedin','Emails']
        for key in keys:
            self.assertIn(key, data.keys())
