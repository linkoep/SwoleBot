import requests, json, os
from google.cloud import firestore


def populateNames(request):
	debug = os.getenv("DEBUG", "false")
	access_token = os.getenv("ACCESS_TOKEN")
	group_id = os.getenv("GROUP_ID")
		
	if debug.lower() == "true":
		print("Fetching last 50 messages")
	messages_response = requests.get("https://api.groupme.com/v3/groups/"+group_id+"/messages?token="+access_token+"&limit=50")
	messages = messages_response.json()
	print(messages)
	return messages
