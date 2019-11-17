import requests, json, os
from google.cloud import firestore


def populateNames(request):
	debug = os.getenv("DEBUG", "false")
	access_token = os.getenv("ACCESS_TOKEN")
	group_id = os.getenv("GROUP_ID")
		
	if debug.lower() == "true":
		print("Fetching last 50 messages")
	response_object = requests.get("https://api.groupme.com/v3/groups/"+group_id+"/messages?token="+access_token+"&limit=50")
	response = response_object.json()
	users = set()
	for message in response["response"]["messages"]:
		users.add((message["sender_id"], message["name"]))
	if debug.lower() == "true":
		print(users)
	return "Done!"
