import os
import requests
from flask import Flask, request, jsonify

# Web service endpoint accpeting get requests to trigger a function sending
# a message and photo to an endpoint of Telegram messenger Bot API.
# The message is forwarded to a specified Telegram chat
app = Flask(__name__)

# Definition of the web service endpoint
@app.route('/notificationRequest', methods=['GET'])
def photoRequest():
    try:
        sendPhoto()
        return jsonify({'result': True})
    except:
        print('Can not send photo to ...')
        return jsonify({'result': False})


def sendPhoto():
	#URL of the Telegram API. <token> has to be replaced by actual token.
    url = 'https://api.telegram.org/bot<token>/sendPhoto'
    path = "./pictures"

    #Get the last photo taken by the camera
    paths = []
    for file in os.listdir(path):
        paths.append(os.path.join(path, file))
    paths.sort()
    files= {'photo': open(paths[-1], 'rb')}

    #Specify chat Id and message text
    print('could open imgage')
    data = {
      'chat_id': '<chatId>',
      'caption': 'Hey, it seems nemo needs help. Please check in on him!'
    }

    #Send HTTP POST
    r = requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)


if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=54321)
