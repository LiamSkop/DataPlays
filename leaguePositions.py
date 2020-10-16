import requests
import pandas as pd

import math
import matplotlib.pyplot as plt
import bisect

api_key = "*insert api key*"
headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': api_key,
    }
leagues_from_id = "https://api-football-v1.p.rapidapi.com/v2/leagues/league/" #league_id
leagues_url = "https://api-football-v1.p.rapidapi.com/v2/leagues/country/" #/country_name
team_from_id = "https://api-football-v1.p.rapidapi.com/v2/teams/team/" #team_id
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


def get_first_x_fix(country, league_name, x):

    '''
    :param country: (string) Country of the league you would like the fixtures from e.g. 'England'
    :param league_name: (string) Name of the league you would like the fixtures from e.g. 'Premier League'
    :param x: (int) amount of fixtures you want e.g. 5 will give you the first 5 fixtures
    :return: (DataFrame) table of the outcomes of the first x amount of fixtures for each league(rows) per team(columns)
    '''

    PL_standings =  get_league_standings(country, league_name)
    league_fixtures = list()
    all_teams = list()
    for league in PL_standings.columns:
        for team in PL_standings[league]:
            if team not in all_teams:
                all_teams.append(team)
            fixtures = get_api(fixtures_from_team_and_league_url + str(team) + '/' + str(league)).get('fixtures')
            results = ['W' if ((fixture.get('homeTeam').get('team_id') == team) and (fixture.get('goalsHomeTeam') > fixture.get('goalsAwayTeam'))) or ((fixture.get('awayTeam').get('team_id') == team) and (fixture.get('goalsAwayTeam') > fixture.get('goalsHomeTeam')))
                        else 'D' if (fixture.get('goalsHomeTeam') == fixture.get('goalsAwayTeam'))
                        else 'L' for fixture in fixtures[:x]]
            league_fixtures.append((league, team, results))

    first_x_fix = pd.DataFrame(columns=all_teams, index=PL_standings.columns)

    for league, team, results in league_fixtures:
        first_x_fix.at[league, team] = results

    return first_x_fix


class Season():
    def __init__(self, league, team_points, team_final_position):
        self.league = league
        self.team_points = team_points
        self.team_final_position = team_final_position

def get_points_from_games(games_string):
    try:
        if math.isnan(games_string):
            return -1
    except TypeError:
        points = 0
        for r in games_string:
            if r == 'W':
                points += 3
            if r == 'D':
                points += 1
        return points

def get_seasons_list(country, league, x):
    seasons_list = list()
    standings = get_league_standings(country, league)
    first_x_fix = get_first_x_fix(country, league, x)
    list_of_leagues = first_x_fix.index
    list_of_teams = first_x_fix.columns
    seasons_leagues = list()
    for league in list_of_leagues:
        api = get_api(leagues_from_id + str(league))
        print(api)
        leagues = api.get('leagues')
        year = leagues[0].get('season')
        bisect.insort(seasons_leagues, (year, league))

    print(seasons_leagues)
    for _, league in seasons_leagues:
        season = Season("", {}, {})
        season.league = league
        for team in standings[league]:
            season.team_points[team] = get_points_from_games(first_x_fix.at[league, team])
        for i in standings.index:
            team = standings.at[i, league]
            season.team_final_position[team] = i
        seasons_list.append(season)
    return seasons_list


def get_points_to_ranking(country, league, x, ranking):
    '''
    :param country: (string) Country of the league you want the data from e.g. 'England'
    :param league: (string) Name of the league you want the data from e.g. 'Premier league'
    :param x: (int) Amount of fixtures you want e.g. 5 will give you the first 5 fixtures
    :param ranking: (int) The position in the final table you want e.g. 1 will give you the teams that won 1st place in the league
    :return: (list) for each season the team that ended up in the defined ranking with the points they had after 4 GWs
    '''
    seasons_list = get_seasons_list(country, league, x)
    winners = list()
    for season in seasons_list:
        team_points = season.team_points
        team_final_position = season.team_final_position
        for team in team_points.keys():
            if team_final_position.get(team) == ranking:
                leagues = get_api(leagues_from_id + str(season.league)).get('leagues')
                year = str()
                for league in leagues:
                    if league.get('league_id') == season.league:
                        year = league.get('season')
                club = get_api(team_from_id + str(team)).get('teams')[0].get('name')
                points = season.team_points.get(team)
                winners.append((year, club, points))
    return winners

def get_ranking_points_spread_all_seasons(country, league, x):
    seasons_list = get_seasons_list(country, league, x)
    ranking_points_spread = dict()
    for i in range(1,21):
        ranking_points_spread[i] = []
    for season in seasons_list:
        team_points = season.team_points
        team_final_position = season.team_final_position
        for team, points in team_points.items():
            rank = team_final_position.get(team)

            ranking_points_spread.get(rank).append(points)
    return ranking_points_spread

def plot_ranking_points_spread_all_seasons(country, league, x, positions, positions_num):

    ranking_spread_all_season = get_ranking_points_spread_all_seasons(country, league, x)
    # Data
    df = pd.DataFrame({'season': ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019'], positions[0] : ranking_spread_all_season.get(positions_num[0]), positions[1] : ranking_spread_all_season.get(positions_num[1]),
                       positions[2] : ranking_spread_all_season.get(positions_num[2]), positions[3] : ranking_spread_all_season.get(positions_num[3])})

    # multiple line plot
    plt.plot('season', positions[0], data=df, marker='', color='blue', linewidth=2)
    plt.plot('season', positions[1], data=df, marker='', color='red', linewidth=2)
    plt.plot('season', positions[2], data=df, marker='', color='yellow', linewidth=2)
    plt.plot('season', positions[3], data=df, marker='', color='purple', linewidth=2)
    plt.ylabel('points after 4 games')
    plt.legend()
    plt.show()
    
plot_ranking_points_spread_all_seasons('England', 'Premier League', 4, ['17th place', '18th place', '19th place', '20th place'], [17,18, 19, 20])
