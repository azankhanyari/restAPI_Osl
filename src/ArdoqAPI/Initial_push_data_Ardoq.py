import json
import urllib.parse
import urllib.request
from src.BikeAPI.OslobikeAPI import OslB
import time

class arqQ():

    def ARD_request(self, ARDOQ_API_HOST, endpoint, ARDOQ_API_TOKEN, method, data=None, query_params=None,
                    path_param=None):
        MAX_RETRIES = 10
        retries = 0

        url = ARDOQ_API_HOST + endpoint

        if path_param:
            url = url + '/' + path_param
        if query_params:
            url = url + "?" + urllib.parse.urlencode(query_params)

        if method == 'GET':
            while retries < MAX_RETRIES:
                try:

                    req = urllib.request.Request(url)
                    req.add_header("Authorization", "Bearer " + ARDOQ_API_TOKEN)
                    with urllib.request.urlopen(req) as resp:
                        if resp.getcode() in [200, 201, 202]:
                            return resp.read().decode('utf-8')

                        else:
                            raise Exception("Invalid HTTP response code")
                except Exception as e:
                    retries += 1
                    time.sleep(2 ** retries)
            return None



        elif method == 'POST':
            while retries < MAX_RETRIES:
                try:

                    data = json.dumps(data).encode("utf-8")
                    req = urllib.request.Request(url, data=data, method='POST')
                    req.add_header("Authorization", "Bearer " + ARDOQ_API_TOKEN)
                    req.add_header("Content-Type", "application/json; charset=utf-8")


                    with urllib.request.urlopen(req, data=data) as resp:
                        if resp.getcode() in [200, 201, 202]:
                            return resp.read().decode('utf-8')

                        else:
                            raise Exception("Invalid HTTP response code")

                except Exception as e:
                    retries += 1
                    time.sleep(2 ** retries)


            return None



        elif method == 'DELETE':
            while retries < MAX_RETRIES:
                try:

                    req = urllib.request.Request(url, method='DELETE')
                    req.add_header("Authorization", "Bearer " + ARDOQ_API_TOKEN)
                    with urllib.request.urlopen(req) as resp:
                        if resp.getcode() in [204]:
                            return resp.getcode()

                        else:
                            raise Exception("Invalid HTTP response code")

                except Exception as e:
                    retries += 1
                    time.sleep(2 ** retries)
            return None

        elif method == 'PATCH':

            while retries < MAX_RETRIES:
                try:

                    req = urllib.request.Request(url, method='PATCH')
                    req.add_header("Authorization", "Bearer " + ARDOQ_API_TOKEN)
                    req.add_header("Content-Type", "application/json; charset=utf-8")
                    data = json.dumps(data).encode('utf-8')
                    with urllib.request.urlopen(req, data=data) as resp:
                        if resp.getcode() in [200, 201, 202]:
                            return resp.read().decode('utf-8')

                        else:
                            raise Exception("Invalid HTTP response code")

                except Exception as e:
                    retries += 1
                    time.sleep(2 ** retries)

            return None



        else:
            raise ValueError('Invalid Method')


    def extractParams(self,existing_data):

        rootWorkspace, typeId = existing_data['values'][0].get('rootWorkspace'), existing_data['values'][0].get('typeId')

        return rootWorkspace,typeId

    def initial_push(self,consolidated_station_data,rootWorkspace,typeId):

        for components in consolidated_station_data:
            components.update({'rootWorkspace': rootWorkspace, 'typeId': typeId})

        pushed_components = []
        for components in consolidated_station_data:
            pushed_components.append(self.ARD_request(method="POST", endpoint='/api/v2/components',ARDOQ_API_HOST='https://caseinterviewazan.ardoq.com',ARDOQ_API_TOKEN='9e15d653cbec4cffab6622d4352f2bc9', data=components))

        return pushed_components

    def delete_all_components(self,existing_data):

        delete_responses = []
        for component in existing_data['values']:
            id =component.get('_id')
            delete_responses.append(self.ARD_request(method="DELETE", endpoint='/api/v2/components', path_param=id,ARDOQ_API_HOST='https://caseinterviewazan.ardoq.com',ARDOQ_API_TOKEN='9e15d653cbec4cffab6622d4352f2bc9'))



if __name__ == '__main__':

    arQ_obj = arqQ()
    existing_data = arQ_obj.ARD_request(ARDOQ_API_HOST = 'https://caseinterviewazan.ardoq.com', endpoint ='/api/v2/components', ARDOQ_API_TOKEN= '9e15d653cbec4cffab6622d4352f2bc9', method= "GET", data=None, query_params=None,path_param=None)                       #rootWorkspace , typeId is required for inital push of components to Ardoq API
    existing_data = json.loads(existing_data)
    rootWorkspace,typeId = arQ_obj.extractParams(existing_data)

    oslb_obj = OslB()
    station_information = oslb_obj.oslobikeapi_fetch(host="https://gbfs.urbansharing.com/oslobysykkel.no/",endpoint="station_information.json")
    station_status = oslb_obj.oslobikeapi_fetch(host="https://gbfs.urbansharing.com/oslobysykkel.no/",endpoint="station_status.json")
    consolidated_station_data,station_status_dict = oslb_obj.process(station_information, station_status)

    arQ_obj.delete_all_components(existing_data)
    pushed_components = arQ_obj.initial_push(consolidated_station_data,rootWorkspace,typeId)

    print('done')