# DataPlays

This repository contains a Python script that allows you to extract and analyze data from the [API-Football API](https://rapidapi.com/api-sports/api/api-football). Specifically, it allows you to retrieve league standings and team fixtures for a given league and country, and analyze the outcomes of the first x fixtures for each team in the league.

## Requirements
To use this script, you need to have a RapidAPI key, which you can obtain by signing up for a [RapidAPI account](https://rapidapi.com/auth/sign-up). You also need to have the following Python libraries installed:

- `requests`
- `pandas`
- `matplotlib`


## Usage
1. Clone the repository:
`git clone https://github.com/{USERNAME}/{REPOSITORY_NAME}.git`
2. Install the required Python libraries:
`pip install -r requirements.txt`
3. Open the script in your Python editor of choice.
4. Insert your RapidAPI key in the api_key variable.
`api_key = "*insert api key*"`
5. Customize the following variables according to your needs:
`country = "England"
league_name = "Premier League"
x = 5
`
- `country`: the name of the country of the league you want to analyze
- `league_name`: the name of the league you want to analyze
- `x`: the number of fixtures you want to analyze

6. Run the script.

## Functions

The following functions are included in the script:

- `get_api(url)`: Sends a GET request to the specified URL with the RapidAPI headers and returns the JSON API response.

- `get_league_standings(country, league_name)`: Gets the league standings for the specified country and league name, and returns a Pandas DataFrame with the data.

- `get_first_x_fix(country, league_name, x)`: Gets the outcomes of the first x fixtures for each team in the specified league and country, and returns a Pandas DataFrame with the data.

- `get_points_from_games(games_string)`: Calculates the points earned from a string of game results (W = win, D = draw).

- `get_seasons_list(country, league, x)`: Gets a list of Season objects for a league and number of fixtures. Each Season object contains the league, team points, and team final position for the specified number of fixtures.

## Example

`
import requests
import pandas as pd
import math
import matplotlib.pyplot as plt
import bisect
`

` \# Set the RapidAPI key and headers for requests
api_key = "*insert api key*"
headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': api_key,
} `

` \# Set the API URLs
leagues_from_id = "https://api-football-v1.p.rapidapi.com/v2/leagues/league/" #leagues
leagues_url = "https://api-football-v1.p.rapidapi.com/v2/leagues/country/" #leagues
team_from_id = "https://api-football-v1.p.rapidapi.com/v2/teams/team/" #team
teams_url = "https://api-football-v1.p.rapidapi.com/v2/teams/league/" #team
league_table_url = "https://api-football-v1.p.rapidapi.com/v2/leagueTable/" #league
fixtures_from_team_and_league_url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/team/" #fixtures
` 

` def get_api(url):
    \# Calculate the team's final position in the league based on their total points
    team_final_position = sorted(team_points, reverse=True).index(points) + 1
    
    \# Create a Season object and add it to the list of seasons
    season = Season(league, team_points, team_final_position)
    seasons_list.append(season)

return seasons_list
`
