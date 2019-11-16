import requests, json, os

# returns unused except for testing

def AddingEvent(request):
    bot_id = os.getenv('BOT_ID')
    
    request_json = request.get_json()
    
    if request_json["name"] != "StaySwole":
        data = json.dumps({"text" : request_json["text"], "bot_id": bot_id})
        send = requests.post("https://api.groupme.com/v3/bots/post", data=data)
        return f'AAA'
    else:
        return f'Hello World!'
