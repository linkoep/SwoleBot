from __future__ import print_function
from datetime import datetime, timedelta
import pickle
import os.path

import requests, json, os, random, sys
from google.cloud import firestore

from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

core = ["core", "abs", "plank"]
upper = ["upper", "chest", "back", "shoulder", "tricep", "tri", "bicep", "push up"]
lower = ["lower", "leg", "squat"]
cardio =["cardio", "run", "ran", "swim", "swam", "pool", "canaan", "ultisquash", "bike", "bicycle"]
skills = ["skills", "throw", "threw", "canaan", "ultisquash", "ultimate", "frisbee"]
recovery = ["recovery", "kit", "ice", "rest", "heat", "stretch"]

quotes = ["\"Core is 90% mental. That's a Curri quote, but I'm gonna keep saying it so all the freshmen think it's a me quote.\" - Calvin Jungreis",
        "\"If you're not gaining, you're losing. And if you're losing, you're not winning\" - Matt Brown",
        "\"If you think lifting is dangerous, try being weak. Being weak is dangerous.\" - Some guy on the internet",
        "\"Just. DO IT!\" - Shia LaBeauouauf"]

def sendMessage(message):
	bot_id = os.getenv("BOT_ID")
	data = json.dumps({"text": message, "bot_id": bot_id})
	requests.post("https://api.groupme.com/v3/bots/post", data=data)

def addWorkout(msg_id, workout_type, unix_time, list_ids):
	db = firestore.Client()

	for user in list_ids:
		user_ref = db.collection("users").document(user)

		user_ref.set({"num_workouts": firestore.Increment(1)}, merge=True)
		workout_ref = user_ref.collection("workouts").document(msg_id)
		workout_ref.set({
			"type" : workout_type,
			"unix_time" : unix_time,
		})
	
def WorkOutType(message):
	workouts = []

	for word in core:
		if message.find(word) != -1:
			workouts.append("core")
			break
	for word in upper:
		if message.find(word) != -1:
			workouts.append("upper")
			break
	for word in lower:
		if message.find(word) != -1:
			workouts.append("lower")
			break
	for word in cardio:
		if message.find(word) != -1:
			workouts.append("cardio")
			break
	for word in skills:
		if message.find(word) != -1:
			workouts.append("skills")
			break
	for word in recovery:
		if message.find(word) != -1:
			workouts.append("recovery")
			break
	if len(workouts) == 0:
		workouts.append("unknown")

	return workouts

def getLeaderboardTop(n):
	db = firestore.Client()
	top = db.collection("users").order_by("num_workouts", direction=firestore.Query.DESCENDING).limit(n).stream()

	statement = "Top {} all time:\n".format(n)
	i = 1
	for person in top:
		person_dict = person.to_dict()
		statement += "{}.) {} with {} workouts\n".format(i, person_dict.get("name", "unknown"), person_dict["num_workouts"])
		i+=1 
	sendMessage(statement)


def FindEvents(n):
	creds = None
	if os.path.exists("token.pickle"):
		with open("token.pickle", "rb") as token:
			creds = pickle.load(token)
	service = build("calendar", "v3", credentials=creds)

	# Call the Calendar API
	now = datetime.utcnow().isoformat() + "Z" # "Z" indicates UTC time
	events_result = service.events().list(calendarId="primary", timeMin=now,
										maxResults=n, singleEvents=True,
										orderBy="startTime").execute()

	events = events_result.get("items", [])

	if not events:
		statement = "No upcoming events found."
	else:
		statement = "Upcoming events:"
		for event in events:
			start = event["start"].get("dateTime", event["start"].get("date"))
			statement += "\n" + event["summary"] + " @ " + str(start)
	return statement

def getKitHours():
	creds = None
	if os.path.exists("token.pickle"):
		with open("token.pickle", "rb") as token:
			creds = pickle.load(token)
	service = build("calendar", "v3", credentials=creds)

	# Call the Calendar API

	"""
	now = datetime.now()
	temp = now - timedelta(hours=5)
	sendMessage(temp.isoformat())

	events_result = service.events().list(calendarId="jqurd415p17322i9p9sqmq5g78@group.calendar.google.com", 
		timeMin=datetime.now(), maxResults=10, orderBy="startTime").execute()
	"""

	now = datetime.utcnow().isoformat() + "Z" # "Z" indicates UTC time
	events_result = service.events().list(calendarId="jqurd415p17322i9p9sqmq5g78@group.calendar.google.com", 
		timeMin=now, maxResults=4, singleEvents=True, orderBy="startTime").execute()





	events = events_result.get("items", [])

	if not events:
		statement = "No hours uploaded"
	else:
		statement = "Kit's Hours this week:"
		for event in events:
			start = str(event["start"].get("dateTime", event["start"].get("date")))
			# temp = start, event["summary"]
			# print(start, event["summary"])
			# statement += "\n" + start

			statement += "\nOn {}/{}/{} @ {}:{}".format(start[0:4], start[6:8], start[10:12], start[14:16], start[18:20])

	return statement

def setKitHours(message):

	creds = None
	if os.path.exists("token.pickle"):
		with open("token.pickle", "rb") as token:
			creds = pickle.load(token)
	service = build("calendar", "v3", credentials=creds)

	# d.isoformat()

	# set Kit's Hours 11/18/2019 09:30-14:30

	"""
	i = message.find("/")
	if i == -1:
		return "Invalid Input"

	month = int(message[i-2:i])
	day = int(message[i+1:i+3])
	year = int(message[i+4:i+8])

	j = message.find(":", i)
	if j == -1:
		return "Invalid Input"

	startHour = int(message[j-2:j])
	startMin = int(message[j+1:j+3])

	k = message.find(":", j+1)
	if k == -1:
		return "Invalid Input"

	endHour = int(message[k-2:k])
	endMin = int(message[k+1:k+3])

	start = datetime(year, month, day, startHour, startMin, 0, 0)
	end = datetime(year, month, day, endHour, endMin, 0, 0)
	
	event = {
		"summary": "Kit's Hours",
		"location": "Armory",
		"description": "Go be healed",
		"start": {
			"date": start.isoformat(),
			"timeZone": "America/New_York",
		},
		"end": {
			"date": end.isoformat(),
			"timeZone": "America/New_York",
		},
	}
	"""

	event = {
		"summary": "Kit's Hours",
		"location": "Armory",
		"description": "Go be healed",
		"start": {
			"date": "2019-08-18T09:00",
			"timeZone": "America/New_York",
		},
		"end": {
			"date": "2019-08-18T12:30",
			"timeZone": "America/New_York",
		},
	}

	event = service.events().insert(calendarId="jqurd415p17322i9p9sqmq5g78@group.calendar.google.com", body=event).execute()

	sendMessage("Hours have been added")



def MorningMessage():
	statement = "Good Morning Trudge!\n"
	statement += getKitHours()
	statement += "\n"
	statement += FindEvents(3)
	statement += "\n"
	statement += "Here's some motivation:\n"
	statement += random.choice(quotes)
	sendMessage(statement)
	
def AddingEvent(request):
	debug = os.getenv("DEBUG", "false")
		
	# Parse input and avoid self-replies
	request_dict = request.get_json()
	if not request_dict:
		print("Forcing JSON Conversion", file=sys.stderr)
		request_dict = request.get_json(force=True)
	if request_dict["sender_type"] == "bot":
		return "Bot message. Do not reply"
	
	if debug.lower() == "true":
		sendMessage(json.dumps(request_dict))
	message = request_dict["text"].lower()
	
	# Bot-commands
	if message.startswith("!bot "):
		message = message[5:]
		if message.startswith("leaderboard"):
			sendMessage("Calculating Leaderboard. Please Wait a Second...")
			getLeaderboardTop(5)
		elif message.startswith("events"):
			sendMessage("Finding Events. Please Wait a Second...")
			sendMessage(FindEvents(10))
		elif message.startswith("get kit"):
			sendMessage("Finding Kit's Hours. Please Wait a Second...")
			sendMessage(getKitHours())
		elif message.startswith("set kit"):
			setKitHours(message)
		elif message.startswith('morning'):
			sendMessage("Saying Good Morning. Please Wait a Second...")
			MorningMessage()

	# Non bot-commands
	else: 
		names = [request_dict["sender_id"]]
		imageFound = False
		for attachment in request_dict["attachments"]:
			if attachment["type"] == "mentions":
				names.extend(set(attachment["user_ids"]))
			elif attachment["type"] == "image":
				imageFound = True
	
		if imageFound:
			typeOfWorkout = WorkOutType(request_dict["text"].lower())
	
			for temp in typeOfWorkout:
				addWorkout(request_dict["id"], temp, request_dict["created_at"], names)
				sendMessage("Logged a {} workout from {}!".format(temp, request_dict["name"]))
