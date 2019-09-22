# RSSPodcastParser

RSS Parser, Used to parse podcast rss to create csv of podcast details, including episode title, episode number, drink of the week, etc. 

Uses feedparser library to pull rss feed, and depending on action either parses full rss feed for pertinent data, creates a pandas dataframe, and turns it into csv, or it pulls the latest episode, parses, connects to corresponding google sheet via google api, and updates with latest episode.

Requires google api credentials file, and a config file setup for email warning system in event of failed episode update. Also logs events into simple log file.
