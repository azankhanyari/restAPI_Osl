import json
import urllib.parse
import urllib.request
from collections import defaultdict
from src.BikeAPI.OslobikeAPI import OslB
from src.ArdoqAPI.Initial_push_data_Ardoq import arqQ
import time



class Arq_stations():


    def compare_station_IDs(self,existing_data,oslobike_data,rootWorkspace, typeId):

        existing_station_IDs = {components.get('customFields').get('station_id') for components in existing_data['values']}  # extract station_id identifier from ArdoqAPI to check against Oslobike station feed

        oslobikeAPI_station_ids= {item.get('customFields').get('station_id') for item in oslobike_data}               # real time API station_ids

        ArOID_stationid_mapping = defaultdict(list)
        for component in existing_data['values']:
            ArOID_stationid_mapping[component.get('customFields').get('station_id')] = component.get('_id')            # station_id -> ArdoqComponentid mapping for DELETE operation




        if len(existing_station_IDs.intersection(oslobikeAPI_station_ids)) == len(oslobikeAPI_station_ids)  :           # all station data is same
            integrity = True

        elif len(oslobikeAPI_station_ids.difference(existing_station_IDs)) > 0:                                      # new station information in OsloAPI, need to create new component
            integrity = False
            toPUSH_components = []

            for newitem in oslobikeAPI_station_ids.difference(existing_station_IDs):
                for data in oslobike_data:
                    if data.get('customFields').get('station_id') == newitem:                                              # get station id to PUSH to ardoqAPI

                        data.update({'rootWorkspace': rootWorkspace, 'typeId': typeId})

                        toPUSH_components.append(arQ_obj.ARD_request(method="POST", endpoint='/api/v2/components',
                                                                  ARDOQ_API_HOST='XXX',
                                                                  ARDOQ_API_TOKEN='xxx',
                                                                  data=data))
                        break


        elif len(existing_station_IDs.difference(oslobikeAPI_station_ids)) > 0:                                       # existing station id is purged from OsloAPI, should be deleted from ardoqAPI too
            integrity = False

            for olditem in existing_station_IDs.difference(oslobikeAPI_station_ids):
                ArdOID = ArOID_stationid_mapping.get(olditem)
                delete_responses.append(arQ_obj.ARD_request(method="DELETE", endpoint='/api/v2/components', path_param=ArdOID,                                                            #ArdoqID for station id to be removed
                                                         ARDOQ_API_HOST='XXX',
                                                         ARDOQ_API_TOKEN='xxx'))



        return integrity




if __name__ == '__main__':
    starttime = time.time()

    while True:

        arQ_obj = arqQ()
        existing_data = arQ_obj.ARD_request(ARDOQ_API_HOST='XXX',endpoint='/api/v2/components',ARDOQ_API_TOKEN='xxx', method="GET",data=None, query_params=None,path_param=None)  # for all bike station componentIDs fetch everything
        existing_data = json.loads(existing_data)
        rootWorkspace, typeId = arQ_obj.extractParams(existing_data)


        oslb_obj = OslB()
        station_information = oslb_obj.oslobikeapi_fetch(host="https://gbfs.urbansharing.com/oslobysykkel.no/",endpoint="station_information.json")
        station_status = oslb_obj.oslobikeapi_fetch(host="https://gbfs.urbansharing.com/oslobysykkel.no/",endpoint="station_status.json")
        consolidated_station_data, realtime_station_status_dict = oslb_obj.process(station_information, station_status)


        arq_stations_obj = Arq_stations()
        arq_stations_obj.compare_station_IDs(existing_data,consolidated_station_data,rootWorkspace, typeId)



        time.sleep(86400.0 - ((time.time() - starttime) % 86400.0))   #run every 24 hour

