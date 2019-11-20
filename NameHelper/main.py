import requests, json, os
from google.cloud import firestore


def populateNames(request):
	debug = os.getenv("DEBUG", "false")
	access_token = os.getenv("ACCESS_TOKEN")
	group_id = os.getenv("GROUP_ID")
	before_id = os.getenv("BEFORE_ID")
		
	if debug.lower() == "true":
		print("Fetching last 50 messages")
	url = "https://api.groupme.com/v3/groups/"+group_id+"/messages?token="+access_token+"&limit=50"
	if before_id:
		url += ("&before_id="+before_id)
	response_object = requests.get(url)
	response = response_object.json()

	users = set()
	for message in response["response"]["messages"]:
		users.add((message["sender_id"], message["name"]))
	if debug.lower() == "true":
		print(users)

	db = firestore.Client()
	for user in users:
		user_ref = db.collection("users").document(user[0])
		user_ref.set({"name": user[1]}, merge=True)
	return "Recent message was " + response["response"]["messages"][0]["id"] + " and oldest message was " + response["response"]["messages"][49]["id"] 
