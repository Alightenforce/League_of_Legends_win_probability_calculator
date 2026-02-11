import requests
import os
import regex as re
from dotenv import load_dotenv
import json
import time

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

def get_link_for_puuid(summoner_name : str, summoner_tag : str, region : str) -> str:
    return f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}?api_key={API_KEY}"

def get_link_for_region(puuid : str, region : str) -> str:
    return f"https://{region}.api.riotgames.com/riot/account/v1/region/by-game/lol/by-puuid/{puuid}?api_key={API_KEY}"

def get_link_for_player_match_history(puuid : str, region : str, count : int) -> str:
    return f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={API_KEY}"

def get_variable_from_link(link : str, variable : str) -> str:
    page = requests.get(link)
    page_json = json.loads(page.content)
    return_variable = page_json[variable]
    return return_variable

def match_history_as_list(match_history_link : str) -> list:
    page = requests.get(match_history_link)
    page_json = json.loads(page.content)
    return page_json

def get_each_match_data_for_player(match_history : list, puuid : str, region : str) -> list[list]:
    match_data = []
    #bad_match_tracker = 0
    session = requests.Session()
    for match in match_history:
        participant_ID = 0
        link = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match}?api_key={API_KEY}"
        page = session.get(link)
        page_json = json.loads(page.content)
        participants_in_current_match_list = page_json["metadata"]["participants"]
        for participant_puuid in participants_in_current_match_list:
            if participant_puuid == puuid:
                break
            participant_ID += 1
        else:
            raise ValueError("Could not find player with puuid")
        match_data.append(page_json["info"]["participants"][participant_ID])
        time.sleep(1.21)
        #bad_match_tracker = bad_match_tracker + 1
        #print(match_data)
        #print (bad_match_tracker)
    return match_data

def calculate_win_rate(each_match_data : list, summoner_name : str, count : int) -> str:
    wins = 0
    losses = 0

    for each_match in each_match_data:
        if each_match["win"]:
            wins += 1
        else:
            losses += 1
    win_rate = wins / len(each_match_data)
    win_rate_percent = win_rate * 100
    return f"{summoner_name}'s winrate is: {win_rate_percent:.2f}% over {count} matches"

def main():
    summoner_name = "Alightenforce"
    summoner_tag = "4040"
    region = "europe"
    count = 5

    link_uuid = get_link_for_puuid(summoner_name, summoner_tag, region)
    puuid = get_variable_from_link(link_uuid, "puuid")
    print(puuid)

    link_region = get_link_for_region(puuid, region)
    region_code = get_variable_from_link(link_region, "region")
    print(region_code)

    match_history_link = get_link_for_player_match_history(puuid, region, count)
    match_history = match_history_as_list(match_history_link)
    each_match_data = get_each_match_data_for_player(match_history, puuid, region)
    print(calculate_win_rate(each_match_data, summoner_name, count))

if __name__ == "__main__":
    main()