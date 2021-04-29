#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import logging
import datetime

logger = logging.getLogger("database")

def init():
    logger.debug("initializing trends database")
    con = sqlite3.connect('trends.db')
    db = con.cursor()
    db.execute("CREATE TABLE IF NOT EXISTS trends( \
                language TINYTEXT, \
                trend TINYTEXT, \
                summary TEXT, \
                created TINYTEXT, \
                published TINYINT \
           )")
    con.commit()
    con.close()

def getTrends(language='de', limit=3, unpublishedOnly=False):
    con = sqlite3.connect('trends.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()
    if (unpublishedOnly):
        db.execute("SELECT * FROM trends WHERE language=? AND published='False' ORDER BY created DESC LIMIT ?",([str(language), limit]))
    else:
        db.execute("SELECT * FROM trends WHERE language=? ORDER BY created DESC LIMIT ?",([str(language), limit]))
    entries = db.fetchall()
    con.close()
    trends = []
    for entry in entries:
        trends.append(entry['trend'])
    logger.debug('following trends are being queried: ' + str(set(trends)))
    return set(trends)

def getTrend(title, language='de'):
    con = sqlite3.connect('trends.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()
    db.execute("SELECT * FROM trends WHERE trend=? AND language=?",([str(title), str(language)]))
    entries = db.fetchall()
    con.close()
    return entries

def addTrend(language, trend, queryDate, summary):
    logger.debug("adding new trend for " + language + " in database")
    con = sqlite3.connect('trends.db')
    db = con.cursor()
    db.execute("INSERT INTO trends (language,trend,summary,created,published) VALUES (?,?,?,?,'False')",([language,trend,summary,queryDate]))
    con.commit()
    con.close()
    
def setNotified():
    logger.debug("setting everything to published in database")
    con = sqlite3.connect('trends.db')
    db = con.cursor()
    db.execute("UPDATE trends set published='True' WHERE 1")
    con.commit()
    con.close()

