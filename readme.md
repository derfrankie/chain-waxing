# GravelDeluxe Chain Waxing Assistant

## Description

This tool assists cyclists in keeping track of when their bicycles need chain maintenance. It connects with Strava's API to pull the total distance ridden for each bike, and based on user's input, provides an estimate of when the next chain waxing or drip is due.

## Features

- **OAuth Integration with Strava**: Securely log in using your Strava account.
  
- **Bike Management**:
    - Display all active bikes with their respective distances and maintenance status.
    - Automatically set bikes as "retired" if they're no longer in use or recognized by the Strava API.
    - Revive "retired" bikes if they're back in active use.
  
## Waxing Schedule

The GravelDeluxe Chain Waxing Assistant assists users in managing the maintenance schedule for their bikes, specifically in terms of chain waxing and dripping. The workflow is built on two intervals:

1. **Complete Waxing Interval**: After every `1000 km` (can be adjusted based on your preferences or chain manufacturer's recommendation).
2. **Drip Waxing Interval**: After every `300 km` between complete waxings.

Given these settings, the maintenance flow follows this pattern:

```
Wax → Drip → Drip → Drip → Wax → Drip → ...
```

So, for example, after a complete wax, you'd be prompted for a drip wax post `300 km`, then another after `600 km`, and once more at `900 km`. After `1000 km`, you'd be advised to do a complete wax again, restarting the cycle.

The assistant provides actionable insights:
- It will indicate when the next waxing (either drip or complete) is due.
- If a bike hasn't had its initial waxing, it will advise to do so.
- Bikes without any maintenance data will simply be marked with a "-".

To get the best lifespan and performance from your chain, it's crucial to adhere to the maintenance intervals.

---

## Setup

1. Clone this repository:

```bash
git clone [repository-link]
```

2. Navigate to the directory and install required Python packages:

```bash
cd GravelDeluxe-Chain-Waxing-Assistant
pip install -r requirements.txt
```

3. Use an external file to store your Strava client ID and secret for security:

Create a file named `strava_config.json` in the root directory:

```json
{
    "STRAVA_CLIENT_ID": "Your-Client-ID",
    "STRAVA_CLIENT_SECRET": "Your-Client-Secret"
}
```

4. Run the script:

```bash
python main_script_name.py
```

## Usage

1. When you run the tool, it will prompt you to authenticate with Strava (only on the first run or when the token expires).
2. Once authenticated, you'll see a list of your active bikes, their distances, and their waxing status.
3. Use the displayed information to determine when to perform the next chain maintenance.

## Contributions

Contributions, bug reports, and feature requests are welcome! Open an issue or submit a pull request.

## License

This project is open source, under the [MIT License](LICENSE).

---

Make sure to adjust `[repository-link]` and `main_script_name.py` with the actual link and script name respectively. You can also add any more sections as needed, like "Acknowledgements" or "Changelog".

## Proudly presented by GravelDeluxe

GravelDeluxe is the Europes largest Gravel Route Collection for people who enjoy their gravel bike. With every kind of tracks available, from after work rides to bikepacking events and routes.
Check it out at [GravelDeluxe](https://graveldeluxe.com)