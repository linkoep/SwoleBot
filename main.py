import requests, json, os

# returns unused except for testing

def sendMessage(message):
	bot_id = os.getenv('BOT_ID')
	data = json.dumps({"text": message, "bot_id": bot_id})
	requests.post("https://api.groupme.com/v3/bots/post", data=data)

def addWorkout(msg_id, workout_type, unix_time, list_ids):
    db = firestore.Client()

    for user in list_ids:
        workout = db.collection('users').document(user).collection('workouts').document(msg_id)
        workout.set({
            'type' : workout_type,
            'unix_time' : unix_time,
            'with' : list_ids
        })
    

def AddingEvent(request):
	# Parse input and avoid self-replies
	request_dict = request.get_json()
	if request_dict["sender_type"] == 'bot':
		return 'Bot message. Do not reply'
	
	# sendMessage(json.dumps(request_dict))

	names = [request_dict["sender_id"]]

	imageFound = False
	typeOfWorkOut = " "
	for attachment in request_dict["attachments"]:
		if attachment["type"] == "mentions":
			names.append(attachment["user_ids"])
		elif attachment["type"] == "image":
			imageFound = True



	if imageFound:
		sendMessage("Good")




