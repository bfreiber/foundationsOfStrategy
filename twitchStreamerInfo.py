################ To do (current) ################

# Timing - not 50, but keep goign until hit 50 seconds
# Only overwrite if len(twitchStreamerInfo) >= len(streamersStaging)

# Open questions
	# Wait for page load (terminate after n seconds if no result)
	# Rewrite readCSV and writeStreamersToCSV to include digital ocean locations
	# Add killChromeprocesses to run
	# Move Twitch information to another page

	# [1] Save file + twitchstreamer function
	# [2] path to csvfile os vs. linux
	# [3] function to put everything together - run once per hour?

################ MAP ################
# [1] Define funcitons
	# [1a] Twitch information: (language, current game, total views, total followers, streamlabs exists?)
	# [1b] Twinge data: (game breakdown top 3 %, )
	# [1c] Streamlabs data (exists?) - DONE
	# [1d] Contact info (I: PayPal, II: Twitch channel panels)
	# [1e] Videos/VODS
	# [1f] Digital ocean server specific functions
		# [1eI] Kill all chrome instances
		# [1eII] Save location?
# [2] Run functions

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
			try:
				spamwriter.writerow(row)
			except:
				try:
					print "Error (spam)writing row: " + row[0]
				except:
					print "Error (spam)writing row"
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
		if (stream['channel']['followers'] > minimumFollowers):# and (stream['channel']['language'] == 'en'):
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
		for stream in jsonObject['streams']:
			if (stream['channel']['followers'] > minimumFollowers):
				streamers.append(stream)
		print len(streamers)
	#return streamers
	# [2] Decide which streamer data to save or update
	# Read in CSV, append new streamers, update? existing streamers #
	csvFileName = 'streamersNew.csv'
	csvFileName = csvFilePath(csvFileName)
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
			csvdataRows.append([streamer['channel']['name'].encode("utf-8"), streamer['channel']['language'].encode("utf-8"), streamer['channel']['followers'], streamer['channel']['views'], streamer['channel']['created_at'].encode("utf-8"), streamer['channel']['mature'], streamer['channel']['partner'], streamer['channel']['logo'].encode("utf-8"), streamer['channel']['game'].encode("utf-8"), '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
	# Write out CSV #
	csvFileName = 'streamersNew.csv'
	csvFileName = csvFilePath(csvFileName)
	writeStreamersToCSV(csvFileName, csvdataRows)
	return csvdataRows, streamers

################[1b] Twinge data ################

# Map (twitchName) -> (lastMonthsViews)
def lastMonthsViewsTwinge(twitchName):
	url = 'http://twinge.tv/%s/growth/#/30' % twitchName
	# Kill all chrome processes
	killChromeIfDigitalOcean()
	try:
		soup=getSoupFromUrl(url)
		monthlyViews = int(soup.find_all("span", {"class":"channelGrowth__increase ng-binding"})[2].text.replace(',','').replace(' ',''))
		return monthlyViews
	except:
		return "Unavailable"

# Map: (twitchName) -> ([{'game1':'x}, {'game2':'y',}, {'game3':'z'}], monthlyHoursStreamed, gamesPlayed, averageConcurrentViewers) s.t x+y+z = 1 = 100%
def gameDistribution(twitchName):
	import urllib
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from random import randint
	import os
	import random
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	import requests
	import time
	from bs4 import BeautifulSoup
	import requests
	import re
	url = 'http://twinge.tv/channels/%s/games/#/30' % twitchName
	# Kill all chrome processes
	killChromeIfDigitalOcean()
	try:
		driver = startSelenium()
		driver.get(url)
		#sleep(randint(3,4))#1-5 seconds
		wait = WebDriverWait(driver, 20)
		element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'channelAllGames__game')))
		def miniSleep():
			sleep(random.uniform(0, 1))
			return
		miniSleep()
		soup=BeautifulSoup(driver.page_source)
		driver.quit()
		#game = soup.find_all("td", {"class":"channelAllGames__game ng-binding"})[0].text.replace('\t','').replace('\n','').replace('Broadcasts','').replace('Directory','').rstrip()
		gamesSoup = soup.find_all("td", {"class":"channelAllGames__game ng-binding"})
		timeHoursSoup = soup.find_all("span", {"class":"hide-hover ng-binding"})
		timePercentagesSoup = soup.find_all("span", {"class":"show-hover ng-binding"})
		viewersPercentagesSoup = soup.find_all("td", {"class":"u-tac ng-binding"})
		averageViewersSoup = soup.find_all("td", {"class":"box-table__right u-tac ng-binding"})
		games = []
		for i in range(len(gamesSoup)):
			games.append({'name':gamesSoup[i].text.replace('\t','').replace('\n','').replace('Broadcasts','').replace('Directory','').rstrip(), 'timeHours':timeHoursSoup[i].text,'timePercentage':timePercentagesSoup[i].text,'viewersPercentage':viewersPercentagesSoup[i].text,'averageViewers':averageViewersSoup[i].text.replace(',','')})
		summarySoup = soup.find_all("h3", {"class":"ng-binding"})
		monthlyHoursStreamed = summarySoup[0].text
		gamesPlayed = summarySoup[1].text
		averageConcurrentViewers = summarySoup[3].text.replace(',','')
		return games, monthlyHoursStreamed, gamesPlayed, averageConcurrentViewers
	except:
		return ([], "Unavailable", "Unavailable", "Unavailable")

# Map (twitchName) -> (averageConcurrentViewers) [UNNCESSARY]
def averageConcurrentViewersTwinge(twitchName):
	url = 'http://twinge.tv/channels/%s/' % twitchName
	# Kill all chrome processes
	killChromeIfDigitalOcean()
	try:
		soup=getSoupFromUrl(url)
		concurrentViewers = ""
		div = soup.find_all("div", {"class":"channelStats__column box-bigVal"})
		for h3 in div:
			h3Tags = h3.find_all("h3", {"class": "ng-binding"})
			for tag in h3Tags:
				concurrentViewers = tag.text
		concurrentViewers = int(concurrentViewers.replace(',',""))
		return concurrentViewers
	except:
		return concurrentViewers

# Map (twitchName) -> (monthlyHoursStreamed) [UNNECESSARY]
def monthlyHoursStreamed(twitchName):
	import time
	# Kill all chrome processes
	killChromeIfDigitalOcean()
	url = 'http://twinge.tv/channels/%s/streams' % twitchName
	try:
		soup=getSoupFromUrl(url)
		# [A] Times streamed #
		h5 = soup.find_all("h5", {"class":"ng-binding"})
		if len(h5) < 30:
			return 'Not enough Twinge data (fewer than 30'
		# Find closest date to 1 month ago.
		now = time.time()
		# (Wed Apr 8, 2015 @  4:20 PM) -> (1509753600)
		def turnTextDateToEpoch(textTime):
			import time
			import re
			now = time.time()
			if any(word in textTime for word in ['Today', 'Yesterday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']):
				return now
			else:
				months = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
				textTime = textTime.split()
				year = textTime[3]
				month = months[textTime[1]]
				day = str(textTime[2]).replace(',','').replace(' ','')
				if len(day) == 1:
					day = '0' + day
				actualTime = '%s-%s-%s' % (year, month, day)
				pattern = '%Y-%m-%d'
				epoch = int(time.mktime(time.strptime(actualTime, pattern)))
				return epoch
		allDates = [turnTextDateToEpoch(time.text) for time in h5]
		oneMonth = now-(30*24*60*60)
		indexFromEnd = len(allDates) - allDates.index(min(allDates, key=lambda x:abs(x-oneMonth)))
		# [B] Hours streamed #
		li = soup.find_all("li", {"ng-if":"stream.last_updated"})
		monthlyHoursList = [time.text.replace(" ", "") for time in li[:indexFromEnd]]
		# [C] Sum hours #
		minutes = sum([int(monthlyHoursListElement[monthlyHoursListElement.find(":")+1:]) for monthlyHoursListElement in monthlyHoursList])
		hours = sum([int(monthlyHoursListElement[:monthlyHoursListElement.find(":")]) for monthlyHoursListElement in monthlyHoursList])
		totalHours = ("%.2f" % (minutes/60.0 + hours))
		return totalHours
	except:
		return 'There was an error'


################[1c] Streamlabs data ################

# Map: (twitchName) -> (True or False if streamlabs exists)
def usingStreamLabs(twitchName):
	import requests
	url = 'https://twitch.streamlabs.com/%s/' % twitchName
	r = requests.get(url)
	if r.status_code == 200:
		return True
	else:
		return False

################ [1d I] Contact information - PayPal ################
def paypalInfo(twitchName):
	import urllib
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from random import randint
	import os
	import random
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	import requests
	import time
	from bs4 import BeautifulSoup
	import requests
	import re
	def human_type(element, text):
	    for char in text:
	        #time.sleep(random.randint(1,5)) #fixed a . instead of a ,
	        time.sleep(random.uniform(0, 1))
	        element.send_keys(char)
	    return
	def miniSleep():
		sleep(random.uniform(0, 1))
		return

	# Kill all chrome processes
	killChromeIfDigitalOcean()

	url = 'https://twitch.streamlabs.com/%s/' % (twitchName)
	try:
		driver = startSelenium()
		miniSleep()
		driver.get(url)
		sleep(randint(1,2))#1-5 seconds

		## (3a) Check to see if streamlabs setup exists for twitchName ##
		if len(driver.find_elements_by_css_selector('.button.button--action.button--lg')) > 0:
			if driver.find_elements_by_css_selector('.button.button--action.button--lg')[0].text != 'DONATE':
				# TERMINATE SESSION #
				driver.quit()
				print 'Terminated as session streamlabs not set up for twitchName'
				return 'Terminated as session streamlabs not set up for twitchName'
		else:
			driver.quit()
			print 'Terminated as session streamlabs not set up for twitchName (twitchname doesnt exist?)'
			return 'Terminated as session streamlabs not set up for twitchName (twitchname doesnt exist?)'

		## (3b) Check minimum donation amount ##
		donation = 25

		## (3c) Fill in form ##
		element = driver.find_element_by_name("name")
		human_type(element, "wambocombo87")

		## 3(d) Check for minimu donation amount ##
		element = driver.find_element_by_name("amount")
		human_type(element, str(donation))

		driver.find_element_by_css_selector('.button.button--action.button--lg').click()
		sleep(3)

		#TERMINATE SESSION#
		if (driver.find_element_by_css_selector('.button.button--action.button--lg').text == "DONATE"):
			# TERMINATE SESSION #
			driver.quit()
			print 'Terminated because costs too high or other donate related issue'
			return 'Terminated because costs too high or other donate related issue'

		## (3e) Click on 'submit donation' button ##
		miniSleep()
		#driver.find_element_by_css_selector('.button.button--lg.button--action').click()
		#driver.find_element_by_css_selector('.logo.logo-paypal.logo-paypal-gold').click()
		driver.find_element_by_css_selector('.button.button--action.button--lg').click()
		sleep(10)

		## [4] Get email address ##
		identifyingInformation = ""
		soup=BeautifulSoup(driver.page_source)
		potentialElements = soup.find_all("span", {"class":"ng-binding"})
		for element in potentialElements:
			if (element.text[:len("Cancel and return to ")] == "Cancel and return to "):
				identifyingInformation = element.text[len("Cancel and return to "):]

		## Return ##
		driver.quit()
		# If is email, return, otherwise return Unavailable
		if len(re.findall(r'[\w\.-]+@[\w\.-]+', identifyingInformation)) > 0:
			return identifyingInformation
		else:
			return ("Unavailable")
	except:
		return ("Unavailable")

################ [1d II] Contact information - Twitch channel (panels) ################
def twitchPanelsEmail(twitchName):
	import urllib
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from random import randint
	import os
	import random
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	import requests
	import time
	from bs4 import BeautifulSoup
	import requests
	import re
	def miniSleep():
		sleep(random.uniform(0, 1))
		return
	# Kill all chrome processes
	killChromeIfDigitalOcean()
	try:
		url = 'https://twitch.tv/%s/' % (twitchName)
		soup=getSoupFromUrl(url)
		panelsSoup = soup.find("div", {"class":"tw-flex tw-flex-column-reverse tw-flex-shrink-1 tw-flex-nowrap tw-mg-x-auto tw-pd-y-3 tw-md-flex-row"})
		panelsSoupString = str(panelsSoup)
		match = re.findall(r'[\w\.-]+@[\w\.-]+', panelsSoupString)
		if (len(match) > 0):
			return match[0]
		else:
			return 'Unavailable'
	except:
		return 'Unavailable'

################ [1e] Video's / VODS info ################
def getLast30DayVideos(twitchName):
	import requests
	import calendar
	import time
	# [1] Define 30 days (in epoch?)
	# [2] Continue to request videos until have surpassed the 30 day mark OR have reached all videos | publishedAt = "2015-07-13T08:29:03Z"
	def convertToEpoch(publishedAt):
		import time
		#date_time = '29.08.2011 11:05:02'
		pattern = '%Y-%m-%dT%H:%M:%SZ'
		epoch = int(time.mktime(time.strptime(publishedAt, pattern)))
		return epoch
	today = calendar.timegm(time.gmtime())
	thirtyDaysAgo = today - (30*24*60*60)
	videos = []
	# [it turns out that all videos = broadcast_type=archive + no broadcast_type indicated] -> We only want archive (auto archive past broadcasts - we don't want increasing fixed costs - more videos - to ruin analysis)
	# [2b] First API call - archive only
	url = "https://api.twitch.tv/kraken/channels/%s/videos?client_id=nrisqw9diqmthnvxx1rknb3wxzhwm2k&limit=100&broadcast_type=archive" % twitchName
	r = requests.get(url)
	jsonObject = r.json()
	seenOldVideo = False
	for video in jsonObject['videos']:
		# If video is less than 30 days old...
		if (convertToEpoch(video['published_at']) >= thirtyDaysAgo):
			videos.append(video)
		else:
			seenOldVideo = True
	# [2c] Continue API calls while haven't hit any videos older than 30 days - archive only
	def roundUp(x):
		import math
		return int(math.ceil(x / 100.0)) * 100
	total = jsonObject['_total']
	for i in range(roundUp(total)/100):
		if (seenOldVideo==False):
			offset = str((i+1)*100)
			url = "https://api.twitch.tv/kraken/channels/%s/videos?client_id=nrisqw9diqmthnvxx1rknb3wxzhwm2k&limit=100&broadcast_type=archive&offset=%s" % (twitchName, offset)
			r = requests.get(url)
			jsonObject = r.json()
			for video in jsonObject['videos']:
				if (convertToEpoch(video['published_at']) >= thirtyDaysAgo):
					videos.append(video)
				else:
					seenOldVideo = True
	# [3] Return total views, total number of videos, cumulative length of videos?
	videoCount = len(videos)
	cumulativeVideoLength = float(sum([int(video['length']) for video in videos]))/3600.0#hours
	totalViews = sum([int(video['views']) for video in videos])
	return videoCount, cumulativeVideoLength, totalViews

################ [1f] Video's / VODS info ################

## DO/OS agnostic soup ##
def getSoupFromUrl(url):
	from sys import platform
	from bs4 import BeautifulSoup
	import requests
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	from random import randint
	import os
	import random
	from pyvirtualdisplay import Display
	from selenium import webdriver 
	if platform == 'darwin':
		chromedriver = "/Users/brandonfreiberg/python-projects/chromedriver"
		os.environ["webdriver.chrome.driver"] = chromedriver
		driver = webdriver.Chrome(chromedriver)
	else:
		display = Display(visible=0, size=(800, 600))
		display.start()
		driver = webdriver.Chrome()
	driver.get(url)
	sleep(randint(2,3))#1-5 seconds
	soup=BeautifulSoup(driver.page_source)
	driver.quit()
	return soup

def startSelenium():
	from sys import platform
	from bs4 import BeautifulSoup
	import requests
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	from random import randint
	import os
	import random
	from pyvirtualdisplay import Display
	from selenium import webdriver 
	if platform == 'darwin':
		chromedriver = "/Users/brandonfreiberg/python-projects/chromedriver"
		os.environ["webdriver.chrome.driver"] = chromedriver
		driver = webdriver.Chrome(chromedriver)
	else:
		display = Display(visible=0, size=(800, 600))
		display.start()
		driver = webdriver.Chrome()
	return driver

## Kill all open chrome browser instances ##
def killChromeIfDigitalOcean():
	from sys import platform
	def killAllChromeDigitalOcean():
		import subprocess
		import os
		import signal
		ps = subprocess.Popen(['ps', 'aux', '--sort', '-rss'], stdout=subprocess.PIPE).communicate()[0]
		processes = ps.split('\n')
		processesSplit = [processesRow.split() for processesRow in processes[1:]]
		for process in processesSplit:
			if (('-nolisten' in process) and ('-screen' in process)):
				os.kill(int(process[1]), signal.SIGTERM)
		return 'Killed all Chrome processes'
	if platform == 'darwin':
		print ('Mac - not killing chrome instances')
	elif platform == 'linux' or platform == 'linux2':
		killAllChromeDigitalOcean()
	else:
		print ('Error')
	return

def sendEmail(fileToSend):
	import smtplib
	import mimetypes
	from email.mime.multipart import MIMEMultipart
	from email import encoders
	from email.message import Message
	from email.mime.audio import MIMEAudio
	from email.mime.base import MIMEBase
	from email.mime.image import MIMEImage
	from email.mime.text import MIMEText

	fileToSend = csvFilePath(fileToSend)

	emailfrom = "Endorse team"
	emailto = "brandon@endorse.gg"
	fileToSend = fileToSend
	username = "endorseggteam@gmail.com"
	password = "endorseggteam$$"

	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = emailto
	msg["Subject"] = "ENDORSE | " + fileToSend
	msg.preamble = "Streamer list"
	#newMarketers, oldMarketers = newSponsors(fileToSend)
	#text = defineText(newMarketers, oldMarketers)

	ctype, encoding = mimetypes.guess_type(fileToSend)
	if ctype is None or encoding is not None:
	    ctype = "application/octet-stream"

	maintype, subtype = ctype.split("/", 1)

	if maintype == "text":
	    fp = open(fileToSend)
	    # Note: we should handle calculating the charset
	    attachment = MIMEText(fp.read(), _subtype=subtype)
	    fp.close()
	elif maintype == "image":
	    fp = open(fileToSend, "rb")
	    attachment = MIMEImage(fp.read(), _subtype=subtype)
	    fp.close()
	elif maintype == "audio":
	    fp = open(fileToSend, "rb")
	    attachment = MIMEAudio(fp.read(), _subtype=subtype)
	    fp.close()
	else:
	    fp = open(fileToSend, "rb")
	    attachment = MIMEBase(maintype, subtype)
	    attachment.set_payload(fp.read())
	    fp.close()
	    encoders.encode_base64(attachment)
	attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
	msg.attach(attachment)
	#msg.attach(MIMEText(text))

	server = smtplib.SMTP("smtp.gmail.com:587")
	server.starttls()
	server.login(username,password)
	server.sendmail(emailfrom, emailto, msg.as_string())
	server.quit()
	return

def grabYouTubeFromTwitch(twitchName):
	import urllib
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from random import randint
	import os
	import random
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	import requests
	import time
	from bs4 import BeautifulSoup
	import requests
	import re
	def miniSleep():
		sleep(random.uniform(0, 1))
		return
	killChromeIfDigitalOcean()
	try:
		url = 'https://twitch.tv/%s/' % (twitchName)
		soup=getSoupFromUrl(url)
		panelsSoup = soup.find("div", {"class":"tw-flex tw-flex-column-reverse tw-flex-shrink-1 tw-flex-nowrap tw-mg-x-auto tw-pd-y-3 tw-md-flex-row"})
		links = panelsSoup.find_all("a")
		youTubeLinks = []
		for link in links:
			try:
				if 'youtube' in link['href'].lower():
					youTubeLinks.append(link['href'])
			except:
				print 'Error in youtube link href grab'
		if (len(youTubeLinks) > 0):
			return youTubeLinks[0]
		else:
			return 'Unavailable'
	except:
		return 'Unavailable'

#print getYouTubeChannelSubscribersFromLink(grabYouTubeFromTwitch(twitchName))

def getYouTubeChannelSubscribersFromLink(youTubeLink):
	import urllib
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from random import randint
	import os
	import random
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	import requests
	import time
	from bs4 import BeautifulSoup
	import requests
	import re
	def miniSleep():
		sleep(random.uniform(0, 1))
		return
	killChromeIfDigitalOcean()
	try:
		url = youTubeLink
		soup=getSoupFromUrl(url)
		youTubeSimpleEndpoints = soup.find_all("a", {"class":"yt-simple-endpoint style-scope yt-formatted-string"})
		youTubeSimpleEndpoint = youTubeSimpleEndpoints[-1]['href'][len('/user/'):]
		return youTubeSimpleEndpoint
	except:
		return 'Unavailable'

def socialBladeYouTubeViews(youTubeSimpleEndpoint):
	import urllib
	from time import sleep
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.keys import Keys
	from random import randint
	import os
	import random
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	import requests
	import time
	from bs4 import BeautifulSoup
	import requests
	import re
	def miniSleep():
		sleep(random.uniform(0, 1))
		return
	killChromeIfDigitalOcean()
	try:
		url = 'https://socialblade.com/youtube/user/%s' % (youTubeSimpleEndpoint)
		soup=getSoupFromUrl(url)
		socialBladeMetrics = soup.find_all("span", {"style":"color:#41a200;"})
		monthlyYouTubeViews = socialBladeMetrics[-1].text.replace(',','').replace('+','')
		return monthlyYouTubeViews
	except:
		return 'Unavailable'

#socialBladeYouTubeViews(getYouTubeChannelSubscribersFromLink(grabYouTubeFromTwitch(twitchName)))

################ [2] Run functions ################
def testFunction():
	print 'testing'
	return

# 1 - Grab everything from staging [Final], preStaging [Workshop]
# 2 - If len(staging) >= len(preStaging), do stuff
# 3 - Do stuff (until reach 50m)
# 4 - If len(preStaging) = len(staging), AND more data filled out - update
# n - Update staging - i.e., if len(current) >= len(staging), update staging
def runProgram():
	import json
	import timeit
	import time
	runStart = timeit.default_timer()
	# [0] Read in csv files #
	# [0a] preStaging
	csvFileNamePreStaging = 'streamersPreStaging.csv'
	csvFileNamePreStaging = csvFilePath(csvFileNamePreStaging)
	csvdataRowsPreStaging = readCSV(csvFileNamePreStaging)
	# [0b] Staging
	csvFileNameStaging = 'streamersStaging.csv'
	csvFileNameStaging = csvFilePath(csvFileNameStaging)
	csvdataRowsStaging = readCSV(csvFileNameStaging)

	# [1] Make sure that len(staging) >= len(preStaging), otherwise terminate #
	def lastFilledRow(csvdataRows):
		count = 0
		for i in range(len(csvdataRows))[1:]:
			if csvdataRows[i][9] != '':
				count = i
		return count

	if (len(csvdataRowsStaging) >= len(csvdataRowsPreStaging)) and (lastFilledRow(csvdataRowsStaging) >= lastFilledRow(csvdataRowsPreStaging)):
		# [2] Wipe preStaging clean (rather copy Staging as the new starting point) #
		csvdataRowsPreStaging = csvdataRowsStaging
		writeStreamersToCSV(csvFileNamePreStaging, csvdataRowsPreStaging)

		# [3] Set startup time
		start_time = time.time()

		# [4] Update each row
		for row in csvdataRowsPreStaging[1:]:
			## Stop after 50 minutes ##
			elapsed_time = time.time() - start_time
			if (elapsed_time <= 5*60):

				#### HERE I AM - RESUME WORK ####
				try:
					# Define variables
					rowStart = timeit.default_timer()
					twitchName = row[0]
					language = row[1]
					partner = row[6]
					# Today - only commence if (language = english)
					if ((language == 'en') and (row[9] == "")):
						# [1a] Monthly views
						row[9] = lastMonthsViewsTwinge(twitchName)
						# [1b] Hours streamed, Average concurrents, Game distribution
						games, monthlyHoursStreamed, gamesPlayed, averageConcurrentViewers = gameDistribution(twitchName)
						row[10] = monthlyHoursStreamed
						row[11] = averageConcurrentViewers
						row[18] = gamesPlayed
						if (len(games) >= 1):
							row[19] = games[0]['name']
							row[22] = games[0]['viewersPercentage']
						if (len(games) >= 2):
							row[20] = games[1]['name']
							row[23] = games[1]['viewersPercentage']
						if (len(games) >= 3):
							row[21] = games[2]['name']
							row[24] = games[2]['viewersPercentage']
						row[25] = json.dumps(games)
						# [1c] Streamlabs
						row[12] = usingStreamLabs(twitchName)
						# [1d] PayPal email
						if row[12] == True:
							row[13] = paypalInfo(twitchName)
						# [1e] Twitch panels email
						if ((row[13] == "") or (row[13] == "Unavailable") or (row[13] == "Terminated because costs too high or other donate related issue")):
							row[14] = twitchPanelsEmail(twitchName)
						# [1f] Video data
						videoCount, cumulativeVideoLength, totalViews = getLast30DayVideos(twitchName)
						row[15] = videoCount
						row[16] = cumulativeVideoLength
						row[17] = totalViews
						# [2] Write to csv
						#csvFileName = 'streamersNew.csv'
						#csvFileName = csvFilePath(csvFileName)
						#writeStreamersToCSV(csvFileName, csvdataRows)
						count += 1
						rowStop = timeit.default_timer()
						rowTime = rowStop - rowStart

						# [2] Write to csv
						csvFileNamePreStaging = 'streamersPreStaging.csv'
						csvFileNamePreStaging = csvFilePath(csvFileNamePreStaging)
						writeStreamersToCSV(csvFileNamePreStaging, csvdataRowsPreStaging)
						print str(count) + ', Saved ' + twitchName + ', Row runtime: ' + str(rowTime)
					else:
						print 'In the future, update monthly views, games etc. for existing references'
				except:
					print 'Error with certain twitchName'
			else:
				print 'Reached maximum time limit (50 minutes)'

	# [n] If preStaging > staging, update staging, otherwise email me error message #
	if (lastFilledRow(csvdataRowsPreStaging) > lastFilledRow(csvdataRowsStaging)):
		csvdataRowsStaging = csvdataRowsPreStaging
		writeStreamersToCSV(csvFileNameStaging, csvdataRowsStaging)

	# Return #
	runStop = timeit.default_timer()
	runTime = runStop - runStart
	print 'Total runtime: ' + str(runTime)
	return csvdataRowsPreStaging

import time
runProgram()
time.sleep(60)
sendEmail('streamersStaging.csv')
