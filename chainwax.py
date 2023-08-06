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
    client_id = '111266'
    client_secret = '246e2176d0d32be095c8c920e2766aff825a6e1d'
    authorization_code = 'd23ae5943da9eb6e33afd2fe56e19d99be5d5a4f'

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
    print(response.json())  # Print the response
    return response.json()

# Function to setup config file and Strava connection
def setup():
    token_info = setup_oauth()
    
    # Store the access_token in the profile
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    profile_response = requests.get(base_url + "athlete", headers=headers).json()
    profile_response['access_token'] = token_info['access_token']  # Add this line

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
            if not profile or 'bikes' not in profile:
                raise ValueError("Profile is incomplete.")
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
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
                bike['converted_distance'] = updated_bike['converted_distance']
                
                wax_state = "OK"
                
                if bike['drip_km']:
                    if bike['converted_distance'] - bike['drip_km'] > drip_interval:
                        wax_state = "Drip Wax Please"
                
                if bike['waxed_km']:
                    if bike['converted_distance'] - bike['converted_distance'] > drip_interval:
                        wax_state = "Drip Wax Please"
                    if bike['converted_distance'] - bike['waxed_km'] > wax_interval:
                        wax_state = "Wax Please"
                
                bike['wax_state'] = wax_state

    with open(config_file, 'w') as f:
        json.dump(profile, f)

    print("Bike Table:")
    header = f"{'Bike Number':<12}{'Name':<20}{'Distance':<10}{'Waxed KM':<10}{'Drip KM':<10}{'Wax State':<15}"
    print(header)
    print('-' * len(header))  # Print line separator
    
    for idx, bike in enumerate(bikes, 1):
        row = f"{idx:<12}{bike['name']:<20}{bike['converted_distance']:<10}{bike['waxed_km'] if bike['waxed_km'] else 'N/A':<10}{bike['drip_km'] if bike['drip_km'] else 'N/A':<10}{bike['wax_state']:<15}"
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

