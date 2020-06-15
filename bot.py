# Importing required python modules
import requests
from bs4 import BeautifulSoup
import time
import schedule
import tweepy

#Twitter API Authentication
consumer_key = "Z4GnZtQPUqPCdNh2fNR3mooQ6"
consumer_secret = "xO35iLKm5XifzphrhVdvpjq7uKOgFQwF87HxQqOR0TlzzvYvBy"
access_token = "1261594236207525888-wAzxJpiRY8Uk5pwcEzeOyzGQdXbbuf"
access_token_secret = "A01ydtGKRCFgJamaNOrH7yp6zzExE1hKJ014qatc8VW8p"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Global Variables
url = "https://covid19.mohp.gov.np/covid/api/confirmedcases"
check = True
prevstat = ""

# Getting data/numbers
def stats(link):
    data = requests.get(link).json()
    tested = data.get('nepal').get('samples_tested')
    negative = data.get('nepal').get('negative')
    positive = data.get('nepal').get('positive')
    deaths = data.get('nepal').get('deaths')
    dt = data.get('nepal').get('created_at')
    recovered = data.get('nepal').get('extra1')
    today_death = data.get('nepal').get('today_death')
    today_newcase = data.get('nepal').get('today_newcase')
    today_recovered = data.get('nepal').get('today_recovered')
    new_data = f"{tested} {negative} {positive} {deaths} {recovered} {dt} {today_death} {today_newcase} {today_recovered}"
    return new_data


def update(new_datal):
    taim = new_datal[6]
    if int(taim.split(':')[0]) > 12:
        dt =  f"{int(taim.split(':')[0])%12}:{taim.split(':')[1]} PM"
    else:
        dt = f"{int(taim.split(':')[0])}:{taim.split(':')[1]} AM"
    return dt

# Formats Tweet
def format_post(new_datal,db_data):
    msg = f"Total Positive Cases: {new_datal[2]}\nDeaths: {new_datal[3]}\nRecovered: {new_datal[4]}\nSamples Tested: {new_datal[0]}\nUpdated at: {update(new_datal)}\n"
    new_case = int(new_datal[2])-int(db_data[1])
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

    new_death = int(new_datal[3])-int(db_data[2])
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
    if new_case =='no' and new_death != 'no':
        msg = f"{new_death} new COVID-19 related {death_value} in Nepal {be_verb} been reported by MoHP.\n\n"+msg
    elif new_case!='no' and new_death == 'no':
        msg = f"{new_case} new COVID-19 {case_value} {be_verb} been reported by MoHP.\n\n"+msg
    else:
        msg = f"{new_case} new COVID-19 {case_value} and {new_death} new COVID-19 related {death_value} in Nepal {be_verb} been reported by MoHP.\n\n"+msg
    print("tweet formatted")
    return msg


# Tweets
def tweet(msg):
    api.update_status(msg)
    print("tweeted")

#Daily Update
def daily_update():
    url = "https://covid19.mohp.gov.np/covid/api/confirmedcases"
    data = requests.get(url).json()
    today_death = data.get('nepal').get('today_death')
    today_newcase = data.get('nepal').get('today_newcase')
    today_recovered = data.get('nepal').get('today_recovered')
    post = f"Updates from last 24 Hours\n\nNew COVID-19 cases: {today_newcase}\nPatients recovered: {today_recovered}\nCOVID-19 related deaths: {today_death}\n"
    tweet(post)


def prev_data():
    tweets = []
    username = 'NepalCovid19Bot'

    for tweet in api.user_timeline(id=username, count=10, tweet_mode = 'extended'):
        tweets.append(tweet.full_text)

    for t in tweets:
        words = t.split()
        if "reported by MoHP." in t:
            data = words
            break

    i = 0
    for word in data:
        if word == 'Cases:':
            total = data[i+1]
        elif word == 'Deaths:':
            deaths = data[i+1]
        elif word == 'Recovered:':
            recovered = data[i+1]
        elif word == 'Tested:':
            sample = data[i+1]
        i +=1

    data = f'{sample} {total} {deaths} {recovered}'
    msg = data.strip().split(' ')
    print("previous data extracted")
    print(msg)
    return msg

# Main
schedule.every().day.at('20:00').do(daily_update)

while check:
    try:
        schedule.run_pending()
        db_data = prev_data()
        new_data = stats(url)
        new_datal = new_data.split(' ')
        if new_datal[3] != db_data[2] or new_datal[2] != db_data[1]:
            msg = format_post(new_datal,db_data)
            print("New data found.... Tweeting...")
            print(new_datal,db_data)
            try:
                tweet(msg)
            except:
                pass
        else:
            pass
    except KeyboardInterrupt:
        break
    except:
        pass




