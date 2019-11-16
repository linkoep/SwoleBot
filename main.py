import requests, json, os

# returns unused except for testing

def AddingEvent(request):
	bot_id = os.getenv('BOT_ID')
	
	request_dict = request.get_json()
	
	if request_dict["sender_type"] != 'bot':
		if len(request_dict["attachments"]) != 0:

			statement = "AAA"

			names = []
			i = 0;
			while (request_dict["text"].find('@', i) != -1):
				j = request_dict["text"].find('@', i+1)

				if j != -1:
					names.append(request_dict[i:j-2])
				else:
					names.append(request_dict[i:len(request_dict)])

				statement += "i: " + i + " j; " + j
				data = json.dumps({"text": statement, "bot_id": bot_id})
				requests.post("https://api.groupme.com/v3/bots/post", data=data)
				
				i = j

			for temp in names:
				statement += temp + " ";

			statement += " " + request_dict["text"];

			# statement = "{} sent by {} of type {}".format(request_dict["text"], request_dict["sender_id"], request_dict["sender_type"])
	
			data = json.dumps({"text": statement, "bot_id": bot_id})
			requests.post("https://api.groupme.com/v3/bots/post", data=data)
