import scrapy
import pymongo
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from getwebdata.items import GetwebdataCar, GetwebdataCollinfo
from getwebdata.settings import my_mongo_uri, my_database
import json

PRICE_MIN = 2000
PRICE_MAX = 30000
YEAR_MIN = 2000
MILEAGE_MIN = 5000
MILEAGE_MAX = 150000
PRICE_AND_MILEAGE_MIN = 10000

class dgdgspider(CrawlSpider):
    #crawl method:
    #with firebug, find out the request GET command (the url) which'll get the reposonse as json string!
    collection_name = 'hertz'
    name = "hertz"
    allowed_domains = ["hertzcarsales.com"]
    start_urls = [
"https://www.hertzcarsales.com/api/VehicleSearch/GetQuickViewVehicles?Distance=50mi&MapLat=37.3415879&MapLong=-121.88614510000002&MINPRICE=0&MAXPRICE=10000&SORTER=Price&SORTORDER=Ascending&BUCKETPAGE=1&pageSize=0&pageNumber=0&BUCKETNAME=Under10000",
"https://www.hertzcarsales.com/api/VehicleSearch/GetQuickViewVehicles?Distance=50mi&MapLat=37.3415879&MapLong=-121.88614510000002&MINPRICE=10000&MAXPRICE=15000&SORTER=Price&SORTORDER=Ascending&BUCKETPAGE=1&pageSize=0&pageNumber=0&BUCKETNAME=10000-20000",
"https://www.hertzcarsales.com/api/VehicleSearch/GetQuickViewVehicles?Distance=50mi&MapLat=37.3415879&MapLong=-121.88614510000002&MINPRICE=15000&MAXPRICE=30000&SORTER=Price&SORTORDER=Ascending&BUCKETPAGE=1&pageSize=0&pageNumber=0&BUCKETNAME=10000-20000",
    ]

    page_num = 0
    total_page_num = 0
    total_processed_link_num = 0
    valid_link_num = 0
    spider_stats = GetwebdataCollinfo()
    base_url = "https://www.hertzcarsales.com/vehicle/details/"

#    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//div[@class="mod"]/a',)), callback="parse_page", follow=True),)

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
        items = []

        data = json.loads(response.body)
        vehicle_info = data['Vehicles']

        for v in vehicle_info:
            self.total_processed_link_num = self.total_processed_link_num + 1
            self.spider_stats['total_processed_links'] += 1
            item = GetwebdataCar()

            year = int(v['Year'])
            if year == '' or year < YEAR_MIN:
                print "----Year not found or too old in %s, skip..."%entry_title
                continue
            brand = v['Make']
            price = int(v['PriceDisplay'].split('.')[0].replace("$","").replace(",",""))
            if price < PRICE_MIN or price > PRICE_MAX:
                print "----Price %s is not within valid range, skip... "%price
                continue
            mileage = int(v['Mileage'].split('.')[0])
            if mileage == 0 or mileage < MILEAGE_MIN or mileage > MILEAGE_MAX:
                print "----Mileage %s not within range"%mileage
                continue
            price_add_mileage = price + mileage
            if price_add_mileage < PRICE_AND_MILEAGE_MIN:
                print "----mileage + price too low, skip"
                continue
            model = v['Model']
            car_type = v['BodyType']
            vin = v['Vin']
            date = v['DateAvailable']
            url = self.base_url + str(v['Vid'])
            place = v['City']+','+v['StateName']
            entry_title = str(year) + ' '+ brand +' '+ model

            item['entry_title'] = entry_title.lower()
            item['year'] = year
            item['brand'] = brand.lower()
            item['model'] = model.lower()
            item['price'] = price
            item['mileage'] = mileage
            item['price_add_mileage'] = price_add_mileage
            item['vin'] = vin
            item['car_type'] = car_type.lower()
            item['date'] = date 
            item['url'] = url
            item['title_status'] = 'NA'
            item['place'] = place
            items.append(item)
            self.valid_link_num = self.valid_link_num + 1
            self.spider_stats['valid_links'] += 1
#            print "----Found valid entry at link %s"%item['url']
        #end of for
        return items

#vehicle info example
#data.keys() is [u'NewBodyStyle', u'Vehicles', u'NewSearchRadius', u'NoResultsFound', u'BucketsPerPage']
'''
u'Vehicles' is list of the following json dicts
 {u'Available': u'Yes',
  u'BodyType': u'Short Bed',
  u'BucketDisplayName': u'$20,000 - $30,000',
  u'BucketMax': 0.0,
  u'BucketMin': 0.0,
  u'BucketName': u'20000-30000',
  u'BucketOrder': 1,
  u'BucketPage': 1,
  u'BucketTotal': 212,
  u'BusinessUnitID': u'R2BUS',
  u'City': u'Hayward',
  u'CountryCode': u'US',
  u'DateAvailable': u'2016-05-04T00:00:00-04:00',
  u'DateAvailableDisplay': u'05/04/2016',
  u'DiscountAmount': 0.0,
  u'DiscountText': u'',
  u'Distance': 0.0,
  u'DistanceDisplay': None,
  u'DriveTrain': u'RWD',
  u'EPA': None,
  u'EPACity': 0,
  u'EPAHwy': 0,
  u'Engine': None,
  u'ExteriorColor': u'Silver',
  u'Features': u'',
  u'FeaturesCode': 1,
  u'FuelEconomy': None,
  u'FuelType': u'Gasoline Fuel',
  u'HertzModelid': None,
  u'ImageCount': 3,
  u'ImageUrl': u'9442_K23_1.jpg',
  u'InteriorColor': u'Brown',
  u'IsCertified': False,
  u'IsSuggestedVehicle': False,
  u'KBBPrice': 24790.0,
  u'KBBPriceDisplay': u'$24,790',
  u'Make': u'Nissan',
  u'Mileage': u'37999.0',
  u'MileageDisplay': u'38K',
  u'Model': u'Frontier',
  u'OriginalPriceDisplay': u'$21,000',
  u'OwnArea': None,
  u'PickupLocationId': 0,
  u'Price': 21000.0,
  u'PriceDiff': 0.0,
  u'PriceDiffDisplay': None,
  u'PriceDisplay': u'$21,000',
  u'PriceRange': None,
  u'SortBucket': u'Price',
  u'StateName': u'CA',
  u'StateProvinceCode': u'CA',
  u'StreetAddress': None,
  u'TotalBucketPages': 1,
  u'TotalResults': 3274,
  u'Transmission': u'AUTO 5-SPEED',
  u'Trim': u'SV',
  u'UnitId': None,
  u'Vid': 14405331,
  u'Vin': u'1N6AD0ER5EN744751',
  u'Year': 2014}
'''
