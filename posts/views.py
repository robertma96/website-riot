from django.shortcuts import render, redirect
from .forms import PostsForm
import json
import requests
import time
from .models import Posts
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
api_key = config.get('auth', 'api_key')


def summonerid(summoner_name, region):
    global profileIcon, summonerlevel, summoner_name_real
    link = "https://" + region + ".api.riotgames.com/lol/summoner/v3/summoners/by-name/" + \
           summoner_name.replace(" ", "%20") + "?api_key=" + api_key
    response = requests.get(link)
    if response.status_code == 200:
        obiect = json.loads(response.content.decode('utf-8'))
        accountId = obiect['accountId']
        id_simple = obiect['id']
        profileIcon = obiect['profileIconId']
        summonerlevel = obiect['summonerLevel']
        summoner_name_real = obiect['name']
        return id_simple, accountId
    else:
        print(response.status_code)


def getIDMatches(reg, accountid):
    lista_match_id = []
    beginIndex = 0
    endIndex = 100
    link = "https://" + \
           reg + ".api.riotgames.com/lol/match/v3/matchlists/by-account/" + str(accountid) + "?beginIndex=" + str(
        beginIndex) + "&endIndex=" + str(endIndex) + "&queue=420&season=11&api_key=" + api_key
    response_link = requests.get(link)
    if response_link.status_code == 200:
        obiect = json.loads(response_link.content.decode('utf-8'))
        for i in range(len(obiect['matches'])):
            lista_match_id.append(obiect['matches'][i]['gameId'])

    while len(lista_match_id) == endIndex:
        beginIndex = endIndex
        endIndex = endIndex + 100
        link = "https://" + \
               reg + ".api.riotgames.com/lol/match/v3/matchlists/by-account/" + str(accountid) + "?beginIndex=" + str(
            beginIndex) + "&endIndex=" + str(endIndex) + "&queue=420&season=11&api_key=" + api_key
        response_link = requests.get(link)
        if response_link.status_code == 200:
            obiect = json.loads(response_link.content.decode('utf-8'))
            for i in range(len(obiect['matches'])):
                lista_match_id.append(obiect['matches'][i]['gameId'])
    return lista_match_id


def rank(reg, summoner_id):
    link = "https://" + reg + ".api.riotgames.com/lol/league/v3/positions/by-summoner/" + str(summoner_id) + \
           "?api_key=" + api_key
    response = requests.get(link)
    if response.status_code == 200:
        obiect = json.loads(response.content.decode('utf-8'))
        wins = obiect[0]['wins']
        losses = obiect[0]['losses']
        winrate = round((wins / (wins + losses)) * 100, 0)
        return obiect[0]['tier'], obiect[0]['rank'], obiect[0]['leaguePoints'], obiect[0]['wins'],obiect[0]['losses'],\
               winrate
    else:
        print(response.status_code)

def inlocuire_nume(campion):
    with open('champions.txt', 'r+') as file:
        obiect = json.loads(file.readline())
    a = list(obiect['data'])
    id_champ = campion
    for champ in a:
        if obiect['data'][str(champ)]['id'] == id_champ:
            nume = obiect['data'][str(champ)]['name']
            nume_splashart = champ
            return nume, nume_splashart


def championwinrate(lista_meciuri, a, regiune, listacampionijucati):
    lista_winrate_campioni = []
    update = None
    participant_id = None
    kills = None
    deaths = None
    assists = None
    meciuri_de_adaugat = []
    matchID = lista_meciuri
    contor = 0
    if len(matchID) != len(a):
        print('Am intrat')
        update = True
        if len(a) != 0:
            print('Am intrat aici?')
            lista_de_comparat = a
            lista_winrate_campioni = listacampionijucati
            for j in range(len(matchID)):
                if lista_meciuri[j] not in lista_de_comparat:
                    meciuri_de_adaugat.append(lista_meciuri[j])
        else:
            meciuri_de_adaugat = lista_meciuri
    if update == True:
        print(meciuri_de_adaugat)
        for match in meciuri_de_adaugat:
            print(match)
            lista = [None, None]
            champID = None
            games = 0
            win = 0
            k = 0
            WON = None
            link_match = "https://" + regiune + ".api.riotgames.com/lol/match/v3/matches/" + str(match) + \
                         "?api_key=" \
                         + api_key
            response_match = requests.get(link_match)
            if response_match.status_code == 200:
                obiect = json.loads(response_match.content.decode('utf-8'))
                if int(obiect['gameDuration']) < 300:
                    print("REMAKEEEEEEEEEEEEEEEEEEEEEEEEE " + str(obiect['gameDuration']))
                    continue
                else:
                    for i in range(2):
                        lista[i] = obiect['teams'][i]['win']
                    for i in range(0, 10):
                        if obiect['participantIdentities'][i]['player']['accountId'] == a_id:
                            participant_id = obiect['participantIdentities'][i]['participantId']
                        if obiect['participants'][i]['participantId'] == participant_id:
                            kills = obiect['participants'][i]['stats']['kills']
                            deaths = obiect['participants'][i]['stats']['deaths']
                            assists = obiect['participants'][i]['stats']['assists']
                        if obiect['participantIdentities'][i]['player']['accountId'] == a_id:
                            if i + 1 <= 5 and lista[0] == 'Win':
                                champID = obiect['participants'][i]['championId']
                                games = 1
                                win = 1
                                WON = True
                                print("WIN " + str(champID))
                            elif i + 1 > 5 and lista[1] == 'Win':
                                champID = obiect['participants'][i]['championId']
                                games = 1
                                win = 1
                                WON = True
                                print("WIN " + str(champID))
                            else:
                                champID = obiect['participants'][i]['championId']
                                games = 1
                                WON = False
                                print("LOSS " + str(champID))
                    lista_de_adaugat = [champID, games, win, kills, deaths, assists]
                    contor = contor + 1
                    if contor == 30:
                        time.sleep(30)
                        contor = 0
                    if len(lista_winrate_campioni) == 0:
                        lista_winrate_campioni.append(lista_de_adaugat)
                    else:
                        for i in range(len(lista_winrate_campioni)):
                            if champID != lista_winrate_campioni[i][0]:
                                k = k + 1
                                if k == len(lista_winrate_campioni):
                                    lista_winrate_campioni.append(lista_de_adaugat)
                            elif champID == lista_winrate_campioni[i][0]:
                                lista_winrate_campioni[i][1] += 1
                                lista_winrate_campioni[i][3] += lista_de_adaugat[3]
                                lista_winrate_campioni[i][4] += lista_de_adaugat[4]
                                lista_winrate_campioni[i][5] += lista_de_adaugat[5]
                                if WON == True:
                                    lista_winrate_campioni[i][2] += 1
                                    WON = None
            else:
                print(response_match.status_code)
    else:
        print("No new Updates")
    return lista_winrate_campioni


def index(request):
    print('Hello')
    global s_id, a_id, region, summoner_name
    if request.method == "POST":
        form = PostsForm(request.POST)
        if form.is_valid():
            summoner_name = request.POST['summoner_name']
            region = request.POST['region']
            s_id, a_id = summonerid(summoner_name, region)
            post_item = form.save(commit=False)
            post_item.summonerID = s_id
            post_item.accountID = a_id
            search = Posts.objects.filter(summoner_name=summoner_name, region=region)
            if not search:
                post_item.save()
            listofgames = getIDMatches(region, a_id)    #Din API, actualizata
            searchgamesplayed = Posts.objects.filter(summoner_name=summoner_name, region=region).values('gamesPlayed')[0]['gamesPlayed']
            searchchampsplayed = Posts.objects.filter(summoner_name=summoner_name, region=region).values('championsPlayed')[0]['championsPlayed']
            currentid = Posts.objects.filter(summoner_name=summoner_name, region=region).values('id')[0]['id']
            t = Posts.objects.get(id=int(currentid))
               #from DB
            if len(searchchampsplayed) != 0:
                champslist = json.loads(searchchampsplayed)
            else:
                champslist = []
            if len(searchgamesplayed) != 0:
                gameslist = json.loads(searchgamesplayed)
            else:
                gameslist = []
            champ = championwinrate(listofgames, gameslist, region, champslist)
            if len(champ) != 0:
                t.championsPlayed = champ
                t.save()
            if len(searchgamesplayed) == 0:
                t.gamesPlayed = listofgames
                t.save()
            elif len(searchgamesplayed) != 0:
                gameslist = json.loads(searchgamesplayed)
                if len(gameslist) != len(listofgames):
                    t.gamesPlayed = listofgames
                    t.save()
                else:
                    pass
            return redirect('/stats/')
    else:
        form = PostsForm()
    return render(request, 'posts/index.html', {
        'form': form,
        'title': 'Please enter your summoner name and select your region',
    })


def stats(request):
    print("stats")
    tier, mrank, leaguepoints, wins, losses, winrate = rank(region, s_id)
    icon = "http://ddragon.leagueoflegends.com/cdn/8.6.1/img/profileicon/" + str(profileIcon) + ".png"
    tier_icon = tier.lower() + "_" + mrank.lower() + ".png"

    listapentruhtml = []
    print('Helo')
    searchchampsplayed = Posts.objects.filter(summoner_name=summoner_name, region=region).values('championsPlayed')[0][
        'championsPlayed']
    if len(searchchampsplayed) != 0:
        listadinBDD = json.loads(searchchampsplayed)
        listadinBDD.sort(key=lambda x: x[1], reverse=True)
        for i in range(len(listadinBDD)):
            campion = listadinBDD[i][0]
            numar_jocuri = listadinBDD[i][1]
            numar_winuri = listadinBDD[i][2]
            numar_killuri = listadinBDD[i][3]
            numar_deaths = listadinBDD[i][4]
            numar_assists = listadinBDD[i][5]
            avgkills = round(int(numar_killuri)/int(numar_jocuri), 1)
            avgdeaths = round(int(numar_deaths)/int(numar_jocuri), 1)
            avgassists = round(int(numar_assists)/int(numar_jocuri), 1)
            nume, nume_splash = inlocuire_nume(campion)
            splah_art = "http://ddragon.leagueoflegends.com/cdn/8.8.2/img/champion/" + nume_splash + ".png"
            winrate_int = round((int(numar_winuri)/int(numar_jocuri))*100)
            winrate_campion = str(winrate_int) + "%"
            kda = round((int(numar_killuri) + int(numar_assists)) / int(numar_deaths), 2)
            tulp = (nume, splah_art, numar_jocuri, winrate_campion, kda, avgkills, avgdeaths, avgassists)
            listapentruhtml.append(tulp)
        print(listapentruhtml)


    return render(request, 'posts/stats.html', {
        'name': summoner_name_real,
        'summonerlevel': summonerlevel,
        'icon': icon,
        'tier': tier.title() + " " + mrank,
        'leaguepoints': str(leaguepoints) + 'LP',
        'wins': str(wins) + 'W',
        'losses': str(losses) + 'L',
        'winrate': str(round(winrate)) + '%',
        'tier_icon': tier_icon,
        'listapentruhtml': listapentruhtml,
        'title': 'Aici o sa vezi statsurile',
    })

# def champswinrate(request):
#     listapentruhtml = []
#     print('Helo')
#     searchchampsplayed = Posts.objects.filter(summoner_name=summoner_name, region=region).values('championsPlayed')[0][
#         'championsPlayed']
#     if len(searchchampsplayed) != 0:
#         listadinBDD = json.loads(searchchampsplayed)
#         listadinBDD.sort(key=lambda x: x[1], reverse=True)
#         for i in range(len(listadinBDD)):
#             campion = listadinBDD[i][0]
#             numar_jocuri = listadinBDD[i][1]
#             numar_winuri = listadinBDD[i][2]
#             numar_killuri = listadinBDD[i][3]
#             numar_deaths = listadinBDD[i][4]
#             numar_assists = listadinBDD[i][5]
#             splah_art = "http://ddragon.leagueoflegends.com/cdn/8.6.1/img/champion/" + listadinBDD[i][6] + ".png"
#             winrate = int(numar_jocuri)/int(numar_winuri)
#             kda = (int(numar_killuri) + int(numar_assists))/int(numar_deaths)
#             nume = inlocuire_nume(campion)
#             tulp = (nume, splah_art, numar_jocuri,winrate, kda)
#             listapentruhtml.append(tulp)
#         print(listapentruhtml)
#     return render(request, 'posts/stats.html', {
#         'listapentruhtml': listapentruhtml
#     })