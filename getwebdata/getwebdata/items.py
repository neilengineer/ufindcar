# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy

#car info struct
#fields with #* are must have
class GetwebdataCar(scrapy.Item):
    brand = scrapy.Field()          #*
    entry_title = scrapy.Field()    #*
    year = scrapy.Field()           #*
    price = scrapy.Field()          #*
    mileage = scrapy.Field()        #*
    #The best used car is on x+y=a, where 'a' can be found by min(x+y)
    #Then closest other x+y is, the better
    price_add_mileage = scrapy.Field()  #*
    vin = scrapy.Field()            #*
    title_status = scrapy.Field()   #*
    date = scrapy.Field()           #*
    url = scrapy.Field()            #*
    doc_update_date = scrapy.Field()    #*
    model = scrapy.Field()
    car_type = scrapy.Field()
    car_size = scrapy.Field()
    mpg = scrapy.Field()
    color = scrapy.Field()
    drivetrain = scrapy.Field()
    transmission = scrapy.Field()
    place = scrapy.Field()
    place_area = scrapy.Field()
    who = scrapy.Field()
    place_holder0 = scrapy.Field()  #fields for future use

#Per collection generic info
class GetwebdataCollinfo(scrapy.Item):
    coll_name = scrapy.Field()
    last_update_url = scrapy.Field()
    last_update_time = scrapy.Field()
    total_processed_links = scrapy.Field()
    valid_links = scrapy.Field()
    total_processed_pages = scrapy.Field()

