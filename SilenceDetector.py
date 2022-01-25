"""
Author: Harry Williams
A simple script for sending alerts on a continuous GPIO pulse.
This will send emails or notifcations via Pushover.
This was originally written to be used with a sonifex RB-SD1 Silence detector but it could be adapted to work with many other things!
"""

import RPi.GPIO as GPIO
import time
import smtplib
import http.client, urllib

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


PushoverIDFile = r"Path to file containing Pushover ID's"
PushoverAPIToken = "Your Pushover API Token"

# For this to work you must allow low security apps in gmail
gmailUsername = "Your Gmail Username"
gmailPassword = "Your Gmail Password"

def sendNotication(alarmState):
    if(alarmState == 1): #AlarmTripped
        sendPushover("Silence Detector Tripped") #Send Pushover Notification on alarm
        sendEmail("Silence Detector Tripped!", "The silence detector has tripped. The backup CD Player should be live.\nAnother notifcation will be sent once this issue is resolved!\nAlarm tripped at : ")
    if(alarmState == 0): #Alarm Reset
        sendPushover("Silence Detector Reset") #Send Pushover Notification on Reset
        sendEmail("Silence Detector Reset", "The issue that tripped the silence detector has since been resolved.\nRegular operation has been resumed.\nResolved at ")

def sendPushover(message):
    f = open(PushoverIDFile, "r")
    length = 0
    for x in f:  #Will loop for as many ID's in the file defined in "PushoverIDFile"
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": PushoverAPIToken,
            "user": x,
            "message": message,
            #"sound": "gamelan", Uncomment this line to force a sound for notifcations
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        print("Send notification to user id ",x)
        length += 1
    f.close()
    print("Send a total of ", length, " notificaitons")

def sendEmail(messageSubject, messageBody):

     

    
    to = ['testemail@testemail.com', 'example@exampleemail.com'] # List email addresses here
    subject = messageSubject
    body = messageBody + time.localtime()[2] + time.localtime()[1] + time.localtime()[3] + time.localtime()[4] + time.localtime()[5]

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (gmailUsername, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmailUsername, gmailPassword)
        smtp_server.sendmail(gmailUsername, to, email_text)
        smtp_server.close()
        print ("Email sent!")
    except Exception as ex:
        print ("That didn't quite work: ",ex)

previousAlarmState = 0
currentAlarmState = 0

while(True):
    if GPIO.input(10):
        currentAlarmState = 1
    else:
        currentAlarmState = 0
    
    if(previousAlarmState != currentAlarmState):
        sendNotication(currentAlarmState)
    previousAlarmState = currentAlarmState
    time.sleep(1)