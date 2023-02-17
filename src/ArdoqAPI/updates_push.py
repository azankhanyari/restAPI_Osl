import json
import urllib.parse
import urllib.request
from collections import defaultdict
from src.BikeAPI.OslobikeAPI import OslB
from src.ArdoqAPI.Initial_push_data_Ardoq import arqQ
import time



class UpdatesArQ():


    def getOIDs(self,existing_data,realtime_station_status_dict):

        dict_component = {item.get('customFields').get('station_id'): item.get('_id') for item in existing_data['values']}   #ardoqIOD - stationID mapping

        updates_dict = []
        for k,v in realtime_station_status_dict.items():
            updates_dict.append({dict_component.get(k):{'customFields':v}})





        return updates_dict


    def update_customrealtimeFields(self,updates_dict):
        patch_resp= []

        for item in updates_dict:
            for arOID,dynamicFields in item.items():

                patch_resp.append(arQ_obj.ARD_request(method="PATCH", endpoint='/api/v2/components', path_param=arOID,
                                     ARDOQ_API_HOST='XXX',
                                     ARDOQ_API_TOKEN='xxx',
                                     query_params={'ifVersionMatch': 'latest'},
                                     data=dynamicFields))

        return patch_resp



if __name__ == '__main__':
    starttime = time.time()

    while True:

        arQ_obj = arqQ()
        existing_data = arQ_obj.ARD_request(ARDOQ_API_HOST='XXX',endpoint='/api/v2/components',ARDOQ_API_TOKEN='xxx', method="GET",data=None, query_params=None,path_param=None)  # for all bike station componentIDs fetch everything
        existing_data = json.loads(existing_data)



        oslb_obj = OslB()
        station_information = oslb_obj.oslobikeapi_fetch(host="https://gbfs.urbansharing.com/oslobysykkel.no/",endpoint="station_information.json")
        station_status = oslb_obj.oslobikeapi_fetch(host="https://gbfs.urbansharing.com/oslobysykkel.no/",endpoint="station_status.json")
        consolidated_station_data,realtime_station_status_dict = oslb_obj.process(station_information, station_status)

        Update_obj= UpdatesArQ()
        updates_dict = Update_obj.getOIDs(existing_data,realtime_station_status_dict)  #real time fields fetch
        update_responses = Update_obj.update_customrealtimeFields(updates_dict)

        #print((time.time() - starttime) % 3600.0)
        time.sleep(3600.0 - ((time.time() - starttime) % 3600.0))   #run every 1 hour

        #existing_data = arQ_obj.ARD_request(ARDOQ_API_HOST = 'XXX', endpoint ='/api/v2/components', ARDOQ_API_TOKEN= 'xxx', method= "GET", data=None, query_params=None,path_param=None)                       #rootWorkspace , typeId is required for inital push of components to Ardoq API


        #rootWorkspace, typeId = arQ_obj.extractParams(existing_data)
