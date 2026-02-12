import requests
import os
from dotenv import load_dotenv
import json
import time
import climage
from PIL import Image
from io import BytesIO

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

        self.summoner_name = summoner_name
        self.summoner_tag = summoner_tag
        self.region = region
        self.count = count

        self.set_puuid()
        self.set_region_code()
        self.set_summoner_level()
        self.set_pfp_icon()
        self.set_version_number()

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

    def get_link_for_summoner_profile(self) -> str:
        return f"https://{self.region_code}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{self.puuid}?api_key={API_KEY}"

    def get_link_for_live_match(self):
        return f"https://{self.region_code}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{self.puuid}?api_key={API_KEY}"

    def get_link_for_version_number(self):
        return f"https://ddragon.leagueoflegends.com/api/versions.json"

    def get_most_recent_version(self, link_for_version_number : str):
        page = requests.get(link_for_version_number)
        page_json = json.loads(page.content)
        most_recent_version = page_json[0]
        return most_recent_version

    def set_version_number(self):
        self.version_number = self.get_most_recent_version(self.get_link_for_version_number())

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
            time.sleep(1.21) # CAN BE REMOVED BELOW A COUNT OF 20
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

    def get_player_stats_from_previous_matches(self):
        match_history_link = self.get_link_for_player_match_history()
        match_history_as_list = self.match_history_as_list(match_history_link)
        each_match_data_for_player = self.get_each_match_data_for_player(match_history_as_list)
        return each_match_data_for_player

    def get_win_rate(self):
        each_match_data_for_player = self.get_player_stats_from_previous_matches()
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

        list_of_champion_masteries = self.get_all_champion_masteries(link_mast)
        dictionary_of_champion_ids_and_names = self.find_champion_ids_to_names(link_dd)
        name_to_mastery_points = self.match_champion_name_to_champion_mastery(list_of_champion_masteries, dictionary_of_champion_ids_and_names)
        return name_to_mastery_points

    def print_champion_name_to_champion_mastery(self):
        print("--------------------")
        print("All player's mastery: ")
        for name, points in self.get_champion_name_to_champion_mastery().items():
            print(f"{name}: {points}")
        print("--------------------")

    def get_summoner_level(self, link_for_summoner : str):
        return self.get_variable_from_link(link_for_summoner, "summonerLevel")

    def set_summoner_level(self):
        self.summoner_level = self.get_summoner_level(self.get_link_for_summoner_profile())

    def get_summoner_pfp_id(self, link_for_summoner : str):
        return self.get_variable_from_link(link_for_summoner, "profileIconId")

    def set_pfp_icon(self):
        self.pfp_id = self.get_summoner_pfp_id(self.get_link_for_summoner_profile())

    def get_summoner_pfp_img(self, link_for_summoner : str):
        pfp_id = self.get_summoner_pfp_id(link_for_summoner)
        page = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{self.version_number}/img/profileicon/{pfp_id}.png")
        return page

    def display_summoner_pfp_img(self):
        page = self.get_summoner_pfp_img(self.get_link_for_summoner_profile())
        img = Image.open(BytesIO(page.content))
        buffer = BytesIO() # Puts it into RAM
        img.save(buffer, format="PNG") # Put image data into virtual container in RAM
        buffer.seek(0) # Move head back to start after writing
        output = climage.convert(buffer, is_unicode=True, width = 40)
        print(output)

    def get_champion_in_current_match(self, link_for_live_match : str) -> str:
        page = requests.get(link_for_live_match)
        page_json = json.loads(page.content)
        participants = page_json["participants"]
        for participant in participants:
            if self.puuid == participant["puuid"]:
                current_champion_id = participant["championId"]
                dict_of_champions = self.find_champion_ids_to_names(self.get_link_for_data_dragon())
                return dict_of_champions[current_champion_id]
        return ("Could not find champion in current match")

    def get_banned_champions_in_current_match(self, link_for_live_match : str) -> list:
        list_of_banned_champions_in_current_match = []
        page = requests.get(link_for_live_match)
        page_json = json.loads(page.content)
        banned_champions = page_json["bannedChampions"]
        for champions in banned_champions:
            champion_id_to_team = ((champions["championId"]), (champions["teamId"]))
            list_of_banned_champions_in_current_match.append(champion_id_to_team)
        return list_of_banned_champions_in_current_match

    def match_banned_champion_id_to_name(self, list_of_banned_champions_in_current_match : list) -> dict:
        BLUE_SIDE_ID = 100
        RED_SIDE_ID = 200
        dict_of_champions = self.find_champion_ids_to_names(self.get_link_for_data_dragon())
        bans_dict = {
            "blue_side" : [],
            "red_side" : []
        }
        for champion_id, team_id in list_of_banned_champions_in_current_match:
            if team_id == BLUE_SIDE_ID:
                bans_dict["blue_side"].append(dict_of_champions[champion_id])
            elif team_id == RED_SIDE_ID:
                bans_dict["red_side"].append(dict_of_champions[champion_id])
            else:
                raise ValueError("Team ID not found")
        return bans_dict

    def print_side_bans(self):
        current_banned_champions_ids = self.get_banned_champions_in_current_match(self.get_link_for_live_match())
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

    # Nested dictionary, first initliases dictionary with champion names and sets wins and losses
    # for each champion to 0. Then checks the match data to determine if they win, if they win
    # add 1 to the wins, otherwise add 1 to the losses
    def get_win_and_losses_per_champion(self) -> dict[any, any]:
        dict_of_win_and_losses_per_champion = {}
        each_match_data = self.get_player_stats_from_previous_matches()
        for each_match in each_match_data:
            dict_of_win_and_losses_per_champion[each_match["championName"]] = {"Wins" : 0, "Losses" : 0}
        for each_match in each_match_data:
            if each_match["win"]:
                dict_of_win_and_losses_per_champion[each_match["championName"]]["Wins"] += 1
            else:
                dict_of_win_and_losses_per_champion[each_match["championName"]]["Losses"] += 1
        return dict_of_win_and_losses_per_champion

    def calculate_win_rate_per_champion(self, get_win_and_losses_per_champion : dict) -> dict:
        # print(get_win_and_losses_per_champion)
        champ_name_to_win_rate_dict = {}
        for champion_name, wins_and_losses_dict in get_win_and_losses_per_champion.items():
            wins = 0
            losses = 0
            # print(wins_and_losses_dict)
            for string, wins_and_losses in wins_and_losses_dict.items():
                # print(f"Name: {string}")
                # print(f"{wins_and_losses}")
                if string == "Wins":
                    wins += wins_and_losses
                elif string == "Losses":
                    losses += wins_and_losses
                else:
                    raise ValueError("Could not find win or loss")
            # print("Champion Name:", champion_name)
            # print("Wins:", wins)
            # print("Losses:", losses)
            if losses == 0:
                win_rate = 1
            else:
                win_rate = wins / (wins + losses)
            win_rate_percent = round(win_rate * 100, 2)
            champ_name_to_win_rate_dict[champion_name] = win_rate_percent

        return (champ_name_to_win_rate_dict)

    def get_win_rate_per_champion(self) -> dict:
        dict_of_win_and_losses_per_champion = self.get_win_and_losses_per_champion()
        champ_name_to_win_rate_dict = self.calculate_win_rate_per_champion(dict_of_win_and_losses_per_champion)
        return champ_name_to_win_rate_dict

    def print_win_rate_per_champion(self):
        champ_name_to_win_rate_dict = self.get_win_rate_per_champion()
        print(f"{self.summoner_name}'s winrate for each champion over the last {self.count} games")
        for champion_name, win_rate_percent in champ_name_to_win_rate_dict.items():
            print(f"{champion_name}: {win_rate_percent}%")