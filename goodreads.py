import requests
from lxml import etree
import goodreads

url = "https://www.goodreads.com/book/isbn/0441172717?key=uIcQQiAbnQPgbupzd4YpNQ"
url2 = "https://www.goodreads.com/book/isbn/0441172717?format=JSON" #JSON


r = requests.get(url)



print(r.find('book'))
