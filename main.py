import requests, json, os
from google.cloud import firestore

core = ["core", "abs"]
upper = ["upper"]
lower = ["lower", "leg", "legs"]
cardio =["cardio", "run", "ran"]
skills = ["skills", "threw"]


def sendMessage(message):
	bot_id = os.getenv("BOT_ID")
	data = json.dumps({"text": message, "bot_id": bot_id})
	requests.post("https://api.groupme.com/v3/bots/post", data=data)

def addWorkout(msg_id, workout_type, unix_time, list_ids):
    db = firestore.Client()

    for user in list_ids:
        user_ref = db.collection("users").document(user)
        workout_ref = user_ref.collection("workouts").document(msg_id)
        workout_ref.set({
            "type" : workout_type,
            "unix_time" : unix_time,
        })
    
def WorkOutType(message):
	for word in core:
		if message.find(word) != -1:
			return "core"
	for word in upper:
		if message.find(word) != -1:
			return "upper"
	for word in lower:
		if message.find(word) != -1:
			return "lower"
	for word in cardio:
		if message.find(word) != -1:
			return "cardio"
	for word in skills:
		if message.find(word) != -1:
			return "skills"
	return "unkown"

def AddingEvent(request):
	# Parse input and avoid self-replies
	request_dict = request.get_json()
	if request_dict["sender_type"] == "bot":
		return "Bot message. Do not reply"
	
	# sendMessage(json.dumps(request_dict))

	names = [request_dict["sender_id"]]

	imageFound = False
	for attachment in request_dict["attachments"]:
		if attachment["type"] == "mentions":
			names.extend(set(attachment["user_ids"]))
		elif attachment["type"] == "image":
			imageFound = True



	if imageFound:

		typeOfWorkout = WorkOutType(request_dict["text"].lower())
        addWorkout(request_dict["id"], typeOfWorkout, request_dict["created_at"], names)
        sendMessage("Logged a {} workout from {}!".format(typeOfWorkout, request_dict["name"]))
