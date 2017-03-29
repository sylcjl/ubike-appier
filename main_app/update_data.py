# -*- coding: utf-8 -*-
import requests
import json
import pymysql
from datetime import datetime

# Data source url: "http://data.taipei/youbike"
url = "http://data.taipei/youbike"

# Download data, stop when error happened
json_text = requests.get(url)
if json_text.status_code not in ('200', 200):
    exit()

station = json.loads(json_text.text)
con = pymysql.connect(host="localhost", user="user1", passwd="user", db="ubike",
                      charset='utf8', use_unicode=True)
cur = con.cursor(pymysql.cursors.DictCursor)

fields = ['sno', 'sna', 'sarea', 'lat', 'lng', 'ar', 'sareaen',
          'snaen', 'aren', 'mday', 'tot', 'sbi', 'bemp', 'act']

for _id, detial in station['retVal'].items():
    # datatime field
    for key, val in detial.items():
        if "'" in val:
            detial[key] = val.replace("'", '"')
    detial['new_mday'] = datetime.strptime(detial['mday'], "%Y%m%d%H%M%S")

    sql_base = "REPLACE INTO `station`({0}) VALUES (%s);".format(','.join(fields))
    placeholder = "'%s'" + ",'%s'" * (9) + ",%s" * 4
    vals = placeholder % (detial['sno'], detial['sna'], detial['sarea'],
                          detial['lat'], detial['lng'], detial['ar'],
                          detial['sareaen'], detial['snaen'], detial['aren'],
                          detial['mday'], detial['tot'], detial['sbi'],
                          detial['bemp'], detial['act'])
    sql = sql_base % vals
    # print(sql)
    cur.execute(sql)
con.commit()
cur.close()
con.close()