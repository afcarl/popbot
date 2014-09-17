
import json
import urllib 

class NewsGenerator(object):
	def __init__(self):
		# svd api
		self.svd= json.load(urllib.urlopen("https://www.kimonolabs.com/api/6ekmqxg8?apikey=pxLpHSlRdqfoMxazY5CX43l1i058u9SK"))
		self.buzzfeed = json.load(urllib.urlopen("https://www.kimonolabs.com/api/60vnl0n6?apikey=pxLpHSlRdqfoMxazY5CX43l1i058u9SK"))
		pass

	def generate_svd(self):
		urls = []
		svd_items = self.svd['results']['collection1']
		for item in svd_items[:-1]:
			url = item['title']['href']
			urls.append(url)

		return urls[0]


	def generate_buzzfeed(self):
		items = self.buzzfeed['results']['collection1']

		urls = []
		for item in items:
			url = item['title']['href']
			urls.append(url)
			print url
		return ""

	def generate(self):
		return self.generate_buzzfeed()



