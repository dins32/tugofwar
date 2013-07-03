#/usr/bin/python
#
"""Try to open a filtered search stream
   And grab the #qanda tagged tweets
   Then spit out the timestamp of the tweet.  
   Which can then be used as an input to another script.  BECAUSE MODADS.

Homepage and documentation: http://dev.moorescloud.com/

Copyright (c) 2012, Mark Pesce.
License: MIT (see LICENSE for details)"""

__author__ = 'Mark Pesce'
__version__ = '0.01.dev'
__license__ = 'MIT'

import sys, os, json, time, stat
from twitter.oauth_dance import oauth_dance
import twitter

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import requests

# File name for the oauth info
#
# This will work for *NIX systems, not sure for Windows.
#
fn = os.path.join(os.path.expanduser('~'),'.qanda-oauth')

consumer_secret=con_secret = "pG9hrZAUURqyDTfBbJcgAMdpemBmgAdZDL92ErVELY"
consumer_key=con_key = "JwCegsVjfjfK0GvsQkpUw"

# Do we have the correct OAuth credentials?
# If credentials exist, test them.  
# If they fail, delete them.
# If they do not exist or fail, create them.
#
def check_twitter_auth():
	authorized = False
	if os.path.isfile(fn):  # Does the token file exist?
		tokens = twitter.oauth.read_token_file(fn)
		#print 'OAuth tokens exist, will try to authorize with them...'
		twapi = twitter.Twitter(auth = twitter.OAuth(token=tokens[0],
					token_secret=tokens[1],
					consumer_secret=con_secret, 
					consumer_key=con_key))
		try:
			result = twapi.account.verify_credentials()
			twitter_id = result['id']
			twitter_handle = result['screen_name']
			#print 'Good, we seem to be authorized for username %s with id %d' % (twitter_handle, int(twitter_id))
			authorized = twapi
		except twitter.TwitterError as e:
			print "Call failed, we don't seem to be authorized with existing credentials.  Deleting..."
			print e
			os.remove(fn)

	if authorized == False:                   # If not authorized, do the OAuth dance
		print 'Authorizing the app...'
		tokens = oauth_dance(app_name='CrypTweet', consumer_key=con_key, consumer_secret=con_secret, token_filename=fn)
		os.chmod(fn, stat.S_IRUSR | stat.S_IWUSR)		# Read/write, user-only
		#
		# Get an open API object for Twitter
		#
		twapi = twitter.Twitter(auth = twitter.OAuth(token=tokens[0],
						token_secret=tokens[1],
						consumer_secret=con_secret, 
						consumer_key=con_key))
		try:	# Is this going to work?
			result = twapi.account.verify_credentials()
			twitter_id = result['id']
			twitter_handle = result['screen_name']
			print 'Good, we seem to be authorized for username %s with id %d' % (twitter_handle, int(twitter_id))
			authorized = twapi
		except twitter.TwitterError as e:		# Something bad happening, abort, abort!
			print "Call failed, we don't seem to be authorized with new credentials.  Deleting..."
			print e
			os.remove(fn)
			
	return authorized

curr_sec = 0
total_in_sec = 0
total_in_last_sec = 0
SAMPLE_SIZE = 1

visarray = [ [0, 0, 0], [0, 0, 15], [ 0, 0, 63 ], [ 0, 0, 128 ], [0, 0, 255], 
[0, 15, 255 ], [ 0, 63, 255 ], [ 0, 127, 255 ], [ 0, 255, 255 ], 
[ 0, 255, 127 ], [ 0, 255, 63 ], [ 0, 255, 15 ], [ 0, 255, 0 ], 
[ 15, 255, 0 ], [ 63, 255, 0 ], [ 127, 255, 0 ], [ 255, 255, 0 ], 
[ 255, 127, 0 ],  [ 255, 63, 0 ], [ 255, 15, 0 ], [ 255, 0, 0 ] ] 
vislast = [ 0, 0, 0 ]


def visualize(hz):
	"""Visualize the data and send it out to a nearby Holiday. Or even not so nearby."""

	global visarray, vislast
	hostname = "192.168.0.129"

	if hz >= len(visarray):
		visnew = visarray[len(visarray)-1]
	else:
		visnew = visarray[hz]

	gradjson = """{ "begin": %s, "end": %s, "steps": 12 }""" % (vislast, visnew)
	print gradjson
	r = requests.put("http://%s/device/light/gradient" % hostname, data=gradjson)
	vislast = visnew
	return

class StdOutListener(StreamListener):
	""" A listener handles tweets are the received from the stream. 
	This is a basic listener that just prints received tweets to stdout.

	"""
	def on_data(self, data):
		global curr_sec, total_in_sec, total_in_last_sec, SAMPLE_SIZE

		dj = json.loads(data)
		try:
			djt = dj['created_at']
			tv = time.strptime(djt, "%a %b %d %H:%M:%S +0000 %Y")
			tvs = time.mktime(tv)
			#sys.stdout.write("%s\n" % tvs)
			#sys.stdout.flush()

			# Count the number of tweets to occur in that second
			# If the second has changed, clear count, start again.
			if (tvs > (curr_sec + SAMPLE_SIZE)):
				curr_sec = tvs			# Set to current second
				total_in_last_sec = total_in_sec
				total_in_sec = 1
				#sys.stdout.write("Total in last second: %d\n" % total_in_last_sec)
				sys.stdout.write("%d,\n" % total_in_last_sec)
				sys.stdout.flush()
				#visualize(total_in_last_sec)
			else:
				total_in_sec = total_in_sec + 1

		except KeyError:
			pass

		return True

	def on_error(self, status):
		print status

class Listener(threading.Thread):
	"""If you want to run the Twitter listener on its own thread, use this"""
	def run(self):
		global hashterm
		stream = Stream(auth, l)	
		stream.filter(track=[hashterm])  # Blocking call.  We do not come back.

if __name__ == '__main__':
	"""The two strings passed after command invocation are the two search terms for the tug-of-war"""

	if len(sys.argv) > 2:
		hashterm = [ sys.argv[1], sys.argv[2] ]
	else:
		hashterm = [ "Morales", "Snowden" ]		# You asked for it
		print "Using defaults"
		
	if (check_twitter_auth() == False):
		sys.exit()
	
	tokens = twitter.oauth.read_token_file(fn)

	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(tokens[0], tokens[1])

	#stream = Stream(auth, l)	
	#stream.filter(track=[hashterm])  # Blocking call.  We do not come back.

	while True:
		# Process updates
		time.sleep(.1)
		
