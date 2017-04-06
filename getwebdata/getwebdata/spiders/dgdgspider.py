import scrapy
import pymongo
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from getwebdata.items import GetwebdataCar, GetwebdataCollinfo
from getwebdata.settings import my_mongo_uri, my_database
from getwebdata.mylib import get_pst_time_isostr
import re
import urlparse

CAR_BRANDS = ["ford","chevrolet","chevy","ram","toyota","honda","nissan","hyundai","jeep","gmc", \
 "subaru","kia","bmw","lexus","infiniti","volkswagen","vw","dodge","chrysler","audi","mercedes-benz","benz",\
"mazda","mini","buick","fiat","cadillac","jaguar","acura","volvo","scion","mercedes","mb"]
PRICE_MIN = 2000
PRICE_MAX = 30000
YEAR_MIN = 2000
MILEAGE_MIN = 5000
MILEAGE_MAX = 150000
PRICE_AND_MILEAGE_MIN = 30000

#crawl all pages(price among 0-30000) daily, update with unique VIN
#On each page,
#info availabe: year, brand, entry_title, mileage, price, vin, url, car_type(most can get from title)
#info not availabe: title_status(na), date(na), place/area(na)
#place/area not needed for dgdg since it's SF bayarea local
#parse per page, no need to parse per entry

class dgdgspider(CrawlSpider):
    #crawl method:
    #get info directly from entries on one page, no need to open each entry url. 
    #crawl all pages daily. update db with same unique VIN
    collection_name = 'dgdg'
    name = "dgdg"
    allowed_domains = ["dgdg.com"]
    start_urls = [ "http://www.dgdg.com/used-inventory/index.htm?listingConfigId=auto-used&accountId=&compositeType=&year=&make=&model=&trim=&bodyStyle=&driveLine=&internetPrice=1-9999&start=0&sort=&facetbrowse=true&searchLinkText=SEARCH&showFacetCounts=true&showRadius=false&showSubmit=true&showSelections=true",
"http://www.dgdg.com/used-inventory/index.htm?listingConfigId=auto-used&accountId=&compositeType=&year=&make=&model=&trim=&bodyStyle=&driveLine=&internetPrice=10000-19999&start=0&sort=&facetbrowse=true&searchLinkText=SEARCH&showFacetCounts=true&showRadius=false&showSubmit=true&showSelections=true",
"http://www.dgdg.com/used-inventory/index.htm?listingConfigId=auto-used&accountId=&compositeType=&year=&make=&model=&trim=&bodyStyle=&driveLine=&internetPrice=20000-29999&start=0&sort=&facetbrowse=true&searchLinkText=SEARCH&showFacetCounts=true&showRadius=false&showSubmit=true&showSelections=true",
    ]

    page_num = 0
    total_page_num = 0
    total_processed_link_num = 0
    valid_link_num = 0
    spider_stats = GetwebdataCollinfo()

    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//div[@class="mod"]/a',)), callback="parse_page", follow=True),)

    def __init__(self, debug='',coll='',spider_return_stats={},*args, **kwargs):
        self.debug = debug
        self.coll = self.collection_name
        self.spider_return_stats = self.spider_stats
        self.spider_stats['coll_name'] = self.collection_name
        self.spider_stats['last_update_time'] = ''
        self.spider_stats['total_processed_links'] = 0
        self.spider_stats['valid_links'] = 0
        self.spider_stats['total_processed_pages'] = 0
        super(dgdgspider, self).__init__(*args, **kwargs)

#    def closed(self, reason):
#        print "--Spider closing, processed page=%d total_processed_link_num=%d, valid_link_num=%d this run"%(self.page_num,self.total_processed_link_num,self.valid_link_num)

    def parse_start_url(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        self.page_num = self.page_num + 1
        self.spider_stats['total_processed_pages'] += 1
        if self.page_num == self.total_page_num:
            print "----This is the last page, stop following"
            self._follow_links = False

#        print "--Opening page%d URL = %s"%(self.page_num, response.url)
        titles = response.xpath("//a[@class='url']") 
        prices = response.xpath("//span[@class='internetPrice final-price']")
        descs = response.xpath("//div[@class='description']")
        entry_num = len(titles)
        items = []

        for i,_ in enumerate(titles):
            self.total_processed_link_num = self.total_processed_link_num + 1
            self.spider_stats['total_processed_links'] += 1
            ######################titles
            item = GetwebdataCar()

            #url
            url = urlparse.urljoin(response.url, titles[i].xpath("@href").extract()[0])
            entry_title = titles[i].xpath("text()").extract()[0]
            #year
            year = int(re.findall(r"\d{4}",entry_title)[0])
            if year == '' or year < YEAR_MIN:
                print "----Year not found or too old in %s, skip..."%entry_title
                continue
            #brand
            brand = ''
            brand_str = entry_title.lower().split()
            for b in CAR_BRANDS:
                if b in brand_str:
                    brand = b
                    break
            if brand == '':
                print "----Brand not found in %s, skip brand"%brand_str
            #type
            car_type = entry_title.lower().split()[-1]

            ######################prices
            #price
            price = int(prices[i].xpath("span[@class='value']/text()").extract()[0].replace("$","").replace(",",""))
            if price < PRICE_MIN or price > PRICE_MAX:
                print "----Price %s is not within valid range, skip... "%price
                continue

            ######################descs
            mileage = int(descs[i].xpath("dl[@class='last']/dd/text()").extract()[-1])
            if mileage == 0 or mileage < MILEAGE_MIN or mileage > MILEAGE_MAX:
                print "----Mileage %s not within range"%mileage
                continue

            vin = descs[i].xpath("dl[@class='vin']/dd/text()").extract()[0]

            price_add_mileage = (price)+ (mileage)
            if price_add_mileage < PRICE_AND_MILEAGE_MIN:
                #if mileage very low, price is also very low, skip
                continue

            item['entry_title'] = entry_title
            item['year'] = year
            item['brand'] = brand
            item['price'] = price
            item['mileage'] = mileage
            item['price_add_mileage'] = price_add_mileage
            item['vin'] = vin
            item['car_type'] = car_type
            #data date is for PST timezone
            item['date'] = get_pst_time_isostr()
            item['url'] = url
            item['title_status'] = 'NA'
            item['place'] = 'sfbay'
            items.append(item)
            self.valid_link_num = self.valid_link_num + 1
            self.spider_stats['valid_links'] += 1
#            print "----Found valid entry at link %s"%item['url']
        #end of for
        return items

