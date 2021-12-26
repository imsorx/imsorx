import os
import logging
import requests
import json
import re


class UpdatSteamStats:

    endpoints = {
        'user_info': 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={steamId}',
        'owned_games': 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={steamId}&include_played_free_games=true&include_appinfo=true',
        'img': 'https://media.steampowered.com/steamcommunity/public/images/apps/{appId}/{url}.jpg'
    }

    status = {
        0: 'Offline',
        1: 'Online',
        2: 'Busy',
        3: 'Away',
        4: 'Snooze',
        5: 'looking to trade',
        6: 'looking to play'
    }

    __total_games: list = []

    def __init__(self) -> None:
        self.__key = os.environ['STEAM_KEY']
        self.__steamId = os.environ['STEAM_ID']
        self.fetch_info()
        self.fetch_games()
        self.write_changes()

    def write_changes(self):
        reader = open('README.md', encoding='utf-8')
        content = reader.read()
        reader.close()

        readme = self.build_content(content)

        writer = open('README.md', 'w', encoding='utf-8')
        writer.write(readme)
        writer.close()

    def fetch_info(self):
        url = self.__url('user_info')
        res = requests.get(url)
        self.__userInfo = json.loads(res.text)['response']['players'][0]

    def fetch_games(self):
        url = self.__url('owned_games')
        res = requests.get(url)
        games = (json.loads(res.text)['response']['games'])

        for game in games:
            self.__total_games.append({
                "name": game['name'],
                "hrs": round(game['playtime_forever']/60),
                "image": self.endpoints['img'].format(appId=game['appid'], url=game['img_logo_url'])
            })
        self.__total_games = sorted(
            self.__total_games, key=lambda game: game['hrs'], reverse=True)
        self.__total_games_count = len(self.__total_games)

    def build_content(self, content):
        updates = '<!-- steam-stats-start -->\n'
        updates += self.get_styles()
        games = ''
        for game in self.__total_games[:4]:
            games += self.get_game_template().format(
                src=game['image'], hrs=game['hrs']
            )

        updates += self.get_template().format(
            profile_url=self.__userInfo['profileurl'],
            username=self.__userInfo['personaname'],
            avatar_url=self.__userInfo['avatarfull'],
            status=self.get_status(),
            games_count=self.__total_games_count,
            games=games
        )
        updates += '<!-- steam-stats-end -->'

        # Replace posts
        pattern = re.compile(
            r'<!-- steam-stats-start -->[\s\S]*<!-- steam-stats-end -->')
        readme = re.sub(pattern, updates, content)
        return readme

    def get_status(self) -> str:
        if('gameextrainfo' in self.__userInfo):
            return 'Playing {}'.format(self.__userInfo['gameextrainfo'])
        return self.status[self.__userInfo['personastate']]

    def __url(self, endpoint: str) -> str:
        return self.endpoints[endpoint].format(
            key=self.__key,
            steamId=self.__steamId
        )

    def get_styles(self) -> str:
        return """<style>
    .container {
        padding: 1em 1.5em;
    }
    .user-info{
        color:inherit;
    }
    .user-info:hover{
        text-decoration:none;
        color:rgb(255, 136, 0);
    }
    .user-info figure{
        display: flex;
        align-items: center;
        margin: 0 0 1em 0;
        line-height: 1.2;
    }
    .games {
        display: flex;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 0.5em;
    }
    .games figure{
        padding: 0;
        margin: 0;            
    }
    .games figure figcaption{
        margin: 0;
        padding: 0;
        color: inherit;
        background-color: inherit;
    }
</style>"""

    def get_template(self) -> str:
        return """
<div class="container">
    <a href="{profile_url}" target="_blank" class="user-info">
        <figure>
            <img src="{avatar_url}" height="60px">
            <figcaption style="margin-left:0.5em">
                <strong>{username}</strong></br>
                <small>{status}</small> </br>
                <small>{games_count} Games owned</small>
            </figcaption>
        </figure>
    </a>
    <h4>Frequent games</h4>
    <div class="games">{games}
    </div>
</div>
"""

    def get_game_template(self) -> str:
        return """
        <figure>
              <img src="{src}">
              <figcaption>{hrs} hrs</figcaption>
        </figure>"""


if __name__ == '__main__':
    logging.basicConfig()
    try:
        worker = UpdatSteamStats()
    except Exception as e:
        logging.error(e)