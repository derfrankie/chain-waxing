
================================================================

Get Authenticated Athlete (getLoggedInAthlete)
Returns the currently authenticated athlete. Tokens with profile:read_all scope will receive a detailed athlete representation; all others will receive a summary representation.

$ http GET "https://www.strava.com/api/v3/athlete" "Authorization: Bearer [[token]]"

{
  "id" : 1234567890987654321,
  "username" : "marianne_t",
  "resource_state" : 3,
  "firstname" : "Marianne",
  "lastname" : "Teutenberg",
  "city" : "San Francisco",
  "state" : "CA",
  "country" : "US",
  "sex" : "F",
  "premium" : true,
  "created_at" : "2017-11-14T02:30:05Z",
  "updated_at" : "2018-02-06T19:32:20Z",
  "badge_type_id" : 4,
  "profile_medium" : "https://xxxxxx.cloudfront.net/pictures/athletes/123456789/123456789/2/medium.jpg",
  "profile" : "https://xxxxx.cloudfront.net/pictures/athletes/123456789/123456789/2/large.jpg",
  "friend" : null,
  "follower" : null,
  "follower_count" : 5,
  "friend_count" : 5,
  "mutual_friend_count" : 0,
  "athlete_type" : 1,
  "date_preference" : "%m/%d/%Y",
  "measurement_preference" : "feet",
  "clubs" : [ ],
  "ftp" : null,
  "weight" : 0,
  "bikes" : [ {
    "id" : "b12345678987655",
    "primary" : true,
    "name" : "EMC",
    "resource_state" : 2,
    "distance" : 0
  } ],
  "shoes" : [ {
    "id" : "g12345678987655",
    "primary" : true,
    "name" : "adidas",
    "resource_state" : 2,
    "distance" : 4904
  } ]
}





================================================================

Get Equipment (getGearById)
Returns an equipment using its identifier.

GET
/gear/{id}
Parameters
id
required String, in path	The identifier of the gear.
Responses
HTTP code 200	A representation of the gear. An instance of DetailedGear.
HTTP code 4xx, 5xx	A Fault describing the reason for the error.



Python

from __future__ import print_statement
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: strava_oauth
swagger_client.configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.GearsApi()
id = id_example # String | The identifier of the gear.

try: 
    # Get Equipment
    api_response = api_instance.getGearById(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GearsApi->getGearById: %s\n" % e)


Responses
{
  "id" : "b1231",
  "primary" : false,
  "resource_state" : 3,
  "distance" : 388206,
  "brand_name" : "BMC",
  "model_name" : "Teammachine",
  "frame_type" : 3,
  "description" : "My Bike."
}
================================================================


I want to create a go script where:

- the script has 2 global variables: wax_interval = 300 and drip_interval = 100
- the script has / creates a config file
- the script can connect to more than one strava accounts
- has various command line commands (which calls available functions)
  - addAccount 
    - The script asks for username and password and writes that to the config file
    - the script connects to the strava account and reads the profile (getLoggedInAthlete)
    - add to the profile the username and password and 2 parameters to each bike set to Null : waxed_km, drip_km, wax_state
    - write the profile to the config file
    - continue to showBikes
  - showBikes
    - if the config file has no profile saved
      - call addAcount
    - for each account in the config
      - connect to strava with the username password from the profile
      - read the current information for bikes from the config and update the distance via getLoggedInAthlete, give each bike a number (bikeNumber) and keep them globally in Memory
      - Write the updated distance for each bike to the config file
      - Print the First and Second Name of the user on the screen
      - wax_state = "OK"
      - if drip_km is not NULL
        - if distance - drip_km > drip_interval then wax_state ="Drip Wax Please"
      - if waxed_km is not NULL
        - if distance - drip_km > drip_interval then wax_state ="Drip Wax Please"
        - if distance - waxed_km > wax_interval then wax_state ="Wax Please"
      - Print a table of the bikes with following information: bikenumber, name, distance, waxed-km, drip-km, wax_state
  - Driped
    - Call ShowBikes
    - Ask which bike the user wants to "drip" - he can enter the bikenumber
    - Update the drip-km to the current distance - write the bike information to the config file
    - Call Showbikes





