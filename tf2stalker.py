import requests

from json import loads
from sys import argv

ETF2L_TEAM_API = 'https://api.etf2l.org/team'
ETF2L_PLAYER_API = 'https://api.etf2l.org/player'

class Team:

    # Ex : https://api.etf2l.org/team/32155.json
    def __init__(self, teamID):

        api_req = requests.get(f'{ETF2L_TEAM_API}/{teamID}.json')
        self.teamData = loads(api_req.text)['team']

        self.country = self.teamData['country']
        self.type = self.teamData['type']
        self.name = self.teamData['name']
    


    def genPlayerStatsList(self):

        self.player_stats_list = []

        for player in self.teamData['players']:
            self.player_stats_list.append(Player(player['id']))
    

    def printPlayerStats(self):

        for player in self.player_stats_list:
            print(player.name)

        
    




class Player:

    # Ex : https://api.etf2l.org/player/116824.json
    def __init__(self, playerID):
        api_req = requests.get(f'{ETF2L_PLAYER_API}/{playerID}.json')
        self.playerData = loads(api_req.text)['player']

        self.name = self.playerData['name']
        self.classes = self.playerData['classes']



class Steam:

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

    new_team.genPlayerStatsList()

    new_team.printPlayerStats()





    