#!/usr/bin/env python
# Chir.py Twitter Bot
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/chir.py
# functions.py

import random
import re
import urllib.request

import feedparser

import config
import debug

def coinurl(url):
	source  = urllib.request.urlopen('https://coinurl.com/api.php?uuid=%s&url=%s' % (config.coinurl_uuid, url))
	charset = source.headers.get_content_charset()
	if charset : return source.read().decode(charset)
	else	   : return source.read().decode()

def get_news(): # This is very sloppy and needs some work.
	try:
		description = ''
		sport		  = random.choice(list(config.news_feeds.keys()))
		sport_news	 = feedparser.parse(config.news_feeds[sport])
		sport_keywords = config.news_keywords[sport]
		item = random.choice(sport_news.entries)
		description = strip_html(item.summary)
		description = sport + " " + description
		if ') -- ' in description:
			cutoff	  = description.split(') -- ')[0]
			description = description.split(cutoff)[1]
		if ') - ' in description:
			cutoff	  = description.split(') - ')[0]
			description = description.split(cutoff)[1]
		description = description.replace('*',  '')
		description = description.replace('\'', '')
		description = description.replace('"',  '')
		description = description.replace('--', '-')
		description = description.replace('  ', ' ')
		for word in sport_keywords:
			if word in description.lower():
				description = re.sub(word, '#' + word, description, flags=re.IGNORECASE)
		if len(description) > 115:
			description = description[:115] + '...'
		try:
			link = coinurl(item.link)
		except Exception as ex:
			debug.error('Error occured creating PPC link!', ex)
		else:
			description = description + ' ' + link
		return description
	except Exception as ex:
			debug.error('Error occured getting news!', ex)	


def strip_html(source):
	return re.compile(r'<.*?>').sub('', source)
