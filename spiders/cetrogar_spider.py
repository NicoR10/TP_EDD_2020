import scrapy
import re
from datetime import datetime
from spiders.items import Items
from nltk.corpus import stopwords
from nltk import word_tokenize


class CetrogarSpiderSpider(scrapy.Spider):
    name = 'cetrogar_spider'
    allowed_domains = ['www.cetrogar.com.ar']
    start_urls = ['https://www.cetrogar.com.ar/']
    
    def __init__(self, target='', **kwargs):
        super().__init__(**kwargs)  # python3
        self.target = target

    def parse(self, response):
        links = response.xpath('//div[@class="navigation-container"]/ul/li/a')
        for link in links:
            nombre = link.xpath(".//text()").get()
            link = link.xpath(".//@href").get()
            
            yield response.follow(url=link, callback=self.parse_productos)
            
    def parse_productos(self, response):
        
        categoria = response.xpath('//span[@class="base"]/text()').get()
        for product in response.xpath("//ol[@class='products list items product-items  defer-images-grid']/li"):
            title = product.xpath("normalize-space(.//a[@class='product-item-link']/text())").get()
            precio = product.xpath('.//span[@class="price-container price-final_price tax weee"]/span[@data-price-type="finalPrice"]/span[@class="price"]/text()').get()
            #title = titulo.strip().lower()
            
            #trabajo con los precios
            price = 0
            if precio:
                price = precio.replace('$','')
                price = price.replace('.', '')
                price = float(price)

            #fecha y hora de extraccion
            now = datetime.now()
            dt_format = now.strftime("%d/%m/%Y %H:%M:%S")
            
            #link del producto
            product_link = response.xpath(".//a[@class='product-item-link']/@href").get()

            entra_yield = False
            
            if self.tipo_busqueda == '1':
                entra_yield = title.lower() == self.target
                
            elif self.tipo_busqueda == '2':
                stop_words = frozenset(stopwords.words('spanish'))
                title_tokens = word_tokenize(title.lower())
                title_token = [w for w in title_tokens if not w in stop_words]
                entra_yield =  all(item in self.target for item in title_token)
            
            elif self.tipo_busqueda == '3':
                if re.findall(r"(?=("+'|'.join(self.target)+r"))",title.lower()):
                    entra_yield = True

            if entra_yield:
                item = Items()
                item['title'] = title
                item['categoria'] = categoria
                item['price'] = price
                item['link'] = product_link 
                item['fecha'] = dt_format
                item['market'] = 'cetrogar'

                yield item
        
        next_page = response.xpath('//a[@class="action  next"]/@href').get()
        
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_productos)