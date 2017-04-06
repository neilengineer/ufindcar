import scrapy
import pymongo
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from getwebdata.items import GetwebdataCar, GetwebdataCollinfo
from getwebdata.settings import my_mongo_uri, my_database
import re

CAR_BRANDS = ["ford","chevrolet","chevy","ram","toyota","honda","nissan","hyundai","jeep","gmc", \
 "subaru","kia","bmw","lexus","infiniti","volkswagen","vw","dodge","chrysler","audi","mercedes-benz","benz",\
"mazda","mini","buick","fiat","cadillac","jaguar","acura","volvo","scion","mercedes","mb"]
PRICE_MIN = 2000
PRICE_MAX = 20000
YEAR_MIN = '2000'
MILEAGE_MIN = 5000
MILEAGE_MAX = 150000
PRICE_AND_MILEAGE_MIN = 30000

#date: show most recent 2 days' result only
#price range 2000-15000
#mileage range 5000-150000
#year > 2000
#only owner
#entries without mileage or without price will be skipped

class craigspider(CrawlSpider):
    #crawl method:
    #get last save url entry, crawl all urls in one page, and follow next pages until same url found
    name = "craig"
    collection_name = 'craig'
    allowed_domains = ["craigslist.org"]
    start_urls = [
    "https://sfbay.craigslist.org/search/cto?postedToday=1&min_price=2000&max_price=20000&min_auto_year=2000&min_auto_miles=5000&max_auto_miles=150000",
    ]
    last_update_url = ''
    page_num = 0
    total_page_num = 0
    total_processed_link_num = 0
    valid_link_num = 0
    spider_stats = GetwebdataCollinfo()

    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@class="button next"]',)), callback="parse_page", follow=True),)

    def __init__(self, debug='',coll='',spider_return_stats={},*args, **kwargs):
        self.debug = debug
        self.coll = self.collection_name
        self.spider_return_stats = self.spider_stats
        self.spider_stats['coll_name'] = self.collection_name
        self.spider_stats['last_update_time'] = ''
        self.spider_stats['total_processed_links'] = 0
        self.spider_stats['valid_links'] = 0
        self.spider_stats['total_processed_pages'] = 0
        super(craigspider, self).__init__(*args, **kwargs)
        if self.debug != '1':
            self.client = pymongo.MongoClient(my_mongo_uri)
            self.db = self.client[my_database]
            cursor = self.db[self.collection_name].find({'coll_name':self.collection_name})
            if cursor != None:
                for document in cursor:
                    if 'last_update_url' in document.keys():
                        self.last_update_url = document['last_update_url']
                        print "----Got last update url = %s"%self.last_update_url
        else:
            print "----Dry run for debugging"

#    def closed(self, reason):
#        print "--Spider closing, processed page=%d total_processed_link_num=%d, valid_link_num=%d this run"%(self.page_num,self.total_processed_link_num,self.valid_link_num)

    def parse_start_url(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        self.page_num = self.page_num + 1
        self.spider_stats['total_processed_pages'] += 1
        if self.page_num == 1:
            self.total_page_num = 1 + int(response.xpath("//span[@class='totalcount']/text()").extract()[0])/100
        if self.page_num == self.total_page_num:
            print "----This is the last page, stop following"
            self._follow_links = False
#        print "--Opening page%d URL = %s"%(self.page_num, response.url)

        links = response.xpath("//p[@class='row']/span[@class='txt']/span[@class='pl']/a/@href").extract()
#        print "----Total number of URLs = %d on this page"%len(links)
        if self.debug != '1':
            if self.last_update_url == '':
                self.last_update_url = links[0]
                print "----Set the first threshold url %s"%self.last_update_url
        for i,href in enumerate(links):
            if self.debug != '1':
                #Always save the 1st link on the 1st page once
                if self.page_num == 1 and i == 0:
                    updateurl = GetwebdataCollinfo()
                    updateurl['coll_name'] = self.collection_name
                    updateurl['last_update_url'] = links[0]
                    self.db[self.collection_name].update(
                                            {'coll_name': self.collection_name},
                                            {'$set': dict(updateurl) },upsert=True,multi=True )
                    print "----Saving last_update_url to new URL %s"%(updateurl['last_update_url'])
                if href == self.last_update_url:
                    print "----Last update URL found on this page at link%d, stop following next pages"%i
                    self._follow_links = False
                    break
            url = response.urljoin(href)
#            print "************Sending http request to %s"%url
            yield scrapy.Request(url, callback=self.parse_link_detail)

    def parse_link_detail(self, response):
#        print "***********parse_link_detail() for  %s"%response.url
        self.total_processed_link_num = self.total_processed_link_num + 1
        self.spider_stats['total_processed_links'] += 1
        items = []
        entries = response.xpath("//section[@class='body']")
        for a_entry in entries:
            item = GetwebdataCar()

            tmp_title = a_entry.xpath("h2[@class='postingtitle']/span[@class='postingtitletext']")
            #price
            price = int(tmp_title.xpath("span[@class='price']/text()").extract()[0].replace("$",""))
            if price < PRICE_MIN or price > PRICE_MAX:
                print "----Price %s is not within valid range, skip... "%price
                continue
            #place
            place = tmp_title.xpath("small/text()").extract()
            if place != []:
                place = place[0].strip().replace("(","").replace(")","")
                if 'best offer' in place:
                    #empty invalid place string
                    place = ''
            else:
                place = ''

            tmp_attrs = a_entry.xpath("section[@class='userbody']/div[@class='mapAndAttrs']/p[@class='attrgroup']/span")
            #entry title string
            entry_title = tmp_attrs.xpath("b/text()").extract()[0]
            #year from 1970
            year = (re.findall(r"\d{4}",entry_title)[0])
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

            #mileage, vin, title_status, car_type
            mileage = 0
            vin = ''
            title_status = ''
            car_type = ''
            for i in tmp_attrs.extract():
                tmp_value = re.findall(r"<b>(.*?)</b>",i)
                if 'odometer: ' in i:
                    #mileage
                    mileage = int(tmp_value[0])
                elif 'VIN: ' in i:
                    vin = tmp_value[0]
                elif 'title status: ' in i:
                    title_status = tmp_value[0]
                elif 'type: ' in i:
                    car_type = tmp_value[0]
            if mileage == 0 or mileage < MILEAGE_MIN or mileage > MILEAGE_MAX:
                print "----Mileage %s not within range"%mileage
                continue

            #date
            tmp_date = a_entry.xpath("section[@class='userbody']/div[@class='postinginfos']/p[@class='postinginfo reveal']/time/@datetime").extract()
            # if there're two dates, 1st is post date, 2nd is update date, e.g.
            # [u'2016-04-05T10:56:38-0700', u'2016-04-27T11:15:56-0700']
            # date is in ISO format
            date = tmp_date[0]
            if(len(tmp_date) > 1):
                date = tmp_date[1]

            price_add_mileage = int(price)+ int(mileage)
            if price_add_mileage < PRICE_AND_MILEAGE_MIN:
                #if mileage very low, price is also very low, skip
                #likely: info not correct, it's a spam or a lease transfer etc.
                continue

            url = response.url
            sf_bayarea = ["eby","nby","pen","sfc","scz","sby"]
            for area in sf_bayarea:
                if area in url.split("/"):
                    item['place_area'] = area
            item['entry_title'] = entry_title
            item['year'] = int(year)
            item['brand'] = brand
            item['price'] = int(price)
            item['mileage'] = int(mileage)
            item['price_add_mileage'] = price_add_mileage
            item['vin'] = vin
            item['title_status'] = title_status
            item['car_type'] = car_type.lower()
            item['date'] = date
            item['place'] = place
            item['url'] = url
            items.append(item)
            self.valid_link_num = self.valid_link_num + 1
            self.spider_stats['valid_links'] += 1
#            print "----Found valid entry at link %s"%item['url']
        return items

