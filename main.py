from __future__ import print_function
import datetime
import pickle
import os.path
from google.auth import _helpers
from google.auth import credentials
from google.auth import exceptions
from google.oauth2 import _client

import requests, json, os
from google.cloud import firestore


core = ["core", "abs", "plank"]
upper = ["upper", "chest", "back", "shoulder", "tricep", "tri", "bicep", "push up"]
lower = ["lower", "leg", "squat"]
cardio =["cardio", "run", "ran", "swim", "swam", "pool", "canaan", "ultisquash", "bike", "bicycle"]
skills = ["skills", "throw", "threw", "canaan", "ultisquash", "ultimate", "frisbee"]
recovery = ["recovery", "kit", "ice", "rest", "heat", "stretch"]

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

	sendMessage( "Top {} all time: ".format(n))
	for person in top:
		sendMessage("{} => {} ".format(person.id, json.dumps(person.to_dict())))

def FindEvents():

	SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

	CLIENT_ID = os.getenv("CLIENT_ID")
	PROJECT_ID = os.getenv("PROJECT_ID")
	CLIENT_SECRET = os.getenv("CLIENT_SECRET")
	REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")


	creds = Credentials(None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)

	service = build('calendar', 'v3', credentials=creds)

	sendMessage("Good: 4")

	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	sendMessage("Getting the upcoming 10 events")
	events_result = service.events().list(calendarId='Trudge', timeMin=now,
										maxResults=10, singleEvents=True,
										orderBy='startTime').execute()

	sendMessage("Good: 5")

	events = events_result.get('items', [])

	sendMessage("Good: 6")

	if not events:
		sendMessage("No upcoming events found.")
	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		sendMessage(start, event["summary"])
		# print(start, event['summary'])

	# for event in events:
		# statement += event + "\n"

	# sendMessage(statement)

def AddingEvent(request):
	debug = os.getenv("DEBUG", "false")
		
	# Parse input and avoid self-replies
	request_dict = request.get_json()
	if request_dict["sender_type"] == "bot":
		return "Bot message. Do not reply"
	
	if debug.lower() == "true":
		sendMessage(json.dumps(request_dict))
	message = request_dict["text"]
	
	# Bot-commands
	if message.startswith('!bot '):
		message = message[5:]
		if message.startswith('leaderboard'):
			sendMessage("Calculating Leaderboard. Please Wait a Second...")
			getLeaderboardTop(5)
		elif message.startswith('events'):
			sendMessage("Finding Events. Please Wait a Second...")
			FindEvents()

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
