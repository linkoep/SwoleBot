import requests, json, os

# returns unused except for testing

def AddingEvent(request):
    bot_id = os.getenv('BOT_ID')
    
    request_dict = request.get_json()
    
    if request_dict["id"] != bot_id:
        if len(request_dict["attachments"]) != 0:
            return f'BBB'
        else:
            data = json.dumps({"text" : request_dict["text"], "bot_id": bot_id})
            send = requests.post("https://api.groupme.com/v3/bots/post", data=data)
            return f'AAA'
    else:
        return f'Hello World!'
