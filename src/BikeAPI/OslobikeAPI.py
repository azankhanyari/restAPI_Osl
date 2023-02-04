import json
import os
import urllib.request
import urllib.parse
import requests
from collections import defaultdict
import time


class OslB:

    def oslobikeapi_fetch(self,host:str,endpoint:str):
        MAX_RETRIES = 10
        retries = 0

        while retries < MAX_RETRIES:
            try:
                url = host + endpoint
                req = urllib.request.Request(url, method="GET")

                with urllib.request.urlopen(req) as resp:
                    if resp.getcode() in [200, 201, 202]:

                        return json.loads(resp.read().decode("utf-8")).get('data')

                    else:
                        raise Exception("Invalid HTTP response code")
            
            except Exception as e:
                retries += 1
                time.sleep(2 ** retries)
                
        return None
    

    def process(self,station_information:list,station_status:list):

        station_status_dict = defaultdict(dict)
        for item in station_status['stations']:
            station_status_dict[item['station_id']] = {'currently_renting_bikes': bool(item.get('is_renting')),
                                                      'currently_returning_bikes': bool(item.get('is_renting')),
                                                      'num_available_bikes': item.get('num_bikes_available'),
                                                      'num_dockstations_available': item.get('num_docks_available')}

        consolidated_station_data = []
        for stationdata in station_information['stations']:
            inner = {}

            inner['name'] = stationdata.get('name')
            inner['description'] = 'sourcedfrom -- https://gbfs.urbansharing.com/oslobysykkel.no/'
            inner['customFields'] = {'address': stationdata.get('address'),
                                     'geocoordinates': str(stationdata.get('lat')) + ',' + str(stationdata.get('lon')),
                                     'station_id': stationdata.get('station_id'),
                                     'currently_renting_bikes': station_status_dict[stationdata.get('station_id')].get(
                                         'currently_renting_bikes'),
                                     'currently_returning_bikes': station_status_dict[stationdata.get('station_id')].get(
                                         'currently_returning_bikes'),
                                     'num_available_bikes': station_status_dict[stationdata.get('station_id')].get(
                                         'num_available_bikes'),
                                     'num_dockstations_available': station_status_dict[
                                         stationdata.get('station_id')].get('num_dockstations_available')}

            consolidated_station_data.append(inner)

        return  consolidated_station_data,station_status_dict






if __name__ == '__main__':

    oslb_obj = OslB()
    station_information= oslb_obj.oslobikeapi_fetch(host="https://gbfs.urbansharing.com/oslobysykkel.no/", endpoint= "station_information.json")
    station_status = oslb_obj.oslobikeapi_fetch(host= "https://gbfs.urbansharing.com/oslobysykkel.no/", endpoint= "station_status.json")
    consolidated_station_data,station_status_dict = oslb_obj.process(station_information,station_status)
    print('done')