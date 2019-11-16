import requests, json, os

# returns unused except for testing

def sendMessage(message):
	bot_id = os.getenv('BOT_ID')
	data = json.dumps({"text": message, "bot_id": bot_id})
    requests.post("https://api.groupme.com/v3/bots/post", data=data)

def AddingEvent(request):
	# Parse input and avoid self-replies
	request_dict = request.get_json()
	if request_dict["sender_type"] == 'bot':
            return 'Bot message. Do not reply'
        sendMessage(json.dumps(request_dict))

        # Respond to workout photos
        if len(request_dict["attachments"]) != 0:
