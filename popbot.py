# PopBot 0.1

import twitter
import random
from datetime import datetime as dt
import sqlite3
import newsgenerator as ng


class PopBot(object):
	def __init__(self):
		APP_KEY = '1Oieebhnx0xrTfRdlhLOPIUgF'
		APP_SECRET = 'WlBEMvbwxl2oH19Hvsx8kOrqBstPxLDsHkqu2i0x9Tq8gdABVh'
		OAUTH_TOKEN = "2786427865-vJzKgiRO75oblrsCEhkCynYBqR0a682NV0PeVxR"
		OAUTH_TOKEN_SECRET = "bI5So0s8bu0rk49gaRXd3Ypnl6PzFEs5wHjLlJOkc6CNM"

		auth = twitter.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
				APP_KEY, APP_SECRET)

		self.api = twitter.Twitter(auth=auth)

		self.news_generator = ng.NewsGenerator()

		self.db = sqlite3.connect("popbot.db")
		print "PopBot initialized"


	def store_user(self,user):
		print user
		user_id = user['id']
		name = user['name']
		fol_count = user['followers_count']
		fri_count = user['friends_count']
		self.db.execute("INSERT OR REPLACE INTO USERS (ID,NAME,FRIEND_COUNT,FOLLOWER_COUNT) VALUES (%d,'%s',%d,%d)"%(user_id,name,fri_count,fol_count,)	)
		self.db.commit()
		print "stored",name

	def get_users(self):
		cursor = self.db.execute("SELECT * FROM USERS")
		
		return [{'id':row[0],'name':row[1],'friends':row[2],'followers':row[3],'baited':row[4]} for row in cursor]
		

	def reset_db(self):
		self.db.execute("DELETE FROM USERS WHERE 1")
		self.db.execute("DROP TABLE USERS")
		self.db.execute("""
			CREATE TABLE USERS (
				ID INT NOT NULL PRIMARY KEY,
				NAME TEXT, 
				FRIEND_COUNT INT, 
				FOLLOWER_COUNT INT, 
				BAITED BOOLEAN DEFAULT 'FALSE')""")

	def shutdown(self):
		pass


	def cleanup_friends(self):
		# remove friends who do not follow back
		friends = set(self.api.friends.ids()['ids'])
		followers = set(self.api.followers.ids()['ids'])
		not_friends = list(friends - (friends.intersection(followers)))
		print "starting friend cleanup"
		for id in not_friends:
			print "removing friend with id",id
			self.api.friendships.destroy(user_id=id)



	def bait_user(self,user_id):
		#follow him
		print "baiting user", user_id
		self.api.friendships.create(user_id=user_id)
		#update user record in database
		self.db.execute("REPLACE INTO USERS (ID,BAITED) VALUES (%d, 'TRUE')"%(user_id,)	)
			
	def bait(self,n):
		# get n user_ids who havent been baited yet
		cursor = self.db.execute("SELECT * FROM USERS WHERE BAITED = 'FALSE' LIMIT %d"%(n,))
		for row in cursor:
			user_id = row[0]
			self.bait_user(user_id)			

	def fetch_follower_tweets(self):
		filehandle = open("tweets.txt","w")
		fol_ids = self.api.followers.ids()['ids']
		for fol_id in fol_ids:
			print "getting tweets from",fol_id
			result=self.api.statuses.user_timeline(user_id=fol_id)
			for tweet in result:
				text = tweet['text'].encode("utf8")
				filehandle.write(text+"\n")
		filehandle.close()
	
	
	def find_users(self,query):
		users = []
		geocode = "58.111466,15.211484,200mi"
		for i in range(50):
			print "getting page %d of query '%s'"%(i+1,query,)
			user_page = self.api.users.search(q=query,count=20,page=(i+1),location=geocode)
			users += user_page
		for user in users:
			self.store_user(user)		


	def post_news(self):
		url = self.news_generator.generate()
		self.api.statuses.update(status=url)
		print "posted status",url


	def test_message(self):
		self.api.direct_messages.new(screen_name="Where_is_JB_now",text="BOOM2")



if __name__=="__main__":
	# get command line arguments
	import sys
	commands = sys.argv[1:]
	
	bot = PopBot()
	if 'reset' in commands:
		bot.reset_db()

	if 'bait' in commands:
		bot.bait(30)
	
	if 'find' in commands:
		bot.find_users('norge')

	if 'unfollow' in commands:
		bot.cleanup_friends()

	if 'post' in commands:
		bot.post_news()

	if 'test' in commands:
		bot.news_generator.generate()
	
	bot.shutdown()









