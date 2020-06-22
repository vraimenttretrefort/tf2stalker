import requests
from json import loads


ETF2L_TEAM_API = 'https://api.etf2l.org/team'
ETF2L_PLAYER_API = 'https://api.etf2l.org/player'
ETF2L_PLAYER_PAGE = 'https://etf2l.org/forum/user'


STEAM_PROFILE = 'https://steamcommunity.com/profiles'
STEAM_API_KEY = '1470922A6B6E5C001546E51ACA5D987B' #Randomly taken from internet, lel
STEAM_API = 'https://api.steampowered.com/'
STEAM_INVENTORY = 'https://steamcommunity.com/inventory'
STEAM_TF2_APPID = 440


LOGSTF_PROFILE = 'http://logs.tf/profile'
TF2CENTER_PROFILE = 'https://tf2center.com/profile'


class Team:

    def __init__(self, teamID):

        api_req = requests.get(f'{ETF2L_TEAM_API}/{teamID}.json')
        self.teamData = loads(api_req.text)['team']

        self.country = self.teamData['country']
        self.type = self.teamData['type']
        self.name = self.teamData['name']

        self.players = self.genPlayerList()

        self.avgTf2PlaytimeHrs = self.getAvgTf2PlaytimeHrs()
        
    def genPlayerList(self):

        players = []

        for player in self.teamData['players']:
            new_player = Player()
            new_player.ETF2L = ETF2L(player['id'])
            new_player.Steam = Steam(player['steam']['id64'])

            players.append(new_player)
        
        return(players)

    def getAvgTf2PlaytimeHrs(self):
        
        avgTf2PlaytimeHrs = 0
        considered_players = 0

        for player in self.players:

            if player.Steam.tf2PlaytimeHrs:
                avgTf2PlaytimeHrs += player.Steam.tf2PlaytimeHrs
                considered_players += 1

        avgTf2PlaytimeHrs = avgTf2PlaytimeHrs//6

        return(avgTf2PlaytimeHrs, considered_players)



    def printPlayerStats(self):

        for player in self.players:
            print("-"*15)
            print(player.ETF2L.name)
            print("-"*15)
            print(f'{ETF2L_PLAYER_PAGE}/{player.ETF2L.id}/')

            print(f'{player.Steam.profileUrl}')
            print(f'\tTF2 playtime = {player.Steam.tf2PlaytimeHrs}H')
            for medal in player.Steam.tf2Medals:
                print(f'\t{medal}')

            #print(f'{LOGSTF_PROFILE}/{player.steam_id64}')
            #print(f'{TF2CENTER_PROFILE}/{player.steam_id64}/')


class Player:

    def __init__(self):
        self.ETF2L = None
        self.Steam = None
        self.Logstf = None


class ETF2L:
    """
    A class that holds all ETF2L-related player info + methods
    """
    def __init__(self, playerID):
        api_req = requests.get(f'{ETF2L_PLAYER_API}/{playerID}.json')
        self.playerData = loads(api_req.text)['player']

        self.id = playerID
        self.name = self.playerData['name']
        self.classes = self.playerData['classes']
        
        

class Steam:
    """
    A class that holds all Steam-related player info + methods
    """
    
    def __init__(self, id64):
        self.id64 = id64
        self.profileUrl = f'{STEAM_PROFILE}/{self.id64}'
        self.tf2PlaytimeHrs = self.getTf2Playtime()
        self.tf2Medals = self.getTf2Medals()
    
    def getTf2Playtime(self):

        tf2PlaytimeHrs = None
        url_req = f'{STEAM_API}/IPlayerService/GetOwnedGames/v1/?'
        url_req += f'key={STEAM_API_KEY}&steamid={self.id64}&include_played_free_games=1'
        api_req =  requests.get(url_req)

        playerOwnedGames = loads(api_req.text)['response']

        # Dictionary not empty ==> Public profile
        if playerOwnedGames:
            for game in playerOwnedGames['games']:
                if game['appid'] == STEAM_TF2_APPID:
                    tf2PlaytimeHrs = game['playtime_forever']//60
        
        return(tf2PlaytimeHrs)
        
    def getTf2Medals(self):

        tf2Medals = []
        api_req =  requests.get(f'{STEAM_INVENTORY}/{self.id64}/{STEAM_TF2_APPID}/2?l=english')
        playerInventory = loads(api_req.text)

        # Dictionary not empty ==> Public profile
        if playerInventory:
            for tf2item in playerInventory['descriptions']:
                if 'Tournament Medal' in tf2item['type']:
                    tf2Medals.append(tf2item['name'])
        
        return(tf2Medals)


class Logstf:
    """
    A class that holds all logs.tf-related player info + methods
    """
    def __init__(self):
        pass   


def get_team_id(filepath):
    link = open(filepath , 'r')    
    liste = link.readlines()
    url_team = liste[0]
    team_id = url_team.strip("https:etf2l.orgteams/\n")

    
    return team_id



if __name__ == "__main__":
    
    print(get_team_id('to_stalk.txt'))

    new_team = Team('32155')

    new_team.printPlayerStats()

    print(f'This team has an average of {new_team.avgTf2PlaytimeHrs[0]} hours among {new_team.avgTf2PlaytimeHrs[1]} public profiles')
