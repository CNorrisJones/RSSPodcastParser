import feedparser
import numpy as np
import pandas as pd
import re

def main():

    urls = {'HUG': "http://hoppedupgaming.hipcast.com/rss/hoppedupgaming.xml",
            'SHU': "http://hoppedupgaming.hipcast.com/rss/super_hopped_up.xml"
            }

    episode_list = []
    title_list = []
    podcast_type = []
    episode_host_list = []
    duration_list = []
    beer_list = []

    for url in urls:
        podcast_feed = feedparser.parse(urls[url])

        for entry in podcast_feed['entries']:
            # Enter in which podcast type
            podcast_type.append(urls[url])

            # Parse episode number from title
            episode_list.append(entry["title"].split(" ")[1][:-1])

            # Parse episode name from title
            try:
                title_list.append(entry["title"].split(": ")[1])
            except IndexError:
                title_list.append(entry["title"].split(": ")[0])

            # Pull episode's description
            duration_list.append(entry['itunes_duration_detail']['value'])

            # Pull episodes content, (attempt to) parse hosts and beer
            try:
                beer_list.append(entry['content'][0]['value'].split("of the Week:")[1].split("\n")[0])
            except IndexError:
                beer_list.append("None")

    podcast_df = pd.DataFrame({"Podcast Type": podcast_type,
                               "Episode Number": episode_list,
                               "Episode Title": title_list,
                               "Episode Length": duration_list,
                               "Episode Beer": beer_list
                               })

    podcast_df.to_csv('podcast.csv')
    return


if __name__ == "__main__":
    main()