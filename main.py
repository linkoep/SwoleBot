from __future__ import print_function
from datetime import datetime, timedelta, date
import pickle
import os.path

import requests, json, os, random, sys, re
from google.cloud import firestore

from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

workouttypes = {
        "core" : ["core", "abs", "plank"],
        "upper" : ["upper", "chest", "shoulder", "tricep", "tris", "bicep", "push up", "strength", "lift"],
        "lower" : ["lower", "leg", "squat"],
        "cardio" : ["cardio", "run", "ran", "swim", "swam", "pool", "canaan", "ultisquash", "bike", "bicycle", "mile", "treadmill", "hiit", "track"],
        "skills" : ["skills", "throw", "threw", "canaan", "ultisquash", "ultimate", "frisbee"],
        "recovery" : ["recovery", "kit", "ice", "rest", "heat", "stretch", "yoga", "roll"]
        }

quotes = ["\"Core is 90% mental. That's a Curri quote, but I'm gonna keep saying it so all the freshmen think it's a me quote.\" - Calvin Jungreis",
        "\"If you're not gaining, you're losing. And if you're losing, you're not winning\" - Matt Brown",
        "\"If you think lifting is dangerous, try being weak. Being weak is dangerous.\" - Some guy on the internet",
        "\"Just. DO IT!\" - Shia LaBeauouauf",
        "\"Pain is just weakness leaving the body\" - Chesty Puller (Yes that's a real person)",
        "\"Frisbee is 20% mental, and 80% being mental\" - Some old dude on Trudge",
        "\"I am a gladiator! My body is a machine! I hit home runs! Because I'm F O C U S E D   A S   F U C K\" - Devin & Alec",
        "\"Fat and Ugly? Join a gym and just be ugly!\"",
        "\"Curls get the girls, but tri's get the guys ;)\"",
        "\"Motivation is what gets you started. Habit is what gets you going\"",
        "\"Square the fuck up or shut the fuck up\" - Brooks Wallace",
        "\"Sucking at something is the first step to being sorta good at something\" - Jake the Dog"
        ]

def sendMessage(message):
    bot_id = os.getenv("BOT_ID")
    data = json.dumps({"text": message, "bot_id": bot_id})
    requests.post("https://api.groupme.com/v3/bots/post", data=data)

def DatesFormat(event):
    startEvent = event["start"].get("dateTime", event["start"].get("date"))
    startDate = datetime.fromisoformat(startEvent)
    startString = startDate.strftime("%m/%d @ %H:%M")

    endEvent = event["end"].get("dateTime", event["end"].get("date"))
    endDate = datetime.fromisoformat(endEvent)
    endString = endDate.strftime("%H:%M")

    if endString == "00:00" and startDate.strftime("%H:%M") == "00:00":
        startString = startDate.strftime("%m/%d")
        return "\n    On {}: All Day".format(startString)
    else:
        return "\n    On {} - {}".format(startString, endString)

def addWorkout(msg_id, workout_type, unix_time, list_ids):
    db = firestore.Client()

    if workout_type == "recovery":
        # sendMessage("recovery")
        for user in list_ids:
            user_ref = db.collection("users").document(user)

            workout_ref = user_ref.collection("workouts").document(msg_id)
            workout_ref.set({
                "type" : workout_type,
                "unix_time" : unix_time,
                })

    else:
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
    for workouttype, keywords in workouttypes.items():
        for word in keywords:
            if re.search(
                    r"\b"						#word boundary
                    +word[:-1]					#all but last character
                    +r"(" + word[-1]+r"){0,2}"	#last character 0 (icing), 1 (core), or 2 (swimming) times
                    +r"(s|d|es|ed|ing)*"			#0 or more of the suffixes
                    +r"\b",						#word boundary
                    message):
                workouts.append(workouttype)
                if os.getenv("DEBUG", "false").lower() == "true":
                    print("matched {}".format(word))
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
            maxResults=n, singleEvents=True, orderBy="startTime").execute()

    events = events_result.get("items", [])

    if not events:
        statement = "No Upcoming Hours Found"
    else:
        statement = "Upcoming Events:"
        for event in events:
            statement += "\n" + event["summary"] + ":"
            statement += DatesFormat(event)
    return statement

def getKitHours():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.utcnow().isoformat() + "Z" # "Z" indicates UTC time
    events_result = service.events().list(calendarId="jqurd415p17322i9p9sqmq5g78@group.calendar.google.com", 
            timeMin=now, maxResults=4, singleEvents=True, orderBy="startTime").execute()

    events = events_result.get("items", [])

    if not events:
        statement = "No Upcoming Hours Found"
    else:
        statement = "Kit's Hours this week:"
        for event in events:
            statement += DatesFormat(event)
    return statement

def setKitHours(message):

    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    service = build("calendar", "v3", credentials=creds)


    created_event = service.events().quickAdd(
            calendarId='jqurd415p17322i9p9sqmq5g78@group.calendar.google.com',
            text=message).execute()


    sendMessage("Hours have been added")

def MorningMessage():
    statement = "Rise and Grind Workout Friends!\n"
    statement += getKitHours()
    statement += "\n"
    statement += FindEvents(3)
    statement += "\n"
    statement += "Here's some motivation:\n"
    statement += random.choice(quotes)
    sendMessage(statement)

def Resources(message):

    db = firestore.Client()

    if message.startswith("cardio"):
        doc = db.collection("resources").document("cardio").get()
        doc_dict = doc.to_dict()

    elif message.startswith("core"):
        doc = db.collection("resources").document("core").get()
        doc_dict = doc.to_dict()

    elif message.startswith("full body"):
        doc = db.collection("resources").document("full body").get()
        doc_dict = doc.to_dict()

    elif message.startswith("lower"):
        doc = db.collection("resources").document("lower").get()
        doc_dict = doc.to_dict()

    elif message.startswith("skills"):
        doc = db.collection("resources").document("skills").get()
        doc_dict = doc.to_dict()

    elif message.startswith("upper"):
        doc = db.collection("resources").document("upper").get()
        doc_dict = doc.to_dict()


    statement = "Resources:\n"
    for key in doc_dict:
        statement += "{}: {}\n".format(key, doc_dict[key])

    sendMessage(statement)

    # sendMessage(json.dumps(temp))

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
            # sendMessage("Calculating Leaderboard. Please Wait a Second...")
            getLeaderboardTop(5)
        elif message.startswith("event"):
            # sendMessage("Finding Events. Please Wait a Second...")
            sendMessage(FindEvents(5))
        elif message.startswith("get kit"):
            # sendMessage("Finding Kit's Hours. Please Wait a Second...")
            sendMessage(getKitHours())
        elif message.startswith("set kit"):
            setKitHours(message[4:])
        elif message.startswith('morning'):
            # sendMessage("Saying Good Morning. Please Wait a Second...")
            MorningMessage()
        elif message.startswith('resources'):
            # sendMessage("Saying Good Morning. Please Wait a Second...")
            Resources(message[10:])


        elif message.startswith('help'):
            statement = "Share a picture of you while working out and @ all others involved\n"
            statement += "Commands:\n"
            statement += "!bot leaderboard: See most active Trudge members\n"
            statement += "!bot events: See upcoming Trudge events\n"
            statement += "!bot get kit: See Kit's hours for that week\n"
            statement += "!bot set kit ____: Set a time that kit will be in\n"
            statement += "!bot resources ____: Gives resources for each workout\n"
            sendMessage(statement)
        elif message.startswith('update'):
            statement = "Patch Notes: (2/27)\n"
            statement += "   Rose from the dead\n"
            statement += "   Removed individual logs\n"
            sendMessage(statement)


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
                if debug.lower() == "true":
                    sendMessage("Logged a {} workout from {}!".format(temp, request_dict["name"]))

