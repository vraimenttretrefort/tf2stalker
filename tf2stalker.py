import requests
from json import loads
from tabulate import tabulate


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

        avgTf2PlaytimeHrs = avgTf2PlaytimeHrs//considered_players

        return(avgTf2PlaytimeHrs, considered_players)



    def DBGprintPlayersStats(self):
        
        for player in self.players:
            print("-"*15)
            print(player.ETF2L.name)
            print("-"*15)
            

            print(5*"#" + "ETF2L" + "#"*5)
            print(f"\t{player.ETF2L.profileUrl}")
            print("\tClasses on ETF2L : {player.ETF2L.classes}")
            sixes_matches = player.ETF2L.machesplayed["6on6"]
            hl_matches = player.ETF2L.machesplayed["Highlander"]
            print(f"\t6v6 matches played : {sixes_matches}")
            print(f"\tHighlander matches played : {hl_matches}")


            print(5*"#" + "Steam" + "#"*5)
            print(f"\t{player.Steam.profileUrl}")
            print(f"\tTF2 playtime = {player.Steam.tf2PlaytimeHrs}H")
            for medal in player.Steam.tf2Medals:
                print(f"\t{medal}")
            
            print(5*"#" + "Logs.tf" + "#"*5)
            print(f"\t{LOGSTF_PROFILE}/{player.Steam.id64}")

            print("\n")


        print(f'This team has an average of {self.avgTf2PlaytimeHrs[0]} hours among {self.avgTf2PlaytimeHrs[1]} public profiles')


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
        self.profileUrl = f'{ETF2L_PLAYER_PAGE}/{self.id}'
        self.name = self.playerData['name']
        self.classes = self.playerData['classes']

        self.machesplayed = self.getMatches()


    def findDiv(self, match_string):
        """
        Divisions names are a huge mess, none of them are standard.
        This functions tries to find a fitting one anyway.

        Example output :
        - Premiership => Premiership
        - Season 32 Premiership Qualifiers => Premiership
        - Premiership Group => Premiership
        - Season 32 Premiership Qualifiers => Premiership
        - Division 3A => D3
        """

        # New divs
        if "Premiership" in match_string:
            div = "Premiership"
        
        elif "High" in match_string:
            div = "High"
        
        elif "Mid" in match_string:
            div = "Mid"
        
        elif "Low" in match_string:
            div = "Low"
        
        elif "Open" in match_string:
            div = "Open"
        
        # Old divs
        elif "Division " in match_string:
            for i in range(7):
                if f"Division {i}" in match_string:
                    div = f"D{i}"
        
        # Not found
        else:
            div = "Other cup"

        # Playoffs
        if "Playoffs" in match_string:
            div += " Playoffs"
        
        return(div)

    def getMatches(self):
        """
        Counts the number of matches played for a given player.
        Gathers all matches and split them into different categories.
        Returns a dictionnary containing the name of the division as the key and the number of matches played in the division as the value.
        """
        machesplayed = {
            '6on6':{},
            'Highlander':{}            
        }

        try:
            # light API request by getting the number of pages without any actual result
            numPages = int(loads(requests.get(f'{ETF2L_PLAYER_API}/{self.id}/results.json?since=0').text)['page']['total_pages'])
        
            for page in range(1, numPages+1):

                # GET the current page
                req_page = requests.get(f'{ETF2L_PLAYER_API}/{self.id}/results/{page}.json?since=0')
                page_results = loads(req_page.text)['results']

                if page_results:
                    for match in page_results:
                        divname = match['division']['name']
                        matchtype = match['competition']['type']

                        # Try to find a representative div name
                        if divname:
                            divname = self.findDiv(match['division']['name'])
                        else:
                            divname = self.findDiv(match['competition']['name'])


                        # Count the number of 6on6 matches in each div
                        if matchtype == '6on6':
                            if divname not in machesplayed['6on6']:
                                machesplayed['6on6'].update({divname:1})
                            else:
                                machesplayed['6on6'][divname] += 1

                        # Count the number of HL matches in each div
                        elif matchtype == 'Highlander':
                            if divname not in machesplayed['Highlander']:
                                machesplayed['Highlander'].update({divname:1})
                            else:
                                machesplayed['Highlander'][divname] += 1
        except:
            print(f"Unable to get matches for {self.name}")
        
        return(machesplayed)
       

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

        try:
            url_req = f'{STEAM_API}/IPlayerService/GetOwnedGames/v1/?'
            url_req += f'key={STEAM_API_KEY}&steamid={self.id64}&include_played_free_games=1'
            api_req =  requests.get(url_req)

            playerOwnedGames = loads(api_req.text)['response']

            # Dictionary not empty ==> Public profile
            if playerOwnedGames:
                for game in playerOwnedGames['games']:
                    if game['appid'] == STEAM_TF2_APPID:
                        tf2PlaytimeHrs = game['playtime_forever']//60 #playtime_forever in minutes

        except:
            print(f"Unable to get tf2 playtime for {self.id64}")
        
        return(tf2PlaytimeHrs)
        
    def getTf2Medals(self):
        """
        Returns all the Team Fortress 2 medals within a player Steam inventory in a list.
        """

        tf2Medals = []

        try:
            api_req =  requests.get(f'{STEAM_INVENTORY}/{self.id64}/{STEAM_TF2_APPID}/2?l=english&count=2000')
            playerInventory = loads(api_req.text)

            # Dictionary not empty ==> Public profile
            if playerInventory:
                for tf2item in playerInventory['descriptions']:
                    if 'Tournament Medal' in tf2item['type']:
                        tf2Medals.append(tf2item['name'])
            else:
                tf2Medals.append("Private inventory :/")
        except:
            print(f"Unable to get medals for {self.id64}")
            tf2Medals.append("error")
        
        return(tf2Medals)


class Logstf:
    """
    A class that holds all logs.tf-related player info + methods
    """
    def __init__(self):
        pass   


class UserInterface:
    """
    A class that holds all attributes and methods related to displaying results
    """

    def __init__(self, teamlist):
        self.teamlist = teamlist

    
    def tabulateTeam(self, team):
        headers = ["Name", "Playtime", "6s matches", "HL matches", "Medals", "Profile urls"]
        table = []
        
        for player in team.players:
            pinfo = []

            # Name
            pinfo.append(player.ETF2L.name)
            
            # Playtime
            if player.Steam.tf2PlaytimeHrs:
                pinfo.append(player.Steam.tf2PlaytimeHrs)
            else:
                pinfo.append("Private profile :/")
            
            # 6s Seasons
            sixes_matches = ""
            for div in player.ETF2L.machesplayed["6on6"]:
                sixes_matches += '{div} : {numMatches}\n'.format(div=div, numMatches=player.ETF2L.machesplayed["6on6"][div])
            pinfo.append(sixes_matches)

            # HL Seasons
            hl_matches = ""
            for div in player.ETF2L.machesplayed["Highlander"]:
                hl_matches += '{div} : {numMatches}\n'.format(div=div, numMatches=player.ETF2L.machesplayed["Highlander"][div])
            pinfo.append(hl_matches)

            # Medals
            player_medals = ""
            for medal in player.Steam.tf2Medals:
                player_medals += f'{medal}\n'
            pinfo.append(player_medals)

            # Profile urls
            urls = ""
            urls += f'{player.ETF2L.profileUrl}\n'
            urls += f'{player.Steam.profileUrl}\n'
            #TODO : Utiliser l'attribut player.Logstf.profileUrl quand il sera dispo
            urls += f'{LOGSTF_PROFILE}/{player.Steam.id64}'
            pinfo.append(urls)


            table.append(pinfo)
        
        # Total hours
        total_h = ["", f"AVERAGE TOTAL HOURS\n{team.avgTf2PlaytimeHrs[0]}H / {team.avgTf2PlaytimeHrs[1]} public profiles", "", "", "", "", "", ""]
        table.append(total_h)

        team_tab = tabulate(table, headers, tablefmt="grid")

        return(team_tab)


    def printTeamsTables(self):
        teamTables = []

        # Generate a list of tabulate objects
        for team in self.teamlist:
            teamTables.append(self.tabulateTeam(team))
        
        # Display each team table
        for teamTable in teamTables:
            print(teamTable)

    



def get_team_id(filepath):
    link = open(filepath , 'r')    
    liste = link.readlines()
    url_team = liste[0]
    team_id = url_team.strip("https:etf2l.orgteams/\n")

    
    return team_id



if __name__ == "__main__":
    
    new_team = Team('32155') #jump_etf2l_6v6.bsp
    #new_team.DBGprintPlayersStats()

    UI = UserInterface([new_team])
    UI.printTeamsTables()

