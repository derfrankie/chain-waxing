package main

import (
	"flag"
	"fmt"
	"log"
)

type Bike struct {
	ID         string `json:"id"`
	Primary    bool   `json:"primary"`
	Name       string `json:"name"`
	Distance   int    `json:"distance"`
	WaxedKm    *int   `json:"waxed_km"`
	DripKm     *int   `json:"drip_km"`
	WaxState   string `json:"wax_state"`
	BikeNumber int    `json:"bike_number"` // this will be populated at runtime
}

type Account struct {
	Name     string  `json:"name"`
	Token    string  `json:"token"`
	Username string  `json:"username"`
	Password string  `json:"password"` // It's generally not recommended to store passwords in plaintext
	Athlete  Athlete `json:"athlete"`
}

func addAccount() {
	fmt.Print("Enter Strava username: ")
	var username string
	fmt.Scan(&username)

	fmt.Print("Enter Strava password: ") // Ideally use a method that hides input
	var password string
	fmt.Scan(&password)

	// TODO: You need to integrate Strava OAuth to get the token using these credentials.
	// For the sake of this example, let's use a placeholder token.
	token := "a18baab2fa81698d34c1b742597165b845058722"

	athlete, err := GetAthlete(token)
	if err != nil {
		log.Fatalf("Failed to get athlete data: %v", err)
	}

	config, err := LoadConfig()
	if err != nil {
		// handle error
	}

	account := Account{
		Name:     athlete.Firstname + " " + athlete.Lastname,
		Token:    token,
		Username: username,
		Password: password,
		Athlete:  *athlete,
	}

	for _, bike := range account.Athlete.Bikes {
		bike.WaxedKm = nil
		bike.DripKm = nil
		bike.WaxState = "OK"
	}

	config.Accounts = append(config.Accounts, account)
	SaveConfig(config)

	showBikes()
}

func showBikes() {
	config, err := LoadConfig()
	if err != nil {
		log.Fatalf("Config load error: %v", err)
	}

	if len(config.Accounts) == 0 {
		addAccount()
		return
	}

	for _, account := range config.Accounts {
		fmt.Printf("\n%s's Bikes:\n", account.Name)
		fmt.Println("Number\tName\tDistance\tWaxedKm\tDripKm\tState")
		for i, bike := range account.Athlete.Bikes {
			bike.BikeNumber = i + 1
			if bike.DripKm != nil && (bike.Distance-*bike.DripKm) > drip_interval {
				bike.WaxState = "Drip Wax Please"
			}
			if bike.WaxedKm != nil {
				if (bike.Distance - *bike.WaxedKm) > wax_interval {
					bike.WaxState = "Wax Please"
				} else if (bike.Distance - *bike.DripKm) > drip_interval {
					bike.WaxState = "Drip Wax Please"
				}
			}
			fmt.Printf("%d\t%s\t%d\t%d\t%d\t%s\n", bike.BikeNumber, bike.Name, bike.Distance, *bike.WaxedKm, *bike.DripKm, bike.WaxState)
		}
	}
}

func dripped() {
	showBikes()

	fmt.Print("\nEnter the bike number you want to 'drip': ")
	var bikeNum int
	fmt.Scan(&bikeNum)

	config, err := LoadConfig()
	if err != nil {
		log.Fatalf("Config load error: %v", err)
	}

	for _, account := range config.Accounts {
		for i, bike := range account.Athlete.Bikes {
			if bike.BikeNumber == bikeNum {
				bike.DripKm = &bike.Distance
				SaveConfig(config)
				break
			}
		}
	}

	showBikes()
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
