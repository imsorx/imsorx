import os
import requests
import json
import base64


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
        content = self.build_content()
        writer = open('steam-stats.svg', 'w', encoding='utf-8')
        writer.write(content)
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
                "image": self.get_image(self.endpoints['img'].format(appId=game['appid'], url=game['img_logo_url']))
            })
        self.__total_games = sorted(
            self.__total_games, key=lambda game: game['hrs'], reverse=True)
        self.__total_games_count = len(self.__total_games)

    def build_content(self):
        updates = ''
        games = ''
        for game in self.__total_games[:4]:
            games += self.get_game_template().format(
                src=game['image'], hrs=game['hrs']
            )

        updates += self.get_template().format(
            styles=self.get_styles(),
            profile_url=self.__userInfo['profileurl'],
            username=self.__userInfo['personaname'],
            avatar_url=self.__userInfo['avatarfull'],
            status=self.get_status(),
            games_count=self.__total_games_count,
            games=games
        )

        return updates

    def get_status(self) -> str:
        if('gameextrainfo' in self.__userInfo):
            return 'Playing {}'.format(self.__userInfo['gameextrainfo'])
        return self.status[self.__userInfo['personastate']]

    def __url(self, endpoint: str) -> str:
        return self.endpoints[endpoint].format(
            key=self.__key,
            steamId=self.__steamId
        )
    def get_image(self,url):
        with requests.get(url) as response:
            return "data:" + response.headers['Content-Type'] + ";" + "base64," + str(base64.b64encode(response.content))

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
        return """<svg fill="none" viewBox="0 0 800 400" width="800" height="400" xmlns="http://www.w3.org/2000/svg">
    <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml">
            {styles}
            <div class="container">
                <a href="{profile_url}" target="_blank" class="user-info">
                    <figure>
                        <img src="{avatar_url}" height="60px" />
                        <figcaption style="margin-left:0.5em">
                            <strong>{username}</strong><br />
                            <small>{status}</small><br />
                            <small>{games_count} Games owned</small>
                        </figcaption>
                    </figure>
                </a>
                <h4>Frequent games</h4>
                <div class="games">{games}
                </div>
            </div>
        </div>
    </foreignObject>
</svg>
"""

    def get_game_template(self) -> str:
        return """
        <figure>
              <img src="{src}" />
              <figcaption>{hrs} hrs</figcaption>
        </figure>"""


if __name__ == '__main__':
    try:
        worker = UpdatSteamStats()
    except Exception as e:
        print(traceback.format_exc())
