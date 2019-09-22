import feedparser
import pandas as pd
import datetime
import sys
import gspread
import smtplib
from oauth2client.service_account import ServiceAccountCredentials

import config

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPES)
client = gspread.authorize(creds)

urls = {'HUG': "http://hoppedupgaming.hipcast.com/rss/hoppedupgaming.xml",
        'SHU': "http://hoppedupgaming.hipcast.com/rss/super_hopped_up.xml"
        }


def email_alert(sub, msg):
    """
    Simple Script to use burner email account and alert me of failure to parse
    :param sub: subject
    :param msg: message
    :return: NA
    """
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(config.EMAIL, config.PASS)
        message = 'Subject {}\n\n{}'.format(sub, msg)
        server.sendmail(config.EMAIL, "c.norrisjones@gmail.com", message)
        server.quit()
        logfile = open("logfile", "a+")
        logfile.write(str(datetime.datetime.now()) + ": Error Email Sent\n")
        logfile.close()
    except Exception as error:
        logfile = open("logfile", "a+")
        logfile.write(str(datetime.datetime.now()) +
                      ": Error Email Attempted and Failed. Things going real wrong over here. Error is "
                      + str(error) + "\n")
        logfile.close()


def init_parser():
    """
    Used for Creating the initial Podcast Info csv, parsing pertinent details from rss feed. I could probably have it
    automatically create a related google worksheet, but this function should honestly only be run in the event I lose
    the current master sheet online

    :return: Nothing, but generates csv file of all old HUG and current SHU podcast episodes
    """
    episode_list = []   # episode #'s
    title_list = []     # episode titles
    episode_date = []   # date of episode's release
    podcast_type = []   # Whether it's Hopped-Up Gaming or Super Hopped-Up
    duration_list = []  # Episode Length
    beer_list = []      # That Episode's Beer
    host_list = []      # Hosts in episode

    for url in urls:
        podcast_feed = feedparser.parse(urls[url])

        for entry in podcast_feed['entries']:
            podcast_type.append(url)
            # Parse episode number from title
            try:
                episode_list.append(int(entry["title"].split(" ")[1][:-1]))
            except ValueError:
                episode_list.append(0)

            # Parse episode name from title
            try:
                title_list.append(entry["title"].split(": ")[1])
            except IndexError:
                title_list.append(entry["title"].split(": ")[0])

            # Pull episode day, month, year
            episode_date.append(entry['published'][5:16])

            # Pull episode's duration
            duration_list.append(entry['itunes_duration_detail']['value'])

            # Pull episode content, (attempt to) parse hosts and beer
            try:
                beer_list.append(entry['content'][0]['value'].split("of the Week:")[1].split("\n")[0])
            except IndexError:
                beer_list.append("Couldn't Parse")
            try:
                host_list.append(entry['content'][0]['value'].split("Hosts: ")[1].split("\n")[0])
            except IndexError:
                host_list.append("Couldn't Parse")

    # Throw results into pandas dataframe
    podcast_df = pd.DataFrame({"Podcast Type": podcast_type,
                               "Episode Number": episode_list,
                               "Episode Title": title_list,
                               "Episode Date": episode_date,
                               "Episode Length": duration_list,
                               "Hosts": host_list,
                               "Episode Beer": beer_list,
                               })

    # Sort entries so latest from new podcast first
    podcast_df.sort_values(by=['Podcast Type', 'Episode Number'], ascending=False, inplace=True)
    # Re-index, convert to csv
    podcast_df.reset_index(drop=True, inplace=True)
    podcast_df.to_csv('podcast.csv')

    logfile = open("logfile", "a+")
    logfile.write(str(datetime.datetime.now()) + ": New CSV file created\n")
    logfile.close()
    return


def update_parser():
    """
    Pulls latest entry from SHU RSS feed, parses for pertinent info, connects to google sheets via API, then adds new
    row. If update fails,
    :return:
    """
    sheet = client.open("Podcast Info").sheet1
    try:
        podcast_feed = feedparser.parse(urls['SHU'])
        latest_entry = podcast_feed['entries'][0]
        ep_num = int(latest_entry["title"].split(" ")[1][:-1])

        try:
            ep_title = latest_entry["title"].split(": ")[1]
        except IndexError:
            ep_title = latest_entry["title"].split(": ")[0]

        ep_date = latest_entry['published'][5:16]
        ep_len = latest_entry['itunes_duration_detail']['value']

        try:
            ep_hosts = latest_entry['content'][0]['value'].split("Hosts: ")[1].split("\n")[0]
        except IndexError:
            ep_hosts = "Couldn't Parse"

        try:
            ep_beer = latest_entry['content'][0]['value'].split("of the Week:")[1].split("\n")[0]
        except IndexError:
            ep_beer = "Couldn't Parse"

        sheet.insert_row(["SHU", ep_num, ep_title, ep_date, ep_len, ep_hosts, ep_beer], index=2,
                         value_input_option='USER_ENTERED')

        logfile = open("logfile", "a+")
        logfile.write(str(datetime.datetime.now()) + ": New podcast entry successfully added\n")
        logfile.close()

    except Exception as error:
        logfile = open("logfile", "a+")
        logfile.write(str(datetime.datetime.now()) + ": Error updating podcast feed. Error is: " + str(error) + "\n")
        logfile.close()
        # Email me so I know something's up
        email_alert("Pod Parser Update Failed", "Check Log")
    return


def main(argv):
    if argv == '-c':
        print("Creating New CSV")
        # init_parser()
    elif argv == '-u':
        print("Updating Google Sheet")
        update_parser()
    else:
        print("No valid argument given. Closing.")
    return


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError as err:
        print("No argument given. Closing.")
