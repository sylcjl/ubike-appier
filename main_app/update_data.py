# -*- coding: utf-8 -*-
import requests
import json
import pymysql
from datetime import datetime
from django.conf import settings


def update():
    # Data source url: "http://data.taipei/youbike"
    url = "http://data.taipei/youbike"


    # Download data, stop when error happened
    print("[ Getting Data... link to '%s' ]" % url)
    json_text = requests.get(url)
    if json_text.status_code not in ('200', 200):
        exit()
    DB = settings.DATABASES['default']
    station = json.loads(json_text.text)


    print("[ Connecting to database... ]")
    con = pymysql.connect(host=DB['HOST'], user=DB['USER'], passwd=DB['PASSWORD'], db=DB['NAME'],
                          charset='utf8', use_unicode=True)
    cur = con.cursor(pymysql.cursors.DictCursor)


    print("[ Parse station informations... ]")
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


    # create_table = """CREATE TABLE IF NOT EXISTS `station` (
    #                   `sno` varchar(4) NOT NULL DEFAULT '',
    #                   `sna` varchar(255) NOT NULL DEFAULT '',
    #                   `sarea` varchar(255) NOT NULL DEFAULT '',
    #                   `lat` float NOT NULL,
    #                   `lng` float NOT NULL,
    #                   `ar` varchar(255) NOT NULL DEFAULT '',
    #                   `sareaen` varchar(255) NOT NULL DEFAULT '',
    #                   `snaen` varchar(255) NOT NULL DEFAULT '',
    #                   `aren` varchar(255) NOT NULL DEFAULT '',
    #                   `tot` int(3) NOT NULL,
    #                   `sbi` int(3) NOT NULL,
    #                   `bemp` int(3) NOT NULL,
    #                   `act` int(1) NOT NULL,
    #                   `mday` datetime NOT NULL,
    #                   `point` point DEFAULT NULL,
    #                   PRIMARY KEY (`sno`)
    #                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    # cur.execute(create_table)
    # con.commit()

