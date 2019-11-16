import requests, json, os

# returns unused except for testing

def AddingEvent(request):
    bot_id = os.getenv('BOT_ID')
    
    request_dict = request.get_json()
    
    if request_dict["sender_type"] != 'bot':
        if len(request_dict["attachments"]) != 0:
            return f'BBB'
        else:
            data = json.dumps({"text" : "{} sent by {} of type {}".format(request_dict["text"], request_dict["sender_id"], request_dict["sender_type"]), "bot_id": bot_id})
            send = requests.post("https://api.groupme.com/v3/bots/post", data=data)
            return f'AAA'
    else:
        return f'Hello World!'
