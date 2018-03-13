################ To do (current) ################

# All functions built to use twitchName as input, except Twitch information which builds list of Twitch Names

################ [Subfunctions] Twitch information ################
################ [1a] Twitch information ################
def readCSV(csvFileName):
	import csv
	csvdataRows = []
	with open(csvFileName, 'rb') as csvfile:
		spamreader = csv.reader(csvfile)
		#for line in data:
		for row in spamreader:
			csvdataRows.append(row)
	## Return rows #
	return csvdataRows

def writeStreamersToCSV(csvFileName, csvdataRows):
	import csv
	with open(csvFileName, 'wb') as csvfile:
		spamwriter = csv.writer(csvfile)
		for row in csvdataRows:
			spamwriter.writerow(row)
	return

def csvFilePath(csvFileName):
	from sys import platform
	if platform == 'darwin':
		return csvFileName
	else:
		return 'foundationsOfStrategy/' + csvFileName

def grabTwitchStreamers(minimumFollowers):
	# [1] Get data on streamers
	import requests
	streamers = []
	#minimumFollowers = 10000
	minimumFollowers = int(minimumFollowers)
	count = 0
	url = 'https://api.twitch.tv/kraken/streams?client_id=nrisqw9diqmthnvxx1rknb3wxzhwm2k&limit=100'
	r = requests.get(url)
	jsonObject = r.json()
	for stream in jsonObject['streams']:
		if (stream['channel']['followers'] > minimumFollowers) and (stream['channel']['language'] == 'en'):
			streamers.append(stream)
	print len(streamers)
	total = jsonObject['_total']
	print total
	def roundUp(x):
		import math
		return int(math.ceil(x / 100.0)) * 100
	for i in range(roundUp(total)/100):
		offset = str((i+1)*100)
		url = 'https://api.twitch.tv/kraken/streams?limit=100&offset=%s&stream_type=live&client_id=nrisqw9diqmthnvxx1rknb3wxzhwm2k' % offset
		r = requests.get(url)
		jsonObject = r.json()
		try:
			for stream in jsonObject['streams']:
				if (stream['channel']['followers'] > minimumFollowers) and (stream['channel']['language'] == 'en'):
					streamers.append(stream)
		except:
			print "Error with jsonObject['streams']"
		print len(streamers)
	#return streamers
	# [2] Decide which streamer data to save or update
	# Read in CSV, append new streamers, update? existing streamers #
	csvFileName = 'streamers.csv'
	#csvFileName = csvFilePath(csvFileName)
	csvdataRows = readCSV(csvFileName)
	for streamer in streamers:
		twitchNamesinCSV = [row[0] for row in csvdataRows]
		# For streamers in CSV, update #
		if streamer['channel']['name'] in twitchNamesinCSV:
			# Find index of twitchName #
			streamerIndex = twitchNamesinCSV.index(streamer['channel']['name'])
			# Update #
			csvdataRows[streamerIndex][1] = streamer['channel']['language'].encode("utf-8")
			csvdataRows[streamerIndex][2] = streamer['channel']['followers']
			csvdataRows[streamerIndex][3] = streamer['channel']['views']
			csvdataRows[streamerIndex][5] = streamer['channel']['mature']
			csvdataRows[streamerIndex][6] = streamer['channel']['partner']
			csvdataRows[streamerIndex][7] = streamer['channel']['logo'].encode("utf-8")
			csvdataRows[streamerIndex][8] = streamer['channel']['game'].encode("utf-8")
		# For streamers not in CSV, append #
		else:
			try:
				csvdataRows.append([streamer['channel']['name'].encode("utf-8"), streamer['channel']['language'].encode("utf-8"), streamer['channel']['followers'], streamer['channel']['views'], streamer['channel']['created_at'].encode("utf-8"), streamer['channel']['mature'], streamer['channel']['partner'], streamer['channel']['logo'].encode("utf-8"), streamer['channel']['game'].encode("utf-8"), '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
			except:
				print 'Error with csvdataRows.append'
	# Write out CSV #
	csvFileName = 'streamers.csv'
	#csvFileName = csvFilePath(csvFileName)
	writeStreamersToCSV(csvFileName, csvdataRows)
	return csvdataRows, streamers

################ Run ################

#grabTwitchStreamers(100)
