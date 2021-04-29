#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import string
from time import sleep
import wikipedia
from datetime import date,timedelta
import pandas as pd

import os
import json
import requests
import shutil

import databaseHandler

HOURS_IDLE = 8
THUMB_DIR = "/app/trending/thumbs/"
EXCLUDED_TRENDS = ["Main_Page","Hauptseite"]
LANGUAGE = os.environ['LANGUAGE']

logger = logging.getLogger("wiki")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s', datefmt='%d.%m.%y %H:%M')
ch.setFormatter(formatter)
logger.addHandler(ch)

def check():
    yesterday = (date.today() - timedelta(days = 1)).strftime("%Y/%m/%d")
    languages = ['de']

    for language in languages:

        previouslyTrending = databaseHandler.getTrends(language, 1000)
        nowTrending = crawl(language, yesterday)
        if (len(nowTrending) == 0):
            continue
        logger.debug('Now trending (' + str(language) + "): " + str(nowTrending))
        newTrends = set(nowTrending) - set(previouslyTrending)
        if (len(newTrends) == 0):
            continue
        logger.info('New trends for ' + str(language) + ": " + str(newTrends))

        # save new trends in database
        for trend in newTrends:
            summary = getSummary(str(trend), str(language))
            if (summary != None):
                databaseHandler.addTrend(str(language), str(trend), str(yesterday), str(summary))
                downloadThumbnail(str(trend))

def crawl(language, queryDate):
    global EXCLUDED_TRENDS
    try:
        logger.debug ("checking wikipedia-" + str(language))

        url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/" + str(language) + ".wikipedia/all-access/" + str(queryDate)
        wikiData = pd.read_json(url)
        articles = pd.json_normalize(data=wikiData['items'][0]['articles'])
        # filter out special pages
        articles = articles[~articles['article'].str.contains(":")]
        articles = articles[~articles['article'].isin(EXCLUDED_TRENDS)]
        # take top 3
        articles = articles.sort_values(by=['rank'])[:3]
        return (articles['article'].values)

    except:
        logger.warning ("could not get trends for " + str(language) + " (" + str(queryDate) + ")")
        return []

def getSummary(title, language):
    wikipedia.set_lang(str(language))
    try:
        return (wikipedia.WikipediaPage(str(title)).summary)
    except:
        logger.warning("could not retrieve summary for " + str(title))
        return None

def downloadThumbnail(trend):
    try:
        logger.debug("searching thumbnail for " + trend)
        search_url = " https://"+LANGUAGE+".wikipedia.org/w/api.php?action=query&titles="+trend+"&prop=pageimages&format=json&pithumbsize=500"
        wiki_meta = json.loads(requests.get(search_url).text)
        for page in wiki_meta['query']['pages']:
            thumb_url = (wiki_meta['query']['pages'][page]['thumbnail']['source'])
            logger.debug (thumb_url)
            break

        imgtype = thumb_url.split(".")[-1]
        filename = THUMB_DIR+str(trend) + "." + imgtype

        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(thumb_url, stream = True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            # Open a local file with wb ( write binary ) permission.
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)
            logger.debug('Thumbnail image downloaded: ' + str(filename))
        else:
            logger.debug('Image couldn\'t be retreived')
    except:
        logger.debug("no thumbnail found.")

logger.info('starting wiki scanner')
databaseHandler.init()

while True:
    check()
    sleep(HOURS_IDLE*60*60)
