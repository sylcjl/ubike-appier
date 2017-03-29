# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from . import models
import requests
import json
from . import update_data
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.

EARTH_RAD_KM = 6371
GOOGLKEY = "AIzaSyBU4Sk8Yq8pB1zSFdUPygbqZd7wyMfVIuI"


class Taipei(APIView):
    # http_method_names = ["GET"]
    # please handle error / exceptions with following scenarios ( and return coressponding
    # error codes)
    # 1: all ubike stations are full
    # 0: OK
    # -1: invalid latitude or longitude
    # -2: given location not in Taipei City
    # -3: system error

    def __init__(self):
        self.lat = None
        self.lng = None
        self.result = {'code': -3, 'result': []}

    @property
    def update_data(self):
        print("Updating youbike stations infomations...")
        update_data.update()
        print("Update finished.")

    def get(self, request, *args, **kwargs):
        with_update = kwargs.get("update", False)
        if with_update:
            self.update_data
        self.lat = request.GET.get('lat')
        self.lng = request.GET.get('lng')
        if not self.check_lat_lng:
            return Response(self.result)

        # Taipei city postal code starts with '1'
        if not self.check_city('1'):
            return Response(self.result)

        # get station status
        stats = self.station_stats()
        self.result['result'] = stats

        # return result
        return Response(self.result)

    def station_stats(self):
        # check station status
        results = []
        stations = self.get_station_stats(drange=25, limit=2)
        for station in stations:
            # {"station": "捷運象山站", "num_ubike": 10}
            temp_dict = {}
            if station.bemp:
                temp_dict['station'] = station.sna
                temp_dict['num_ubike'] = station.bemp
                results.append(temp_dict)

        if not results:
            self.result['code'] = 1  # all stations are full
            return []
        return results

    @property
    def check_lat_lng(self):
        # Handle longitude error and latitude error
        try:
            self.lat = float(self.lat)
            self.lng = float(self.lng)
        except ValueError:
            self.result['code'] = -1  # -1 means invalid latitude or latitude
            return False
        except:
            self.result['code'] = -3  # -3 means system error
            return False
        return True

    def check_city(self, postal_code):
        # Handle errors
        if not isinstance(postal_code, (int, str)):
            raise ValueError
        if isinstance(postal_code, int):
            try:
                postal_code = str(postal_code)
            except:
                raise ValueError

        # process start
        # get location informations from google maps api
        url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key=%s" % GOOGLKEY
        response = requests.get(url.format(lat=self.lat, lng=self.lng))
        results = json.loads(response.text)

        # check result status
        if results['status'] in ('OK',):
            components = results['results'][0].get('address_components', {})

            # check postal code exists or not
            if len(components):
                if postal_code \
                        and components[-1]['types'][-1] in ('postal_code',) \
                        and components[-1]['short_name'].startswith(postal_code):
                    self.result['code'] = 0
                    return True  # 0 means ok
        self.result['code'] = -2  #-2 means not in this city
        return False  

    def get_station_stats(self, drange, limit):
        sql = """SELECT sno, sna, bemp, ({cons} * acos(cos(radians({begin_lat})) * cos(radians(lat))
                * cos(radians(lng) - radians({begin_lng})) + sin(radians({begin_lat})) * sin(radians(lat)))) AS distance
                FROM station
                WHERE act = 1
                HAVING distance < {range}
                ORDER BY distance
                LIMIT 0 , {limit};""".format(cons=EARTH_RAD_KM,
                                             begin_lat=self.lat, begin_lng=self.lng, range=drange, limit=limit)
        return models.Station.objects.raw(sql)
