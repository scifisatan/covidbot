# Importing required python modules
import requests
from bs4 import BeautifulSoup
import time
import schedule
import tweepy

#Twitter API Authentication
consumer_key = "XklQ1cCtsnz69OxI5M0HTBnxD"
consumer_secret = "hr8GbfI7qlYjvrFSpF0dhRDbl7ScISumNunImzbdQ1n4S36sCi"
access_token = "1261594236207525888-rSiG1qqxk2rRH2JAUx5xMbrvEj1hqG"
access_token_secret = "qrU5TIUWZK3JL9Zt82ZuFGHrfz6H9daLAoqKP21Dh5Eja"
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
    recovered = BeautifulSoup(requests.get("https://www.worldometers.info/coronavirus/country/nepal/").text,'html.parser').find_all('div',{'class':'maincounter-number'})[2].text.strip()
    new_data = f"{tested} {negative} {positive} {deaths} {recovered} {dt}"
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
    new_case = int(new_datal[2])-int(db_data[2])
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
        
    new_death = int(new_datal[3])-int(db_data[3])
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
    return msg                  


# Tweets
def tweet(msg):
    api.update_status(msg)

# Daily Update
def daily_update():
    data_today = stats(url)
    data_todayl = data_today.split(' ')
    with open('daily_data.txt','r') as f:
        db_data_yesterday = f.readline().strip().split(' ')
        post = f"Updates From Last 24 Hours\n\nSamples tested: {int(data_todayl[0])-int(db_data_yesterday[0])}\nNew COVID-19 cases: {int(data_todayl[2])-int(db_data_yesterday[2])}\nPatients recovered: {int(data_todayl[4])-int(db_data_yesterday[4])}\nCOVID-19 related deaths: {int(data_todayl[3])-int(db_data_yesterday[3])}\n"
        browser.refresh()
        tweet(post)
    with open('daily_data.txt','w') as f:
        f.write(data_today+'\n')

# Main
schedule.every().day.at('20:00').do(daily_update)

while check:
    try:
        schedule.run_pending()
        with open('covid19_data.txt','r') as f:
            db_data = f.readline().strip().split(' ')
        new_data = stats(url)
        new_datal = new_data.split(' ')
        msg = format_post(new_datal,db_data)
        if new_datal[2] == db_data[2] and new_datal[3] == db_data[3]:
            pass
        else:
            tweet(msg)
            with open('covid19_data.txt','w') as f:
                f.write(new_data+'\n')
    except KeyboardInterrupt:
        break
    except:
        pass

