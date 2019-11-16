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
            

                #statement = ""
#
                #names = []
                #i = 0;
#
                ## statement += str(request_dict["text"].find("@", i))
#
                #while (request_dict["text"].find('@', i) != -1):
                        #j = request_dict["text"].find('@', i+1)
#
                        #if j != -1:
                                #names.append(request_dict[i:j-2])
                        #else:
                                #names.append(request_dict[i:])
#
                        #i = j
#
                #
                #for temp in names:
                        #statement += str(temp) + " "
#
                #statement += " " + request_dict["text"]
                #
                #sendMessage(statement)
