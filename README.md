# Scrapify
Simple python classes to help with scraping
```
pip3 install git+https://github.com/Norbaeocystin/Scrapify.git
```

Usage:
```
from scrapify import Scraper

class MyScraper(Scraper):
  
  def get_data(self, url):
    soup = self.get_soup(url)
    return [item.text for item in soup.findAll('div')]
```
