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
		workouts.append("unkown")

	return workouts


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

		for temp in typeOfWorkout:
			addWorkout(request_dict["id"], temp, request_dict["created_at"], names)
			sendMessage("Logged a {} workout from {}!".format(temp, request_dict["name"]))
