#!/bin/sh

debug_en=$1
log='log.txt'

#craig
#scrapy crawl craig -a debug=$debug_en -s LOG_FILE=$log
scrapy crawl craig -a debug=$debug_en

#dgdg
scrapy crawl dgdg -a debug=$debug_en

#hertz
scrapy crawl hertz -a debug=$debug_en

