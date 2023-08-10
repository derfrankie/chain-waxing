######################################################################
##
##    GravelDeluxe Chain Waxing Assistant
##    
##    Keep track of your waxed chains with Strava integration
##
##    Created by https://graveldeluxe.com
##
######################################################################

import requests
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Global variables
wax_interval = 1000  # Interval in km between complete waxing of chain
drip_interval = 300  # Interval in km in between drip waxing (in dry conditions)

config_file = 'config.json'
bikes = []  # List to keep bikes in memory
base_url = "https://www.strava.com/api/v3/"

def load_strava_config():
    with open('strava_config.json', 'r') as file:
        config = json.load(file)
    return config


def setup_oauth():
    strava_config = load_strava_config()
    
    STRAVA_CLIENT_ID = strava_config['STRAVA_CLIENT_ID']
    STRAVA_CLIENT_SECRET = strava_config['STRAVA_CLIENT_SECRET']
    AUTHORIZATION_URL = "http://www.strava.com/oauth/authorize"
    REDIRECT_URI = "http://localhost:8000"
    TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"
    
    auth_code = None
    auth_event = threading.Event()

    class TempServerHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            self.send_response(200, "OK")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            auth_code = self.path.split("code=")[1].split("&")[0]
            #print(f"Auth code received: {auth_code}")
            self.wfile.write(b"Authentication successful. You can close this window/tab.")
            auth_event.set()

        def log_message(self, format, *args):
            return

    httpd = HTTPServer(('localhost', 8000), TempServerHandler)

    threading.Thread(target=httpd.handle_request).start()

    auth_url = f"{AUTHORIZATION_URL}?client_id={STRAVA_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&approval_prompt=force&scope=profile:read_all"
    webbrowser.open(auth_url)

    auth_event.wait()

    if auth_code:
        token_response = requests.post(TOKEN_URL, data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'code': auth_code,
            'grant_type': 'authorization_code'
        })
        #print(token_response.json())
        token_info = token_response.json()
        return token_info

    else:
        print("Authentication failed.")
        return None

# Function to setup config file and Strava connection
def setup():
    token_info = setup_oauth()
        
    # Store the access_token in the profile
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    profile_response = requests.get(base_url + "athlete", headers=headers).json()
    profile_response['access_token'] = token_info['access_token']  # Add this line

    # Add tokens and additional parameters to the profile
    profile_response['refresh_token'] = token_info['refresh_token']
    profile_response['expires_at'] = token_info['expires_at']  # Storing the expiration time

    for bike in profile_response['bikes']:
        bike['waxed_km'] = None
        bike['drip_km'] = None
        bike['wax_state'] = None

    with open(config_file, 'w') as f:
        json.dump(profile_response, f)

    return profile_response

def refresh_token_if_needed(profile):
    
    strava_config = load_strava_config()
    STRAVA_CLIENT_ID = strava_config['STRAVA_CLIENT_ID']
    STRAVA_CLIENT_SECRET = strava_config['STRAVA_CLIENT_SECRET']
    current_time = time.time()
    # If token is expired or will expire in the next minute
    elapsed_time = current_time - float(profile['expires_at'])
    if elapsed_time > 1000:
        TOKEN_URL = "https://www.strava.com/oauth/token"
        refresh_response = requests.post(TOKEN_URL, data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'refresh_token': profile['refresh_token'],
            'grant_type': 'refresh_token'
        })
        new_token_info = refresh_response.json()

        # Update profile with new access and refresh tokens and new expiry
        profile['access_token'] = new_token_info['access_token']
        profile['refresh_token'] = new_token_info['refresh_token']
        profile['expires_at'] = new_token_info['expires_at']

        # Save the updated profile to config.json
        with open(config_file, 'w') as f:
            json.dump(profile, f)
    return profile

def clean_bikes(profile, api_bikes):
    # Extract bike IDs from the API response for quick lookup
    api_bike_ids = {bike['id'] for bike in api_bikes}
    
    for bike in profile['bikes']:
        # If the bike is missing in the latest API response, mark it as retired
        if bike['id'] not in api_bike_ids:
            bike['retired'] = True
        else:
            # If the bike was previously marked as retired but is in the latest response, mark it as not retired
            bike['retired'] = False

    return profile


def showBikes():
    try:
        with open(config_file, 'r') as f:
            profile = json.load(f)
            if not profile or 'bikes' not in profile:
                raise ValueError("Profile is incomplete.")
            profile = refresh_token_if_needed(profile)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        profile = setup()

    print(f"{profile['firstname']} {profile['lastname']}")
    
    global bikes
    bikes = profile['bikes']

    # Updating bike distances from Strava
    headers = {"Authorization": f"Bearer {profile['access_token']}"}
    profile_response = requests.get(base_url + "athlete", headers=headers).json()
    
    profile = clean_bikes(profile, profile_response['bikes'])

    for bike in bikes:
        for updated_bike in profile_response['bikes']:
            if bike['id'] == updated_bike['id']:
                bike['converted_distance'] = updated_bike['converted_distance']
                bike['retired'] = updated_bike['retired']
                
                wax_state = "-"

                # If the bike has been waxed

                drips_per_wax = wax_interval // drip_interval

                if not bike['waxed_km']:
                    wax_state = "Needs Initial Wax"
                else:
                    # Calculate the distance since the last complete wax
                    distance_since_wax = bike['converted_distance'] - bike['waxed_km']

                    # Check if we're due for another complete wax
                    if distance_since_wax >= wax_interval:
                        wax_state = "Wax Please"
                    else:
                        # Calculate the number of drips since the last wax
                        drips_since_wax = distance_since_wax // drip_interval

                        # Check if we're due for another drip
                        if (drips_since_wax * drip_interval) + drip_interval <= distance_since_wax:
                            wax_state = "Drip Wax Please"
                        else:
                            # Calculate the kilometers to the next maintenance event
                            next_drip_at = ((drips_since_wax + 1) * drip_interval) - distance_since_wax
                            if drips_since_wax < drips_per_wax:
                                wax_state = f"{int(next_drip_at)} km to next drip"
                            else:
                                wax_state = f"{int(next_drip_at)} km to next complete wax"

                bike['wax_state'] = wax_state




    with open(config_file, 'w') as f:
        json.dump(profile, f)

    print("Welcome to the GravelDeluxe Chain Wax Assistant")
    header = f"{'NR':<3}{'Name':<20}{'Distance':<10}{'Waxed km':<10}{'Driped km':<10}{'Wax State':<25}"
    print(header)
    print('-' * len(header))  # Print line separator
    
    for idx, bike in enumerate(bikes, 1):
        if not bike.get('retired', False):  # Check if the bike isn't marked as retired
            row = f"{idx:<3}{bike['name']:<20}{bike['converted_distance']:<10}{bike['waxed_km'] if bike['waxed_km'] else 'N/A':<10}{bike['drip_km'] if bike['drip_km'] else 'N/A':<10}{bike['wax_state']:<25}"
            print(row)
    print()

def dripit():
    # Load the profile from the config file
    with open(config_file, 'r') as f:
        profile = json.load(f)

    bike_number = int(input("Enter the bike number you want to 'drip': "))
    if 0 < bike_number <= len(bikes):
        selected_bike = profile['bikes'][bike_number-1]
        selected_bike['drip_km'] = selected_bike['converted_distance']
        with open(config_file, 'w') as f:
            json.dump(profile, f)
        print(f"Drip updated for {selected_bike['name']}.")
    else:
        print("Invalid bike number.")
    showBikes()

def waxit():
    # Load the profile from the config file
    with open(config_file, 'r') as f:
        profile = json.load(f)
    
    bike_number = int(input("Enter the bike number you want to 'wax': "))
    if 0 < bike_number <= len(profile['bikes']):
        selected_bike = profile['bikes'][bike_number-1]
        selected_bike['waxed_km'] = selected_bike['converted_distance']
        # Save updated profile to the config file
        with open(config_file, 'w') as f:
            json.dump(profile, f)
        print(f"'Wax' updated for {selected_bike['name']}.")
    else:
        print("Invalid bike number.")
    showBikes()


def reset():
    # Load the profile from the config file
    with open(config_file, 'r') as f:
        profile = json.load(f)

    bike_number = int(input("Enter the bike number you want to reset 'drip' and 'wax' for: "))
    if 0 < bike_number <= len(bikes):
        selected_bike = profile['bikes'][bike_number-1]
        selected_bike['drip_km'] = None
        selected_bike['waxed_km'] = None
        with open(config_file, 'w') as f:
            json.dump(profile, f)
        print(f"Drip and Wax reset for {selected_bike['name']}.")
    else:
        print("Invalid bike number.")
    showBikes()

def main():

    while True:
        showBikes()
        print("-----------------------------------------------------------------------------")
        print("Choose an action: 1. Drip | 2. Wax | 3. Reset Drip and Wax | 4. Exit")
        
        choice = input().strip()

        if choice == "1":
            dripit()
        elif choice == "2":
            waxit()
        elif choice == "3":
            reset()
        elif choice == "4":
            print("Exiting script.")
            break
        else:
            print("Invalid choice. Please choose a number from 1 to 4.")

if __name__ == "__main__":
    main()

