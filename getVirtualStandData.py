import requests
import csv
from bs4 import BeautifulSoup
import sys
import re

if len(sys.argv) != 2:
    print (f"{sys.argv[0]} <URL>")
    exit(-1)

url = sys.argv[1]

csv = csv.DictWriter(sys.stdout, fieldnames=['Model', 'Year', 'Month', 'Fuel', 'Kms', 'Power', 'Price' ,'URL'])
csv.writeheader()

page = 1

while page > 0:
    response = requests.get(url, params={'page': page})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    ads = soup.find('main')
    details = ads.select('article')

    for detail in details:
        model = detail.find('h2', attrs={'data-testid': 'ad-title'}).text

        detailsBox = detail.select_one('div > div > ul')

        fuel, month, year, power, kms = ['','','','', '']
        for idx, string in enumerate(detailsBox.strings):
            match idx:
                case 0: fuel = string
                case 1: month = string
                case 2: year = int(string)
                case 3: 
                    d = re.match(r'(.*) km', string)
                    kms = d.group(1).replace('.', ',').replace(' ', '')
                case 4:
                    d = re.match(r'(.*) cv', string)
                    power = d.group(1)
                case _: raise ValueError('Unexpected value')

        price = detail.select_one('div > div > span')
        d = re.match(r'(.*) EUR', price.text)
        price = d.group(1).replace('.', ',').replace(' ', '')
        
        csv.writerow({
            'Model': model,
            'Year': year,
            'Month': month,
            'Fuel': fuel,
            'Kms': kms,
            'Power': power,
            'Price': price,
            'URL': detail.select_one('h2[data-testid="ad-title"] > a')['href']
        })
    
    no_next = soup.select_one('li[data-testid="pagination-step-forwards"]')['aria-disabled']
    if no_next == 'true': page = -1
    else: page = page + 1 
