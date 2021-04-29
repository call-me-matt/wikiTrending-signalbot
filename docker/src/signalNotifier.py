#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import requests
import fnmatch
from time import sleep

import databaseHandler

HOURS_IDLE = os.environ['HOURS_IDLE']
GROUP_ID = os.environ['GROUP_ID']
USERNAME = os.environ['USERNAME']

INITIAL_IDLE = 5*60*60
THUMB_DIR = "/app/trending/thumbs/"

logger = logging.getLogger("signal")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s', datefmt='%d.%m.%y %H:%M')
ch.setFormatter(formatter)
logger.addHandler(ch)

def send_message(trend,language,summary):
    signal_cli = '/app/signal-cli/bin/signal-cli --config /app/signal_config/ --username ' + USERNAME

    caption = trend + " (https://" + language + ".wikipedia.org/wiki/" + trend + ")"
    message = summary

    # thumb available?
    thumb = ""
    for file in os.listdir(THUMB_DIR):
        if fnmatch.fnmatch(file,str(trend)+'.*'):
            thumb = THUMB_DIR + file
            break

    # send image
    if thumb == "":
        message = caption + " | " + message
    else:
        os.system(signal_cli + ' send --message "'+caption+'" -a "'+thumb+'" -g '+GROUP_ID+' > /dev/null 2>&1')
    os.system(signal_cli + ' send --message "'+message+'" -g '+GROUP_ID+' > /dev/null 2>&1')

    logger.info("sent trend " + str(trend) + " to group")
    logger.debug("receiving messages (for chat consistency only)")
    os.system(signal_cli + ' receive --ignore-attachments > /dev/null 2>&1')

def get_new_trends():
    languages = ['de']
    for language in languages:
        logger.debug('checking ' + str(language))
        trends = databaseHandler.getTrends(language=str(language), unpublishedOnly=True)
        if (trends != set()):
            logger.debug("Sending out new trends (" + language + ")")
            for trend in trends:
                logger.debug("Sending out new trend " + str(trend))
                wikiData = databaseHandler.getTrend(str(trend), str(language))
                send_message(str(trend)), str(language), str(wikiData[0]['summary'])
            logger.debug("Setting everything to notified")
            databaseHandler.setNotified()


logger.debug("Setting everything to notified")
databaseHandler.init()
databaseHandler.setNotified()
sleep(INITIAL_IDLE)

logger.info('starting')
while True:
    get_new_trends()
    sleep(HOURS_IDLE*60*60)
