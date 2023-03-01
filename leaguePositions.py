import requests
import pandas as pd
import math
import matplotlib.pyplot as plt
import bisect

# Set the RapidAPI key and headers for requests
api_key = "*insert api key*"
headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': api_key,
}

# Set the API URLs
leagues_from_id = "https://api-football-v1.p.rapidapi.com/v2/leagues/league/" #leagues
leagues_url = "https://api-football-v1.p.rapidapi.com/v2/leagues/country/" #leagues
team_from_id = "https://api-football-v1.p.rapidapi.com/v2/teams/team/" #team
teams_url = "https://api-football-v1.p.rapidapi.com/v2/teams/league/" #team
league_table_url = "https://api-football-v1.p.rapidapi.com/v2/leagueTable/" #league
fixtures_from_team_and_league_url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/team/" #fixtures

def get_api(url):
    '''
    Send a GET request to the specified URL with the RapidAPI headers and return the JSON API response.
    '''
    response = requests.request("GET", url, headers=headers)
    api = response.json().get('api')
    return api

def get_league_standings(country, league_name):
    '''
    Get the league standings for the specified country and league name, and return a Pandas DataFrame with the data.
    '''
    # Get the list of leagues for the specified country
    leagues_list= get_api(str(leagues_url) + country).get('leagues')
    # Get the league IDs for the specified league name
    PL_ids = [league.get('league_id') for league in leagues_list if league.get('name') == league_name][:-1]
    # Get the league tables for each league ID
    tables = list(get_api(league_table_url  + str(id)) for id in PL_ids)
    # Get the season numbers for each league
    seasons = [dict.get('season') for dict in leagues_list if dict.get('name') == league_name][:-1]
    # Extract the team IDs from the standings data for each league
    all_standings = []
    for table in tables:
        standings = [dict.get('team_id') for dict in table.get('standings')[0]]
        all_standings.append(standings)
    # Create a DataFrame with the team IDs as columns and the league IDs as rows
    df = pd.DataFrame(list(map(list, zip(*all_standings))), columns=PL_ids)
    # Add 1 to the index to match the position of the teams in the standings data
    df.index += 1
    return df

def get_first_x_fix(country, league_name, x):
    '''
    Get the outcomes of the first x fixtures for each team in each league for the specified country and league name,
    and return a Pandas DataFrame with the data.
    '''
    # Get the league standings for the specified country and league name
    PL_standings =  get_league_standings(country, league_name)
    # Initialize an empty list to store the fixtures data
    league_fixtures = list()
    # Initialize an empty list to store the team IDs for all teams in all leagues
    all_teams = list()
    # Loop through each league ID and team ID in the league standings DataFrame
    for league
    for league, team, results in league_fixtures:
        first_x_fix.at[league, team] = results

    return first_x_fix


import math
import bisect

class Season():
    def __init__(self, league, team_points, team_final_position):
        self.league = league
        self.team_points = team_points
        self.team_final_position = team_final_position

def get_points_from_games(games_string):
    """
    Function to calculate the points earned from a string of game results (W = win, D = draw)
    :param games_string: (string) String of game results
    :return: (int) Total points earned
    """
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
    """
    Function to get a list of Season objects for a league and number of fixtures
    :param country: (string) Country of the league you want the data from e.g. 'England'
    :param league: (string) Name of the league you want the data from e.g. 'Premier league'
    :param x: (int) Amount of fixtures you want e.g. 5 will give you the first 5 fixtures
    :return: (list) List of Season objects
    """
    seasons_list = list()
    standings = get_league_standings(country, league)
    first_x_fix = get_first_x_fix(country, league, x)
    list_of_leagues = first_x_fix.index
    list_of_teams = first_x_fix.columns
    seasons_leagues = list()
    for league in list_of_leagues:
        api = get_api(leagues_from_id + str(league))
        leagues = api.get('leagues')
        year = leagues[0].get('season')
        bisect.insort(seasons_leagues, (year, league))

    # create Season objects for each league and append to seasons_list
    for _, league in seasons_leagues:
        season = Season("", {}, {})
        season.league = league
        # get points for each team for the first x fixtures
        for team in standings[league]:
            season.team_points[team] = get_points_from_games(first_x_fix.at[league, team])
        # get final position for each team
        for i in standings.index:
            team = standings.at[i, league]
            season.team_final_position[team] = i
        seasons_list.append(season)
    return seasons_list


def get_points_to_ranking(country, league, x, ranking):
    '''
    This function returns a list of tuples that contains information of teams
    that ranked in the given position in the final table of each season of a 
    given league. The tuples contain the season year, the team name, and the 
    number of points the team had after a certain number of fixtures.

    Parameters:
    country (str): Country of the league you want the data from e.g. 'England'
    league (str): Name of the league you want the data from e.g. 'Premier league'
    x (int): Amount of fixtures you want e.g. 5 will give you the first 5 fixtures
    ranking (int): The position in the final table you want e.g. 1 will give you the teams that won 1st place in the league

    Returns:
    list: for each season the team that ended up in the defined ranking with the points they had after 4 GWs
    '''
    # Get the list of seasons for the given league and country
    seasons_list = get_seasons_list(country, league, x)
    # Create an empty list to store the information of the winning teams
    winners = list()
    # Iterate over the seasons in the seasons list
    for season in seasons_list:
        # Get the dictionary of team points and final position in the league
        team_points = season.team_points
        team_final_position = season.team_final_position
        # Iterate over the teams in the team points dictionary
        for team in team_points.keys():
            # Check if the team ended up in the given ranking position
            if team_final_position.get(team) == ranking:
                # Get the league information for the season
                leagues = get_api(leagues_from_id + str(season.league)).get('leagues')
                year = str()
                for league in leagues:
                    if league.get('league_id') == season.league:
                        year = league.get('season')
                # Get the name and points of the team
                club = get_api(team_from_id + str(team)).get('teams')[0].get('name')
                points = season.team_points.get(team)
                # Append the information to the winners list as a tuple
                winners.append((year, club, points))
    return winners


def get_ranking_points_spread_all_seasons(country, league, x):
    '''
    This function returns a dictionary that contains the points spread of each 
    ranking position in the final table of all seasons of a given league. The 
    dictionary keys are the ranking positions and the values are lists that 
    contain the points of the teams that ended up in that ranking position.

    Parameters:
    country (str): Country of the league you want the data from e.g. 'England'
    league (str): Name of the league you want the data from e.g. 'Premier league'
    x (int): Amount of fixtures you want e.g. 5 will give you the first 5 fixtures

    Returns:
    dict: a dictionary that contains the points spread of each ranking position in the final table of all seasons of a given league
    '''
    # Get the list of seasons for the given league and country
    seasons_list = get_seasons_list(country, league, x)
    # Create an empty dictionary to store the points spread information
    ranking_points_spread = dict()
    # Initialize the dictionary keys with the ranking positions
    for i in range(1,21):
        ranking_points_spread[i] = []
    # Iterate over the seasons in the
    
def get_ranking_points_spread_all_seasons(country, league, x):
    """
    Returns the spread of points for each ranking position in all seasons.
    
    :param country: (str) Country of the league you want the data from e.g. 'England'.
    :param league: (str) Name of the league you want the data from e.g. 'Premier league'.
    :param x: (int) Amount of fixtures you want e.g. 5 will give you the first 5 fixtures.
    :return: (dict) A dictionary containing the points spread for each ranking position in all seasons.
    """
    # Get a list of Season objects for the given country and league
    seasons_list = get_seasons_list(country, league, x)
    
    # Initialize an empty dictionary to store the points spread for each ranking position
    ranking_points_spread = dict()
    for i in range(1,21):
        ranking_points_spread[i] = []
        
    # Iterate over each season and extract the team points and final position for each team
    for season in seasons_list:
        team_points = season.team_points
        team_final_position = season.team_final_position
        
        # Iterate over each team and append its points to the corresponding ranking position list
        for team, points in team_points.items():
            rank = team_final_position.get(team)
            ranking_points_spread.get(rank).append(points)
    
    return ranking_points_spread


# Define function to extract position numbers from a list of position strings
def get_positions_num(positions):
    result = []
    for string in positions:
        digits = ''.join(filter(str.isdigit, string))
        result.append(int(digits))
    return result

# Define main function to plot ranking point spreads for all seasons
def plot_ranking_points_spread_all_seasons(country, league, x, positions):
    # Get ranking point spread for all seasons
    ranking_spread_all_season = get_ranking_points_spread_all_seasons(country, league, x)
    # Get position numbers from position strings
    positions_num = get_positions_num(positions)
    # Create dataframe to hold data for multiple line plot
    df = pd.DataFrame({
        'season': ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019'],
        positions[0]: ranking_spread_all_season.get(positions_num[0]),
        positions[1]: ranking_spread_all_season.get(positions_num[1]),
        positions[2]: ranking_spread_all_season.get(positions_num[2]),
        positions[3]: ranking_spread_all_season.get(positions_num[3])
    })
    # Create multiple line plot using data from dataframe
    plt.plot('season', positions[0], data=df, marker='', color='blue', linewidth=2)
    plt.plot('season', positions[1], data=df, marker='', color='red', linewidth=2)
    plt.plot('season', positions[2], data=df, marker='', color='yellow', linewidth=2)
    plt.plot('season', positions[3], data=df, marker='', color='purple', linewidth=2)
    # Add labels and legend to plot
    plt.ylabel('points after 4 games')
    plt.legend()
    # Display plot
    plt.show()

# Call the function with sample arguments
plot_ranking_points_spread_all_seasons('England', 'Premier League', 4, ['17th place', '18th place', '19th place', '20th place'])
