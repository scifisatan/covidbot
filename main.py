# Importing required python modules
from json import load
import os
import requests
import tweepy
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv

load_dotenv()

# Twitter API Authentication
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
webhook_url = os.getenv('WEBHOOK_URL')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Global Variables
url = "https://covid19.mohp.gov.np/covid/api/confirmedcases"
check = True
prevstat = ""


def number(num):
    result = f"{int(num):,d}"
    return result


# Getting data/numbers
def stats(link):
    data = requests.get(link).json()
    tested = data.get('nepal').get('samples_tested')
    negative = data.get('nepal').get('negative')
    positive = data.get('nepal').get('positive')
    deaths = data.get('nepal').get('deaths')
    recovered = data.get('nepal').get('extra1')
    date = data.get('nepal').get('date')
    today_death = data.get('nepal').get('today_death')
    today_newcase = data.get('nepal').get('today_newcase')
    today_recovered = data.get('nepal').get('today_recovered')
    today_rdt = data.get('nepal').get('today_rdt')
    today_pcr = data.get('nepal').get('today_pcr')
    new_data = f"{tested} {negative} {positive} {deaths} {recovered} {date} {today_death} {today_newcase} {today_recovered} {today_rdt} {today_pcr}"
    new_datal = new_data.split(' ')
    return new_datal


# Tweets
def tweet(msg):
    api.update_status(msg)
    print("Tweeted!")


# extracts previous data
def prev_data():
    tweets = []
    username = 'NepalCovid19Bot'

    for tweet in api.user_timeline(id=username,
                                   count=10,
                                   tweet_mode='extended'):
        tweets.append(tweet.full_text)

    for t in tweets:
        words = t.split()
        if "MoHP." in t:
            data = words
            break

    i = 0
    for word in data:
        if word == 'Date:':
            msg = (data[i + 1])
        i += 1

    return msg


# Formats Tweet
def format_post(new_data):
    msg = f"New Covid-19 Cases: {number(new_data[7])}\nToday\'s Deaths: {number(new_data[6])}\nToday\'s Recovered: {number(new_data[8])}\nTotal active cases: {number(int(new_data[2]) - int(new_data[3]) - int(new_data[4]))}\nPCR Test taken today: {number(new_data[10])}\nRDT Tests taken today: {number(new_data[9])}\nDate: {new_data[5]}"
    new_case = int(new_data[7])
    if new_case == 0:
        new_case = "no"
        case_value = 'cases'
        be_verb = 'have'
    elif new_case == 1:
        case_value = 'case'
        be_verb = 'has'
    else:
        case_value = 'cases'
        be_verb = 'have'

    new_death = int(new_data[6])
    if new_death == 0:
        new_death = "no"
        death_value = 'deaths'
        be_verb = 'have'
    elif new_death == 1:
        death_value = 'death'
        be_verb = 'has'
    else:
        death_value = 'deaths'
        be_verb = 'have'
    if new_case == 'no' and new_death != 'no':
        msg = f"{new_death} new COVID-19 related {death_value} in Nepal {be_verb} been reported by MoHP.\n\n" + msg
    elif new_case != 'no' and new_death == 'no':
        msg = f"{new_case} new COVID-19 {case_value} {be_verb} been reported by MoHP.\n\n" + msg
    else:
        msg = f"{new_case} new COVID-19 {case_value} and {new_death} new COVID-19 related {death_value} in Nepal {be_verb} been reported by MoHP.\n\n" + msg
    print("tweet formatted")
    return msg


print(format_post(stats(url)))


while check:
    try:
        prev_date = prev_data()
        new_date = stats(url)[5]
        '''print(new_date)
        print(prev_date)'''
        if prev_date != new_date:
            msg = format_post(stats(url))
            tweet(msg)
            webhook = DiscordWebhook(
                url=webhook_url, content=msg)
            response = webhook.execute()
        else:
            pass
    except KeyboardInterrupt:
        break
