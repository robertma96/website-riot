from django.shortcuts import render, redirect
from .forms import PostsForm
import json
import requests
from .models import Posts
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
api_key = config.get('auth', 'api_key')


def summonerid(summoner_name, region):
    global accountId, id_simple
    link = "https://" + region + ".api.riotgames.com/lol/summoner/v3/summoners/by-name/" + \
           summoner_name.replace(" ", "%20") + "?api_key=" + api_key
    response = requests.get(link)
    if response.status_code == 200:
        obiect = json.loads(response.content.decode('utf-8'))
        accountId = obiect['accountId']
        id_simple = obiect['id']
        return id_simple, accountId
    else:
        print(response.status_code)


def index(request):
    if request.method == "POST":
        form = PostsForm(request.POST)
        if form.is_valid():
            summoner_name = request.POST['summoner_name']
            region = request.POST['region']
            s_id, a_id = summonerid(summoner_name, region)
            post_item = form.save(commit=False)
            post_item.summonerID = s_id
            post_item.accountID = a_id
            search = Posts.objects.filter(summoner_name=summoner_name, region= region)
            if not search:
                post_item.save()
            return redirect('/posts/')
    else:
        form = PostsForm()
    return render(request, 'posts/index.html', {
        'form': form,
        'title': 'Summoner Stats',
    })
