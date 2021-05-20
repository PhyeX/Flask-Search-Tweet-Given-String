from flask import Blueprint, render_template
import csv
import urllib.parse
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import pathlib
from io import StringIO
import os

app_blueprint = Blueprint('app_blueprint', __name__)


def getBearerToken():
    return "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA";


def getGuestToken():
    URL = "https://api.twitter.com/1.1/guest/activate.json"
    headers = {"authorization": getBearerToken()}
    response = requests.post(URL, headers=headers)
    return response.json().get("guest_token")


def urlEncoder(text):
    return urllib.parse.quote(text)


def getUserDataWithUsernameId(id):
    URL = "https://twitter.com/i/api/graphql/WN6Hck-Pwm-YP0uxVj1oMQ/UserByRestIdWithoutResults?variables=" + urlEncoder(
        '{"userId":"' + id + '","withHighlightedLabel":true}')
    headers = {"authorization": getBearerToken(), "x-guest-token": getGuestToken()}
    response = requests.get(URL, headers=headers)
    return response.json()


def getDataFromTwıtter(searchString):
    searchString = urlEncoder(searchString)
    sizeOfInput = "20"
    URL = "https://twitter.com/i/api/2/search/adaptive.json"

    params = {'include_profile_interstitial_type': '1', 'include_blocking': '1', 'include_blocked_by': '1',
              'include_followed_by': '1',
              'include_want_retweets': '1', 'include_mute_edge': '1', 'include_can_dm': '1',
              'include_can_media_tag': '1',
              'skip_status': '1', 'cards_platform': 'Web-12', 'include_cards': '1', 'include_ext_alt_text': 'true',
              'include_quote_count': 'true', 'include_reply_count': '1', 'tweet_mode': 'extended',
              'include_entities': 'true',
              'include_user_entities': 'true', 'include_ext_media_color': 'true',
              'include_ext_media_availability': 'true',
              'send_error_codes': 'true', 'simple_quoted_tweet': 'true', 'q': searchString, 'count': sizeOfInput,
              'query_source': 'typed_query',
              'pc': 1, 'spelling_corrections': '1', 'ext': 'mediaStats%2ChighlightedLabel'
              }

    headers = {"authorization": getBearerToken(),
               "x-guest-token": getGuestToken()}
    response = requests.get(URL, headers=headers, params=params)
    return response.json();


# Every relevant information about tweets should be visible, such as author, date, tweet contents, number of likes, number of retweets and number of discussions.
def extractData():
    json = getDataFromTwıtter("request for startup")
    data = json.get("globalObjects");
    path = 'output.csv'
    f = open(path, 'w' , newline='' ,encoding="utf-8")
    writer = csv.writer(f)
    tweetsAsList = []
    for tweet in data['tweets']:
        exractData = data['tweets'].get(tweet)
        dataOfTweet = {}
        id = str(exractData.get("user_id"))  # We got id to able learn what the name of the author is.
        holdData = exractData.get("full_text")
        dataOfTweet["author"] = getUserDataWithUsernameId(id).get('data').get('user').get('legacy').get('name') #such as author ( Get author name )
        dataOfTweet["content"] =  StringIO(holdData).getvalue().rstrip() # Get tweet
        dataOfTweet["date"] = exractData.get("created_at") # date
        dataOfTweet["numberOfLikes"] = exractData.get("favorite_count") # Number of likes
        dataOfTweet["numberOfRetweets"] = exractData.get("retweet_count") # number of the retweets
        dataOfTweet["numberOfDiscussions"] = exractData.get("reply_count") # Number of dicussions
        writer.writerow(dataOfTweet.values())
        tweetsAsList.append(dataOfTweet)

    return tweetsAsList

def readDataFromCsv():
    path = 'output.csv'
    with open(path, 'r', encoding="utf8") as file:
        reader = csv.reader(file)
        list = []
        for row in reader:
            mydict = {}
            mydict['author'] = row[0]
            mydict['content'] = row[1]
            mydict['date'] = row[2]
            mydict['numberOfLikes'] = row[3]
            mydict['numberOfRetweets'] = row[4]
            mydict['numberOfDiscussions'] = row[5]
            list.append(mydict)
        return list

def getData() :
    data = []
    if os.path.isfile('output.csv'): #Check out if there is output.csv
        data = readDataFromCsv()     #If there is then read from csv.
    else:
        data = extractData()  #Else, get data from twitter and write to csv.

    return data


@app_blueprint.route('/')
def hello_world():
    tweets = getData
    return render_template("index.html", tweets=tweets)
