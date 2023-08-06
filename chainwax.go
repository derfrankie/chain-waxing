package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"sync"

	"golang.org/x/oauth2"
)

const ConfigFileName = "config.json"
const wax_interval = 300
const drip_interval = 100

var stravaOauthConfig = &oauth2.Config{
	RedirectURL:  "http://localhost:8080/callback",
	ClientID:     "YOUR_CLIENT_ID",
	ClientSecret: "YOUR_CLIENT_SECRET",
	Scopes:       []string{"read,activity:read"},
	Endpoint: oauth2.Endpoint{
		AuthURL:  "https://www.strava.com/oauth/authorize",
		TokenURL: "https://www.strava.com/oauth/token",
	},
}
var oauthStateString = "random-state-string"

type Bike struct {
	ID            string `json:"id"`
	Name          string `json:"name"`
	Distance      int    `json:"distance"`
	WaxedKm       *int   `json:"waxed_km"`
	DripKm        *int   `json:"drip_km"`
	WaxState      string `json:"wax_state"`
	ResourceState int    `json:"resource_state"`
}

type AthleteProfile struct {
	// Other athlete fields
	FirstName string `json:"firstname"`
	LastName  string `json:"lastname"`
	Bikes     []Bike `json:"bikes"`
}

type Config struct {
	AthletesProfiles []AthleteProfile
}
type Athlete struct {
	// Other athlete fields
	FirstName string `json:"firstname"`
	LastName  string `json:"lastname"`
}

func LoadConfig() (*Config, error) {
	file, err := os.ReadFile(ConfigFileName)
	if err != nil {
		return nil, err
	}
	var config Config
	err = json.Unmarshal(file, &config)
	return &config, err
}

func SaveConfig(config *Config) error {
	data, err := json.Marshal(config)
	if err != nil {
		return err
	}
	return os.WriteFile(ConfigFileName, data, 0644)
}

func GetAthlete(token *oauth2.Token) (*Athlete, error) {
	client := stravaOauthConfig.Client(context.Background(), token)
	resp, err := client.Get("https://www.strava.com/api/v3/athlete")
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var athlete Athlete
	err = json.NewDecoder(resp.Body).Decode(&athlete)
	if err != nil {
		return nil, err
	}
	return &athlete, nil
}

func handleStravaCallback(w http.ResponseWriter, r *http.Request) {
	state := r.FormValue("state")
	if state != oauthStateString {
		log.Printf("invalid oauth state, expected '%s', got '%s'\n", oauthStateString, state)
		http.Redirect(w, r, "/", http.StatusTemporaryRedirect)
		return
	}

	code := r.FormValue("code")
	token, err := stravaOauthConfig.Exchange(context.Background(), code)
	if err != nil {
		log.Printf("stravaOauthConfig.Exchange() failed with '%s'\n", err)
		http.Redirect(w, r, "/", http.StatusTemporaryRedirect)
		return
	}

	athlete, err := GetAthlete(token)
	if err != nil {
		log.Printf("Failed to get athlete details: %v", err)
		return
	}

	config, err := LoadConfig()
	if err != nil {
		config = &Config{}
	}
	config.Athletes = append(config.Athletes, *athlete)

	err = SaveConfig(config)
	if err != nil {
		log.Printf("Failed to save config: %v", err)
		return
	}

	fmt.Fprintf(w, "Athlete details saved!")
}

func addAccount() {
	http.HandleFunc("/callback", handleStravaCallback)

	url := stravaOauthConfig.AuthCodeURL(oauthStateString)
	fmt.Println("Opening browser for Strava authentication...")
	err := openBrowser(url)
	if err != nil {
		log.Fatalf("Failed to open browser: %v", err)
	}

	// Use WaitGroup to wait for the server to finish processing
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		http.ListenAndServe(":8080", nil)
	}()
	wg.Wait()

	athlete, err := GetAthlete(token)
	if err != nil {
		log.Printf("Failed to get athlete details: %v", err)
		return
	}

	for i := range athlete.Bikes {
		athlete.Bikes[i].WaxedKm = nil
		athlete.Bikes[i].DripKm = nil
		athlete.Bikes[i].WaxState = "OK"
	}

	config, err := LoadConfig()
	if err != nil {
		config = &Config{}
	}
	config.AthletesProfiles = append(config.AthletesProfiles, *athlete)

	err = SaveConfig(config)
	if err != nil {
		log.Printf("Failed to save config: %v", err)
		return
	}

	showBikes()
}

func showBikes() {
	config, err := LoadConfig()
	if err != nil || len(config.AthletesProfiles) == 0 {
		addAccount()
		return
	}

	for _, profile := range config.AthletesProfiles {
		athlete, err := GetAthlete(token) // assuming token is stored & accessible
		if err != nil {
			log.Printf("Failed to get athlete details: %v", err)
			continue
		}
		fmt.Printf("User: %s %s\n", profile.FirstName, profile.LastName)
		for i, bike := range profile.Bikes {
			if bike.DripKm != nil && (bike.Distance-*bike.DripKm) > drip_interval {
				bike.WaxState = "Drip Wax Please"
			}
			if bike.WaxedKm != nil {
				if (bike.Distance - *bike.DripKm) > drip_interval {
					bike.WaxState = "Drip Wax Please"
				}
				if (bike.Distance - *bike.WaxedKm) > wax_interval {
					bike.WaxState = "Wax Please"
				}
			}
			fmt.Printf("%d: %s - %dkm - waxed: %vkm - drip: %vkm - state: %s\n",
				i+1, bike.Name, bike.Distance, bike.WaxedKm, bike.DripKm, bike.WaxState)
		}
	}
}

func dripped() {
	showBikes()
	config, err := LoadConfig()
	if err != nil {
		log.Printf("Failed to load config: %v", err)
		return
	}
	fmt.Print("Enter the bike number you want to drip: ")
	var bikeNum int
	fmt.Scanf("%d", &bikeNum)
	if bikeNum < 1 || bikeNum > len(config.AthletesProfiles[0].Bikes) {
		log.Println("Invalid bike number.")
		return
	}
	bike := &config.AthletesProfiles[0].Bikes[bikeNum-1]
	bike.DripKm = &bike.Distance
	err = SaveConfig(config)
	if err != nil {
		log.Printf("Failed to save config: %v", err)
		return
	}
	showBikes()
}

func openBrowser(url string) error {
	// This opens the default browser, can be improved for cross-platform compatibility
	return exec.Command("open", url).Start()
}

func main() {
	var command string
	flag.StringVar(&command, "cmd", "", "Command to execute")
	flag.Parse()

	switch command {
	case "addAccount":
		addAccount()
	case "showBikes":
		showBikes()
	case "dripped":
		dripped()
	default:
		log.Println("Unknown command:", command)
	}
}
