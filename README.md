
OslobikeAPI.py must be run to fetch real time data from two Oslo Bikes endpoints - these give us information about station_ids and each station_status ##
Initial_push_data_Ardoq.py  This is the initial push to our Ardoq Worspace. Each station is created as a new bike station component in our workspace. Old data on workspace is purged before inital push. Each bike station component has certain fields as below:## 

'description'##
'_id', ##
'_meta', ##
'parent', ##
'name',##
'customFields':{address', 'currently_renting_bikes', 'geocoordinates', 'mostrecentfeed', 'station_id', 'num_dockstations_available', 'currently_returning_bikes', 'num_available_bikes'}##
'type', ##
'rootWorkspace',##
'typeId', ##
'componentKey', ##
'_version'##


We first create new customFields from within the Ardoq SaaS website as API currently does not allow creating new fields. ##
Assumptions- We assume fields related to a bike station like Name, station_id, address, geocoordinates to be relatively low on changes per day whereas bike stations fields from OsloAPI endpoint- 'station_status'
change more frequently. These are fields - 'currently_renting_bikes','num_dockstations_available', 'currently_returning_bikes', 'num_available_bikes'. Hence below strategy is implemented. ##

File updates_push.py is set to keep running every 2 hours (can be set to any time interval). This file fetches realtime API feed for each bike component station_status and updates all bike station component's fast changing fields. Only frequently changing bike station fields change on the Ardoq workspace.
File - station_integrity_check.py is set to run every 24 hours, and will make sure the bike station components on Ardoq remain in sync with the latest station information (slowly changing fields) regularly.##
If some station ids are purged by OslobikeAPI, they will be subsequently deleted from Ardoq workspace. Similarly if OsloBike API adds new stations they will be created on the Ardoq workspace.



