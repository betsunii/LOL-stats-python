import json
import requests
import sys

#temp api key, Sign in/up @ https://developer.riotgames.com to generate a new one
api_key = 'RGAPI-a19393ec-6b7e-4f0e-9ebb-734a0a0914e7'

class Summoner:
    def __init__(self, name, tag):
        self._name = name
        self._tag = tag

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self,tag):
        if not len(tag) >= 3 or not len(tag) <=5:
            raise ValueError("Tag must be between 3 and 5 caracters")
        self._tag = tag

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not len(name) >= 3 or len(name) <= 16:
            raise ValueError("Summoner name must be between 3 and 16 caracters")
        if name.isalnum() == False:
            raise ValueError("Summoner name can't have any special caracters")
        self._name = name

def main():
#1 fetch puuid
    summoner = Summoner(input("Summoner name: "), input("Tag: #"))
    puuid = get_puuid(summoner.name, summoner.tag)
    #print(puuid)

#2 fetch id from puuid
    id = get_id(puuid)

#3 fetch stats
    playerstats = player_ranked_stats(id)

#4 fetch last matches
    lastmatches= get_player_last_matches(puuid)
    #print(lastmatches)

#5 & 6 Print player stats and match history
    print_player_stats(playerstats)
    print_match_history(lastmatches, puuid)

def get_puuid(name, tag):
    try:
        api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
        api_url = api_url + name + "/" + tag + "?api_key=" + api_key
        resp = requests.get(api_url)
        player_info = resp.json()
        puuid = player_info['puuid']
    except KeyError:
        print("Wrong summoner name or tag")
        main()
    else:
        return puuid

def get_id(puuid):
    api_url2 = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + puuid
    api_url2 = api_url2 + "?api_key=" + api_key
    resp2 = requests.get(api_url2)
    id = resp2.json()
    player_id = id["id"]
    #print (player_id)
    return player_id

#3 Gets the player stats
def player_ranked_stats(player_id):
    api_url3 = "https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/"
    api_url3 = api_url3 + player_id + "?api_key=" + api_key
    resp3 = requests.get(api_url3)
    playerstats = resp3.json()
    return playerstats

#4 gets the last 10 matches played
def get_player_last_matches(player_puuid):
    api_url4 = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"
    api_url4 = api_url4 + player_puuid + "/ids?start=0&count=10&" +"api_key=" + api_key
    resp4 = requests.get(api_url4)
    lastmatches = resp4.json()
    return lastmatches

#5 Gets the match details
def match_details(lastmatches,playerpuuid):
    api_url5 = "https://europe.api.riotgames.com/lol/match/v5/matches/"
    api_url5 = api_url5 + lastmatches+ "?api_key=" + api_key
    resp5 = requests.get(api_url5)
    matchdetails = resp5.json()
    n = matchdetails["metadata"]["participants"].index(playerpuuid)
    return matchdetails["info"]["participants"][n]

#5 Prints the player stats
def print_player_stats(playerstats):
    if playerstats == []:
        print ("The player has yet to complete his promomoton games")
    else:
        list = playerstats[0]
        print("Tier: " + list["tier"] + " " + list["rank"] + " " + str(list["leaguePoints"])+ "LP")
        winrate = int(list["wins"]) / (int(list["wins"]) + int(list["losses"])) * 100
        winrate = int(winrate)
        print("Win Rate: " + str(winrate) + "%" )
        print("Wins: " + str(list["wins"]))
        print("Losses: " + str(list["losses"]))

#6 Prints the match history
def print_match_history(lastmatches,puuid):
    matchhistory = []
    won = 0
    loss = 0
    for i in range(5):
        matchdetails = match_details(lastmatches[i], puuid)

        if matchdetails['win'] == False:
            loss += 1
            game = "DEFEAT "
        elif matchdetails['win'] == True:
            game = "VICTORY"
            won += 1

        matchhistory.append(game + "   " + matchdetails['championName'] + "    " + matchdetails['role'] + "    " + str(matchdetails['kills']) + "/" + str(matchdetails['deaths']) + "/" + str(matchdetails['assists']) )
    print("Last 10 games win rate: " + str(won/(won+loss)*100) + "%")

    for i in matchhistory:
        print (i)

if __name__ == "__main__":
    main()

