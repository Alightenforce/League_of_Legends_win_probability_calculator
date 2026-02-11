import requests
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

class Player:

    def __init__(self, summoner_name, summoner_tag, region, count, version_number):
        self.puuid = None
        self.region_code = None

        self.summoner_name = summoner_name
        self.summoner_tag = summoner_tag
        self.region = region
        self.count = count
        self.version_number = version_number

        self.set_puuid()
        self.set_region_code()

    def print_player_data(self):
        print(self.puuid)
        print(self.region_code)
        print(self.summoner_name)
        print(self.summoner_tag)
        print(self.region)
        print(self.count)
        print(self.version_number)

    def get_link_for_puuid(self) -> str:
        return f"https://{self.region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self.summoner_name}/{self.summoner_tag}?api_key={API_KEY}"

    def get_link_for_region_code(self) -> str:
        return f"https://{self.region}.api.riotgames.com/riot/account/v1/region/by-game/lol/by-puuid/{self.puuid}?api_key={API_KEY}"

    def get_link_for_player_match_history(self) -> str:
        return f"https://{self.region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.puuid}/ids?start=0&count={self.count}&api_key={API_KEY}"

    def get_link_for_player_mastery(self) -> str:
        return f"https://{self.region_code}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{self.puuid}?api_key={API_KEY}"

    def get_link_for_data_dragon(self) -> str:
        return f"http://ddragon.leagueoflegends.com/cdn/{self.version_number}/data/en_US/champion.json"

    def get_variable_from_link(self, link: str, variable: str) -> str:
        page = requests.get(link)
        page_json = json.loads(page.content)
        return_variable = page_json[variable]
        return return_variable

    def get_puuid_from_link(self, link : str) -> str:
        return self.get_variable_from_link(link, "puuid")

    def set_puuid(self):
        self.puuid = self.get_puuid_from_link(self.get_link_for_puuid())

    def get_region_code_from_link(self, link : str) -> str:
        return self.get_variable_from_link(link, "region")

    def set_region_code(self):
        self.region_code = self.get_region_code_from_link(self.get_link_for_region_code())

    def match_history_as_list(self, match_history_link: str) -> list:
        page = requests.get(match_history_link)
        page_json = json.loads(page.content)
        return page_json

    def get_each_match_data_for_player(self, match_history: list) -> list[list]:
        match_data = []
        # bad_match_tracker = 0
        session = requests.Session()
        for match in match_history:
            participant_id = 0
            link = f"https://{self.region}.api.riotgames.com/lol/match/v5/matches/{match}?api_key={API_KEY}"
            page = session.get(link)
            page_json = json.loads(page.content)
            participants_in_current_match_list = page_json["metadata"]["participants"]
            for participant_puuid in participants_in_current_match_list:
                if participant_puuid == self.puuid:
                    break
                participant_id += 1
            else:
                raise ValueError("Could not find player with puuid")
            match_data.append(page_json["info"]["participants"][participant_id])
            time.sleep(1.21)
            # bad_match_tracker = bad_match_tracker + 1
            # print(match_data)
            # print (bad_match_tracker)
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

    def get_win_rate(self):
        match_history_link = self.get_link_for_player_match_history()
        match_history_as_list = self.match_history_as_list(match_history_link)
        each_match_data_for_player = self.get_each_match_data_for_player(match_history_as_list)
        winrate = self.calculate_win_rate(each_match_data_for_player)
        return winrate

    def print_win_rate(self):
        print("--------------------")
        print("Player's winrate: ")
        print(f"{self.summoner_name}'s win rate is {self.get_win_rate()}% over the past {self.count} matches")
        print("--------------------")

    def get_all_champion_masteries(self, champion_masteries_link : str) -> list:
        list_of_champion_masteries = []
        page = requests.get(champion_masteries_link)
        page_json = json.loads(page.content)
        for champion in page_json:
            id_to_mastery = ((champion["championId"]), (champion["championPoints"]))
            list_of_champion_masteries.append(id_to_mastery)
        return list_of_champion_masteries

    # Dictionary uses O(1) over a list which would use O(n)
    def find_champion_ids_to_names(self, data_dragon_link : str) -> dict:
        dict_of_champion_ids_to_names = {}
        page = requests.get(data_dragon_link)
        page_json = json.loads(page.content)
        all_champion_names = page_json["data"]
        for champion in all_champion_names.values():
            dict_of_champion_ids_to_names[int((champion["key"]))] = champion["name"]
        return dict_of_champion_ids_to_names

    def match_champion_name_to_champion_mastery(self, list_of_champion_masteries : list, dict_of_champion_ids_to_names : dict) -> dict:
        champion_name_to_champion_mastery = {}
        for champion_id_mastery, mastery_points in list_of_champion_masteries:
            if champion_id_mastery in dict_of_champion_ids_to_names:
                champion_name = (dict_of_champion_ids_to_names[champion_id_mastery])
                champion_name_to_champion_mastery[champion_name] = mastery_points
        return champion_name_to_champion_mastery

    def get_champion_name_to_champion_mastery(self) -> dict:
        link_mast = self.get_link_for_player_mastery()
        link_dd = self.get_link_for_data_dragon()

        list1 = self.get_all_champion_masteries(link_mast)
        dict1 = self.find_champion_ids_to_names(link_dd)
        name_to_mastery_points = self.match_champion_name_to_champion_mastery(list1, dict1)
        return name_to_mastery_points

    def print_champion_name_to_champion_mastery(self):
        print("--------------------")
        print("All player's mastery: ")
        for name, points in self.get_champion_name_to_champion_mastery().items():
            print(f"{name}: {points}")
        print("--------------------")
