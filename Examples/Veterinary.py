import re
from scrapify import Scraper
import pandas as pd
from pymongo import MongoClient
BASE_URL = 'https://findavet.rcvs.org.uk/find-a-vet-practice/?filter-choice=&filter-keyword=&filter-searchtype=practice&treated7=true&p={}' #format with range 1, 464

mail = re.compile('mailto:')

class VeterinaryScraper(Scraper):
    
    def get_data(self, url):
        result = []
        soup = self.get_soup(url)
        main_tags = soup.findAll('div', {'class':'practice'})
        for item in main_tags:
            data = {}
            try:
                data['Email'] = item.find('a', {"href":mail})['href'].replace('mailto:','')
            except (TypeError, AttributeError):
                pass
            data['Name'] = item.find('h3', {"class":'item-title'}).text.replace('\n', '')
            try:
                data['Phone'] = item.find('span', {"class":'item-contact-tel'}).text.replace('\nphone2\n\n\n', '')
            except (TypeError, AttributeError):
                pass
            zipcode = item.nobr.text
            data['Zipcode'] = zipcode
            address = item.find('div', {'class':'item-address'}).text.replace(zipcode, '').replace('\r\n','').replace('  ', '')
            addressSplits = address.split(',')
            if len(addressSplits) == 3:
                data['Street'] = addressSplits[0]
                data['City'] = addressSplits[1]
                data['County'] = addressSplits[2]
            elif len(addressSplits) == 2:
                data['Street'] = addressSplits[0]
                data['City'] = addressSplits[1]
                print(address)
            result.append(data)
        return result
        
CON = MongoClient('localhost')
collection = CON['Scraping']['Veterinary3']
'''
scraper = VeterinaryScraper()
for item in range(1,465):
    data = scraper.get_data(BASE_URL.format(item))
    collection.insert_many(data)
    print('Done {}'.format(item))'''
data = collection.find({},{"_id":0})
df = pd.DataFrame(list(data))
df.to_csv('veterinary.csv', sep = ';')
