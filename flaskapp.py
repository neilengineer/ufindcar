import os
import re
import json
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime,timedelta
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory
import pymongo
import dateutil.parser as parser
from collections import OrderedDict
from emailme  import emailme

#import sys
app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

if os.environ.get('OPENSHIFT_APP_NAME') != None:
    #openshift server
    my_mongo_uri = os.environ['OPENSHIFT_MONGODB_DB_URL']
else:
    #local dev machine
    my_mongo_uri = 'localhost:27017'
my_database = 'ufindcar'
all_colls_map = OrderedDict([('craig\'s list','craig'), ('dgdg.com','dgdg'),('hertz car sales','hertz')])
default_coll_str = all_colls_map.keys()[0]
default_coll_name = all_colls_map[default_coll_str]
default_skip_num = 0
default_query_num = 100

@app.route('/', methods=['GET', 'POST'])
def index():
    ufindcar_data = []
    skip_num = default_skip_num
    query_num = default_query_num
    coll_str = default_coll_str
    coll_name = default_coll_name
    query_range_str = ''
    num = ''

    if request.method == 'POST':
        coll_str = request.form.get("data_source","")
        if coll_str != "":
            coll_name = all_colls_map[coll_str]
        else:
            coll_str = default_coll_str
        num = request.form.get("query_num","")
        print "POST:use collection %s"%coll_name
    else:
        coll_str = request.args.get("data_source","")
        if coll_str != "":
            coll_name = all_colls_map[coll_str]
        else:
            coll_str = default_coll_str
        num = request.args.get("query_num","")
        print "GET: use collection %s"%coll_name

    if num != '':
        query_nums = re.findall(r'\d+', num)
        if len(query_nums) == 1:
            query_num = int(num)
        elif len(query_nums) >= 2:
            skip_num = int(query_nums[0])
            query_num = int(query_nums[1]) - skip_num
            if query_num <= 0:
                skip_num = default_skip_num
                query_num = default_query_num
        else:
            skip_num = default_skip_num
            query_num = default_query_num

    #entries within 48 hours
    update_time = datetime.now() - timedelta(hours=24)
    db_client = pymongo.MongoClient(my_mongo_uri)
    mydb = db_client[my_database]
    cursor = (mydb[coll_name].find({"coll_name":{"$exists":False}, \
                "doc_update_date":{"$gte": update_time} } ) \
                .sort("price_add_mileage",pymongo.ASCENDING))
    coll_total_num_in_24 = cursor.count()
    if query_num <= 0 or skip_num < 0 or skip_num >= coll_total_num_in_24:
        skip_num = default_skip_num
        query_num = default_query_num
    if query_num > coll_total_num_in_24 or (skip_num + query_num) > coll_total_num_in_24:
        query_num = coll_total_num_in_24-skip_num

    query_range_str = str(skip_num)+'-'+str(skip_num+query_num)
    cursor = list(cursor.skip(skip_num).limit(query_num))
    #we have a python list of dicts now
    if cursor != None:
        #json module won't work due to things like the ObjectID, use pymongo json_util
        #dump to json string
        ufindcar_data = json.dumps(cursor, default=json_util.default)

    cursor_time = mydb[coll_name].find({'coll_name':coll_name})
    if cursor_time != None:
        for document in cursor_time:
            if 'last_update_time' in document.keys():
                tmp_time = parser.parse(document['last_update_time'])
                last_update_date = tmp_time.date().strftime("%Y-%m-%d")
                last_update_time = tmp_time.time().strftime("%H:%M:%S")

#    print (ufindcar_data)
#    print sys.getsizeof(ufindcar_data)
    return render_template('index.html', ufindcar_data = ufindcar_data, show_car_num = len(cursor), \
            all_colls = all_colls_map.keys(), current_coll=coll_name , current_coll_str = coll_str, \
            coll_total_num_24 = coll_total_num_in_24, last_update_date = last_update_date, \
            last_update_time=last_update_time, query_range_str = query_range_str)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how')
def how():
    return render_template('how.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    email = ''
    msg = ''
    thankyou = ''
    if request.method == 'POST':
        first_name = request.form.get("first_name","")
        last_name = request.form.get("last_name","")
        email = request.form.get("email","")
        msg = request.form.get("message","")
        if email == '' or msg == '':
            thankyou = 'Sorry, please put in email and message you want to say.'
        else:
            thankyou = 'Thanks for contacting us, we will get back to you shortly.'

    if email != '' and msg != '':
        title = 'Ufindcar contact us: '+first_name+' '+last_name+' email:'+email
        emailme(title, msg)

    return render_template('contact.html', thankyou = thankyou)

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)

@app.route("/test")
def test():
    return "<strong>It's Alive!</strong>"

if __name__ == '__main__':
    app.run()
