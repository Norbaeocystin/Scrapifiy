from scrapify import Scraper

class Europages(Scraper):
    
    def get_data(self, url):
        soup = self.get_soup(url)
        return soup
    
    def get_links(self, url = 'https://www.europages.co.uk/companies/cosmetics.html'):
        '''
        https://www.europages.co.uk/companies/pg-1/cosmetics.html
        '''
        modified_url = '/pg-{}/'.join(url.rsplit('/',1))
        data = []
        for _ in range(1000000):
            soup = self.get_soup(modified_url.format(_))
            if 'Page not found' in soup.text:
                break
            lis = soup.findAll('li',{'class':"list-article vcard"})
            result = []
            for item in lis:
                dictionary = {}
                link = item.find('a', {'class':"company-name display-spinner"})
                url_, name = link['href'], link.text
                dictionary['Url'] = url_
                dictionary['Origin'] = url
                dictionary['Name'] = name.text.replace('\r','').replace('\n','')
                description = soup.find('span', {'class':"description"}).text.replace('\r','').replace('\n','')
                dictionary['Description'] = description
                supplierOf = soup.find('span', {'class':"dfn"}).text
                dictionary['SupplierOf'] = supplierOf
                country = soup.find('span',{'class':"country-name"}).text
                locality = soup.find('span',{'class':"street-address postal-code locality"}).text
                dictionary['Country'] = country
                dictionary['Locality'] = locality
                result.append(dictionary)
            data = data + result
        return data
