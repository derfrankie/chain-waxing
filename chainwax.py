import requests
import json

# Global variables
wax_interval = 300
drip_interval = 100
config_file = 'config.json'
bikes = []  # List to keep bikes in memory
base_url = "https://www.strava.com/api/v3/"

# Function to setup OAuth connection with Strava
def setup_oauth():
    # Your Strava application details
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    authorization_code = 'YOUR_AUTH_CODE'

    # Exchange authorization_code for a refresh token and access token
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code"
        }
    )
    return response.json()

# Function to setup config file and Strava connection
def setup():
    token_info = setup_oauth()
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    profile_response = requests.get(base_url + "athlete", headers=headers).json()

    # Add tokens and additional parameters to the profile
    profile_response['refresh_token'] = token_info['refresh_token']

    for bike in profile_response['bikes']:
        bike['waxed_km'] = None
        bike['drip_km'] = None
        bike['wax_state'] = None

    with open(config_file, 'w') as f:
        json.dump(profile_response, f)

    return profile_response

def showBikes():
    try:
        with open(config_file, 'r') as f:
            profile = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        profile = setup()

    print(f"{profile['firstname']} {profile['lastname']}")
    
    global bikes
    bikes = profile['bikes']

    # Updating bike distances from Strava
    headers = {"Authorization": f"Bearer {profile['access_token']}"}
    profile_response = requests.get(base_url + "athlete", headers=headers).json()
    
    for bike in bikes:
        for updated_bike in profile_response['bikes']:
            if bike['id'] == updated_bike['id']:
                bike['distance'] = updated_bike['distance']
                
                wax_state = "OK"
                
                if bike['drip_km']:
                    if bike['distance'] - bike['drip_km'] > drip_interval:
                        wax_state = "Drip Wax Please"
                
                if bike['waxed_km']:
                    if bike['distance'] - bike['drip_km'] > drip_interval:
                        wax_state = "Drip Wax Please"
                    if bike['distance'] - bike['waxed_km'] > wax_interval:
                        wax_state = "Wax Please"
                
                bike['wax_state'] = wax_state

    with open(config_file, 'w') as f:
        json.dump(profile, f)

    print("Bike Table:")
    print("BikeNumber, Name, Distance, Waxed-km, Drip-km, Wax State")
    for idx, bike in enumerate(bikes):
        print(f"{idx}, {bike['name']}, {bike['distance']}, {bike['waxed_km']}, {bike['drip_km']}, {bike['wax_state']}")

def dripped():
    showBikes()

    bike_number = int(input("Enter the bike number you want to 'drip': "))

    if 0 <= bike_number < len(bikes):
        bikes[bike_number]['drip_km'] = bikes[bike_number]['distance']

        with open(config_file, 'w') as f:
            json.dump(profile, f)

        showBikes()
    else:
        print("Invalid bike number!")

if __name__ == "__main__":
    showBikes()
