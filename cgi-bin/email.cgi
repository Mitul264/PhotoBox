#!/usr/bin/python2.7

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
import os
import json
import sys


users = {} # dictionary that stores username and password
server = "localhost"
fromUser = 'PhotoBox <patelm5@cs.umanitoba.ca>'

dataFile = open("textDb/userData.txt","r")
readStr = dataFile.read().strip()
if readStr != "":
  users = json.loads(readStr)
  dataFile.close()

sendObj = {}
sendStr = "ERROR"

queryText = sys.stdin.readline()
if queryText:
  queryObj = json.loads(queryText)
  username = queryObj["user"]
  photo = queryObj["photo"]
  to = ['Recipient <'+queryObj["email"]+'>']
  filePath = "cloudDb/"+ username + "/" + photo
  namePhoto = photo.split(".")
  lenName = len(namePhoto)
  extension = namePhoto[lenName - 1]
  photoLink = users[username]["photos"][photo]
  # send an email
  subject = "Photo "+photo+" Sent by " + username + "! (Do not reply)"
  text = "Hello, \n\nI hope you are doing well, we have attached a photo that was shared by " + username + " from their PhotoBox! \n\nAlternatively, you can click on the link "+photoLink+" to view it on your browser.\n\nIf you would like to join PhotoBox click here http://www-test.cs.umanitoba.ca/~patelm5/index.html \n\nThanks\nPhotoBox Team"
  messageElement = MIMEMultipart()
  messageElement['from'] = fromUser
  messageElement['To'] = COMMASPACE.join(to)
  messageElement['Date'] = formatdate(localtime=True)
  messageElement['Subject'] = subject
  messageElement.attach(MIMEText(text))
  dataFile = open(filePath,"r")
  readStr = dataFile.read()
  dataFile.close()
  readStr = readStr.split(",",1)
  readStr = readStr[1].decode("base64")
  attachmentImg = MIMEImage(readStr, _subtype=extension)
  attachmentImg.add_header('Content-Disposition', 'attachment; filename="%s"'% photo)
  messageElement.attach(attachmentImg)
  smtp = smtplib.SMTP(server)
  smtp.sendmail(fromUser, to, messageElement.as_string() )
  smtp.close()
  sendObj["info"] = "Yes"
if len(sendObj) != 0:
    sendStr = json.dumps(sendObj)
print ("Content-Type: text/plain")
print ("Content-Length: "+str(len(sendStr))+"\n")
print (sendStr)
