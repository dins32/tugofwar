Twug-of-war
-----------

The classic game of strength and skill - with all of the strength and skill removed.

Two twitter hashtags are pitted against one another.  Which one will win?

Targets the Holiday by MooresCloud - either a real unit, or the simulator

To make this work without a Holiday, you'll need the following:

* simpype - the Holiday simulator - https://github.com/moorescloud/simpype
* iotas - the Internet of Things Access Server - https://github.com/moorescloud/iotas

Clone or otherwise install both projects, then start them up as follows:

blah/blah/simpype% python simpype.py

/blah/blah/iotas% python iotas.py

Now you should be able to point a browser window at localhost:8888 and see the Holiday simulator running.

Now you need to start Twug-of-war.

Invoke with: python tow.py #hashtag1 #hashtag2 hostname:port

The program will attempt to log into Twitter using your Twitter credentials.  
If you haven't used Twug-of-War before, you'll be directed to the OAuth authorization page for twitter.
It will give you a seven-digit PIN, pop that in when asked, and you'll be good to go.
Authorization should only need to be done once per account.

If you don't provide a hostname:port, the default IoTAS simulator value of 'localhost:8080' is used.

Good luck!