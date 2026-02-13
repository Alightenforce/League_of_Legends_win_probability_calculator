import requests
import os
from dotenv import load_dotenv
import json
import time
import climage
from PIL import Image
from io import BytesIO

class Riot_API:

    load_dotenv()
    API_KEY = os.getenv("RIOT_API_KEY")

    def __init__(self):
        self.api_key = self.API_KEY
        self.session = requests.Session()

    def get_account_data(self, region: str, name: str, tag: str):
        link = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={self.api_key}"
        return self.get_json(link)

    def get_region_data(self, region: str, puuid : str):
        link = f"https://{region}.api.riotgames.com/riot/account/v1/region/by-game/lol/by-puuid/{puuid}?api_key={self.api_key}"
        return self.get_json(link)

    def get_summoner_data(self, region_code: str, puuid: str):
        link = f"https://{region_code}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={self.api_key}"
        return self.get_json(link)

    def get_match_ids(self, region: str, puuid: str, count: int):
        link = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={self.api_key}"
        return self.get_json(link)

    def get_match_detail(self, region: str, match_id: str):
        link = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={self.api_key}"
        return self.get_json(link)

    def get_mastery_data(self, region_code: str, puuid: str):
        link = f"https://{region_code}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?api_key={self.api_key}"
        return self.get_json(link)

    def get_active_game(self, region_code: str, puuid: str):
        link = f"https://{region_code}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={self.api_key}"
        return self.get_json(link)

    def get_json(self, link : str):
        response = self.session.get(link)
        return response.json()

    def get_most_recent_version(self):
        link = "https://ddragon.leagueoflegends.com/api/versions.json"
        versions = self.get_json(link)
        return versions[0]

    def get_champion_data(self, version: str):
        link = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
        return self.get_json(link)


