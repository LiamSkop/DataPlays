import requests
import pandas as pd

api_key = "b64fc1b3dcmshed227a3fc11d5dcp1955fcjsnda6d8b64faea"
headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': api_key,
    }

leagues_url = "https://api-football-v1.p.rapidapi.com/v2/leagues/country/" #/country_name
teams_url = "https://api-football-v1.p.rapidapi.com/v2/teams/league/" #/league_id
league_table_url = "https://api-football-v1.p.rapidapi.com/v2/leagueTable/" #/league_id
fixtures_from_team_and_league_url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/team/" #/team_id/league_id

def get_api(url):
    response = requests.request("GET", url, headers=headers)
    api = response.json().get('api')
    return api

def get_league_standings(country, league_name):
    leagues_list= get_api(str(leagues_url) + country).get('leagues')
    PL_ids = [league.get('league_id') for league in leagues_list if league.get('name') == league_name][:-1]
    tables = list(get_api(league_table_url  + str(id)) for id in PL_ids)
    seasons = [dict.get('season') for dict in leagues_list if dict.get('name') == league_name][:-1]
    all_standings = []
    for table in tables:
        standings = [dict.get('team_id') for dict in table.get('standings')[0]]
        all_standings.append(standings)
    df = pd.DataFrame(list(map(list, zip(*all_standings))), columns=PL_ids)
    df.index += 1
    return df

PL_standings =  get_league_standings('England', 'Premier League')

print(PL_standings)
league_fixtures = list()
all_teams = list()
for league in PL_standings.columns:
    for team in PL_standings[team]:
        if team not in all_teams:
            all_teams.append(team)
        fixtures = get_api(fixtures_from_team_and_league_url + str(team) + '/' + str(league)).get('fixtures')
        results = ['W' if ((fixture.get('homeTeam').get('team_id') == team) and (fixture.get('goalsHomeTeam') > fixture.get('goalsAwayTeam'))) or ((fixture.get('awayTeam').get('team_id') == team) and (fixture.get('goalsAwayTeam') > fixture.get('goalsHomeTeam')))
                    else 'D' if (fixture.get('goalsHomeTeam') == fixture.get('goalsAwayTeam'))
                    else 'L' for fixture in fixtures[:4]]
        league_fixtures.append(league, team, results)



first_5_fixtures_per_team_per_league = pd.DataFrame(columns=all_teams, index=PL_standings.columns)

for league, team, results in league_fixtures:
    first_5_fixtures_per_team_per_league

