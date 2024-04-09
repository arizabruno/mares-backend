from mailjet_rest import Client
import os

api_key = '****************************1234'
api_secret = '****************************abcd'

def send_reset_password_email(email: str, token: str):
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
    'Messages': [
        {
        "From": {
            "Email": "aziradev@gmail.com",
            "Name": "Bruno"
        },
        "To": [
            {
            "Email": "aziradev@gmail.com",
            "Name": "Bruno"
            }
        ],
        "Subject": "Greetings from Mailjet.",
        "TextPart": "My first Mailjet email",
        "HTMLPart": "<h3>Dear passenger 1, welcome to <a href='https://www.mailjet.com/'>Mailjet</a>!</h3><br />May the delivery force be with you!",
        "CustomID": "AppGettingStartedTest"
        }
    ]
    }
    result = mailjet.send.create(data=data)
