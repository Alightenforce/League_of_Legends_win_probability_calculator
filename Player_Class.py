from turtledemo.sorting_animate import start_ssort

import requests
import os
from dotenv import load_dotenv
import json
import time
import climage
from PIL import Image
from io import BytesIO
from Riot_API import Riot_API
from pyarrow.types import is_unicode

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

class Player:

    def __init__(self, summoner_name, summoner_tag, region, count):
        self.puuid = None
        self.region_code = None
        self.summoner_level = None
        self.pfp_id = None

        self.version_number = None
        self.champion_lookup = None
        self.match_data = None

        self.api = Riot_API()

        self.summoner_name = summoner_name
        self.summoner_tag = summoner_tag
        self.region = region
        self.count = count

    def update_profile(self):
        self.puuid = self.api.get_account_data(self.region, self.summoner_name, self.summoner_tag)["puuid"]
        self.region_code = self.api.get_region_data(self.region, self.puuid)["region"]
        data = self.api.get_summoner_data(self.region_code, self.puuid)
        self.summoner_level = data["summonerLevel"]
        self.pfp_id = data["profileIconId"]
        self.version_number = self.api.get_most_recent_version()

    def fetch_champion_lookup(self):
        if self.champion_lookup is None:
            self.champion_lookup = self.api.get_champion_data(self.version_number)
        return self.champion_lookup

    def fetch_match_data(self):
        if self.match_data is None:
            self.match_data = self.get_player_stats_from_previous_matches()
        return self.match_data

    def print_player_data(self):
        print(f"PUUID: {self.puuid}")
        print(f"Level: {self.summoner_level}")
        print(f"Name: {self.summoner_name}")
        print(f"Tag: {self.summoner_tag}")
        print(f"Region: {self.region}")
        print(f"Region Code: {self.region_code}")
        print(f"Profile Picture ID: {self.pfp_id}")
        print(f"Count: {self.count}")
        print(f"Version Number: {self.version_number}")

    ###################################################### Win Rate ##########################################################

    def get_player_stats_from_previous_matches(self):
        data = self.api.get_match_ids(self.region, self.puuid, self.count)
        each_match_data_for_player = self.get_each_match_data_for_player(data)
        return each_match_data_for_player

    def get_win_rate(self):
        each_match_data_for_player = self.get_player_stats_from_previous_matches()
        winrate = self.calculate_win_rate(each_match_data_for_player)
        return winrate

    def get_each_match_data_for_player(self, match_history: list) -> list[list]:
        match_data = []
        for match_id in match_history:
            participant_id = 0
            data = self.api.get_match_detail(self.region, match_id)
            participants_in_current_match_list = data["metadata"]["participants"]
            for participant_puuid in participants_in_current_match_list:
                if participant_puuid == self.puuid:
                    break
                participant_id += 1
            else:
                raise ValueError("Could not find player with puuid")
            match_data.append(data["info"]["participants"][participant_id])
            # time.sleep(1.21) # CAN BE REMOVED BELOW A COUNT OF 20
            # bad_match_tracker = bad_match_tracker + 1
        return match_data

    def calculate_win_rate(self, each_match_data: list) -> float:
        wins = 0
        losses = 0
        for each_match in each_match_data:
            if each_match["win"]:
                wins += 1
            else:
                losses += 1
        win_rate = wins / len(each_match_data)
        win_rate_percent = win_rate * 100
        return round(win_rate_percent, 2)

    def print_win_rate(self):
        print("--------------------")
        print("Player's winrate: ")
        print(f"{self.summoner_name}'s win rate is {self.get_win_rate()}% over the past {self.count} matches")
        print("--------------------")

###################################################### Win Rate ##########################################################

###################################################### Mastery ##########################################################
    # Dictionary uses O(1) over a list which would use O(n)
    def find_champion_ids_to_names(self) -> dict:
        dict_of_champion_ids_to_names = {}
        data = self.api.get_champion_data(self.version_number)
        all_champion_names = data["data"]
        for champion in all_champion_names.values():
            dict_of_champion_ids_to_names[int((champion["key"]))] = champion["name"]
        return dict_of_champion_ids_to_names

    def get_all_champion_masteries(self) -> list:
        list_of_champion_masteries = []
        data = self.api.get_mastery_data(self.region_code, self.puuid)
        for champion in data:
            id_to_mastery = ((champion["championId"]), (champion["championPoints"]))
            list_of_champion_masteries.append(id_to_mastery)
        return list_of_champion_masteries

    def match_champion_name_to_champion_mastery(self, list_of_champion_masteries : list, dict_of_champion_ids_to_names : dict) -> dict:
        champion_name_to_champion_mastery = {}
        for champion_id_mastery, mastery_points in list_of_champion_masteries:
            if champion_id_mastery in dict_of_champion_ids_to_names:
                champion_name = (dict_of_champion_ids_to_names[champion_id_mastery])
                champion_name_to_champion_mastery[champion_name] = mastery_points
        return champion_name_to_champion_mastery

    def get_champion_name_to_champion_mastery(self) -> dict:
        list_of_champion_masteries = self.get_all_champion_masteries()
        dictionary_of_champion_ids_and_names = self.find_champion_ids_to_names()
        name_to_mastery_points = self.match_champion_name_to_champion_mastery(list_of_champion_masteries, dictionary_of_champion_ids_and_names)
        return name_to_mastery_points

    def print_champion_name_to_champion_mastery(self):
        print("--------------------")
        print("All player's mastery: ")
        for name, points in self.get_champion_name_to_champion_mastery().items():
            print(f"{name}: {points}")
        print("--------------------")

###################################################### Mastery ##########################################################

###################################################### Live Match ##########################################################
    def get_champion_in_current_match(self) -> str:
        data = self.api.get_active_game(self.region_code, self.puuid)
        participants = data["participants"]
        for participant in participants:
            if self.puuid == participant["puuid"]:
                current_champion_id = participant["championId"]
                dict_of_champions = self.find_champion_ids_to_names()
                return dict_of_champions[current_champion_id]
        return ("Could not find champion in current match")

    def get_banned_champions_in_current_match(self) -> list:
        list_of_banned_champions_in_current_match = []
        data = self.api.get_active_game(self.region_code, self.puuid)
        banned_champions = data["bannedChampions"]
        for champions in banned_champions:
            champion_id_to_team = ((champions["championId"]), (champions["teamId"]))
            list_of_banned_champions_in_current_match.append(champion_id_to_team)
        return list_of_banned_champions_in_current_match

    def match_banned_champion_id_to_name(self, list_of_banned_champions_in_current_match : list) -> dict:
        BLUE_SIDE_ID = 100
        RED_SIDE_ID = 200
        dict_of_champions = self.find_champion_ids_to_names()
        bans_dict = {
            "blue_side" : [],
            "red_side" : []
        }
        for champion_id, team_id in list_of_banned_champions_in_current_match:
            if champion_id == -1:
                champion_name = "No ban"
            else:
                champion_name = dict_of_champions[champion_id]
            if team_id == BLUE_SIDE_ID:
                bans_dict["blue_side"].append(dict_of_champions[champion_id])
            elif team_id == RED_SIDE_ID:
                bans_dict["red_side"].append(dict_of_champions[champion_id])
            else:
                raise ValueError("Team ID not found")
        return bans_dict

    def print_side_bans(self):
        current_banned_champions_ids = self.get_banned_champions_in_current_match()
        blue_and_red_side_champion_name_bans = self.match_banned_champion_id_to_name(current_banned_champions_ids)
        blue_side = blue_and_red_side_champion_name_bans["blue_side"]
        red_side = blue_and_red_side_champion_name_bans["red_side"]

        print("Blue side bans:")
        for champion in blue_side:
            print(champion)
        print ("")
        print("Red side bans:")
        for champion in red_side:
            print(champion)

###################################################### Live Match ##########################################################

###################################################### Champion Specific ##########################################################

    def get_player_stats_per_champion(self) -> dict[any, any]:
        dict_of_player_stats_per_champion = {}
        if self.match_data is None:
            self.fetch_match_data()
        each_match_data = self.match_data

        for each_match in each_match_data:
            champion_name = each_match["championName"]
            kills = each_match["kills"]
            deaths = each_match["deaths"]
            assists = each_match["assists"]
            win = each_match["win"]
            if champion_name not in dict_of_player_stats_per_champion:
                dict_of_player_stats_per_champion[champion_name] = {"Wins" : 0, "Losses" : 0, "Kills" : 0, "Deaths" : 0, "Assists" : 0, "Games" : 0}
            if win:
                dict_of_player_stats_per_champion[champion_name]["Wins"] += 1
            else:
                dict_of_player_stats_per_champion[champion_name]["Losses"] += 1
            dict_of_player_stats_per_champion[champion_name]["Kills"] += kills
            dict_of_player_stats_per_champion[champion_name]["Deaths"] += deaths
            dict_of_player_stats_per_champion[champion_name]["Assists"] += assists
            dict_of_player_stats_per_champion[champion_name]["Games"] += 1
        return dict_of_player_stats_per_champion

    def calculate_win_rate_per_champion(self) -> dict:
        win_rate_per_champion = {}
        player_stats_per_champion = self.get_player_stats_per_champion()
        for name, stats in player_stats_per_champion.items():
            wins = stats["Wins"]
            games = stats["Games"]
            win_rate = wins / games
            win_rate_per_champion[name] = {"Win_Rate" : round(win_rate * 100, 2), "Total_Matches" : games}
        return win_rate_per_champion

    def print_win_rate_per_champion(self):
        win_rate_dict = self.calculate_win_rate_per_champion()
        print(f"{self.summoner_name}'s win rate per champion over the last {self.count} games):")
        for champion_name, data in win_rate_dict.items():
            print(f"{champion_name}: {data['Win_Rate']}% over {data['Total_Matches']} game(s)")

    def get_average_kda_per_champion(self) -> dict:
        average_kda_per_champion = {}
        player_stats_per_champion = self.get_player_stats_per_champion()
        for name, stats in player_stats_per_champion.items():
            kills = stats["Kills"]
            deaths = stats["Deaths"]
            assists = stats["Assists"]
            games = stats["Games"]

            if deaths == 0:
                deaths = 1

            avg_kills = round((kills / games), 1)
            avg_deaths = round((deaths / games), 1)
            avg_assists = round((assists / games), 1)
            avg_kda = round((avg_kills + avg_assists) / avg_deaths, 1)

            average_kda_per_champion[name] = {"Avg_Kills" : avg_kills, "Avg_Deaths" : avg_deaths, "Avg_Assists" : avg_assists, "Avg_KDA" : avg_kda}
        return average_kda_per_champion

    def print_average_kda_per_champion(self):
        avg_kda_per_champion = self.get_average_kda_per_champion()
        print(f"{self.summoner_name}'s average KDA per champion over the last {self.count} games):")
        for champion_name, data in avg_kda_per_champion.items():
            print(f"{champion_name}: {data['Avg_KDA']} KDA | {data['Avg_Kills']}/{data['Avg_Deaths']}/{data['Avg_Assists']}")
###################################################### Champion Specific ##########################################################

    def display_summoner_pfp_img(self):
        page = self.api.get_account_data(self.region_code, self.summoner_name, self.summoner_tag)
        img = Image.open(BytesIO(page.content))
        buffer = BytesIO() # Puts it into RAM
        img.save(buffer, format="PNG") # Put image data into virtual container in RAM
        buffer.seek(0) # Move head back to start after writing
        output = climage.convert(buffer, is_unicode=True, width = 40)
        print(output)
