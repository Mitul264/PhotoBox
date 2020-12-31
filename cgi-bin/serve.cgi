#!/usr/bin/python2.7

import sys
import os
import re
import uuid
import urllib
import json
import time
import cgi

users = {} # dictionary that stores username and password
sessions = {}
locks = {} # stores locks so that two files are not deleted/uploaded at once
cookies = {} # will store all the cookies
fields = {}
directoryStructure = "cloudDb/"

# Get all the data from the DB
dataFile = open("textDb/userData.txt","r")
readStr = dataFile.read().strip()
if readStr != "":
    users = json.loads(readStr)
    dataFile.close()

# Get all the data from the DB
dataFile = open("textDb/sessions.txt","r")
readStr = dataFile.read().strip()
if readStr != "":
    sessions = json.loads(readStr)
    dataFile.close()

# Get all the data from the DB
dataFile = open("textDb/locks.txt","r")
readStr = dataFile.read().strip()
if readStr != "":
    locks = json.loads(readStr)
    dataFile.close()
# "REQUEST_METHOD" in os.environ
# os.environ['REQUEST_METHOD'] == "GET"
if("REQUEST_METHOD" in os.environ):
    if(os.environ['REQUEST_METHOD'] == "GET"):
        sendObj = {}
        sendStr = "ERROR"

        arguments = cgi.FieldStorage()
        user = arguments.getvalue("user")
        session = arguments.getvalue("session")
        newTab = arguments.getvalue("newTab")

        # arguments = {}
        # urlParameters = os.environ['QUERY_STRING'].strip().split("&")
        # for item in urlParameters:
        #     keyVal = item.split("=")
        #     arguments[keyVal[0]] = keyVal[1]
        #
        # user = arguments["user"]
        # session = arguments["session"]
        # newTab = arguments["newTab"]

        # user = "a"
        # session = "6d050b08-3356-4a10-b186-7d3bc08de83c"
        # newTab = "Yes"
        # if user doesnt have up to date data
        if user in sessions and session in sessions[user] and (sessions[user][session] == 1 or newTab == "Yes"):
            # if user doesnt have up to date data
            sendObj["info"] = "changed"
            imagesDict = {}
            loopDict = users[user]["photos"]
            for key in loopDict:
                dirPath = directoryStructure + user + "/" + key
                dataFile = open(dirPath,"r")
                readStr = dataFile.read().strip()
                imagesDict[key] = readStr
            sendObj["photos"] = imagesDict
            sendObj["links"] = loopDict
            # now user has up to date data
            sessions[user][session] = 0
            dataFile = open("textDb/sessions.txt","w")
            writeString = json.dumps(sessions)
            dataFile.write(writeString)
            dataFile.close()

        elif user in sessions and session in sessions[user] and sessions[user][session] == 0:
            # if user has up to date data
            sendObj["info"] = "unchanged"
        else:
            if user not in sessions:
                sendObj["info"] = "LogInPlease"
            if session in sessions[user]:
                sendObj["info"] = "LogInPlease"

        if len(sendObj) != 0:
            sendStr = json.dumps(sendObj)
        print ("Content-Type: text/plain")
        print ("Content-Length: "+str(len(sendStr))+"\n")
        print (sendStr)

    elif(os.environ['REQUEST_METHOD'] == "POST"):
        sendObj = {}
        sendStr = "ERROR"
        linkDir = "http://www-test.cs.umanitoba.ca/~patelm5/cgi-bin/shared.cgi?photoId="
        queryText = sys.stdin.readline()

        if not queryText:
            print ("Content-Type: text/plain\r\n")
            print ("ERROR")
        else:
            queryObj = json.loads(queryText)
            if(queryObj["command"] == "verify"):
                if queryObj["user"] in users and queryObj["user"] in sessions and queryObj["session"] in sessions[queryObj["user"]]:
                    sendObj["existance"] = 1
                else:
                    sendObj["existance"] = 0
            elif(queryObj["command"] == "add"):
                user = queryObj["user"]
                session = queryObj["session"]
                photoName = queryObj["photo"]
                photoData = queryObj["photodata"]
                uniqueLink = linkDir + str(uuid.uuid4())

                # if the same user is uploading or deleting something
                if user in locks:
                    # loop until the user is done
                    while(True):
                        #wait for some time
                        time.sleep(1)
                        # Get all the locks now
                        dataFile = open("textDb/locks.txt","r")
                        readStr = dataFile.read().strip()
                        if readStr != "":
                            locks = json.loads(readStr)
                            dataFile.close()
                        # if the user has not locked
                        if user not in locks:
                            # break and do our uploading
                            break
                    # else the other user session has still locked it, keep waiting

                # Outside the while loop Ill lock it now
                locks[user] = session
                # write my lock to lockdb
                dataFile = open("textDb/locks.txt","w")
                writeString = json.dumps(locks)
                dataFile.write(writeString)
                dataFile.close()

                # lets do our uploading now
                # check if users disk is not full
                numPhotos = len(users[user]["photos"])
                # There is space
                if(numPhotos < 10):
                    if photoName not in users[user]["photos"]:
                        # Lets keep the records first
                        users[user]["photos"][photoName] = uniqueLink
                        # add data to the directory
                        dirPath = directoryStructure + user + "/" + photoName
                        dataFile = open(dirPath,"w")
                        dataFile.write(photoData)
                        dataFile.close()
                        # we made a change to this users data, update in sessions
                        userSession = sessions[user]
                        for key in userSession:
                            userSession[key] = 1
                        sessions[user] = userSession
                        dataFile = open("textDb/sessions.txt","w")
                        writeString = json.dumps(sessions)
                        dataFile.write(writeString)
                        dataFile.close()
                        # update user records
                        dataFile = open("textDb/userData.txt","w")
                        writeString = json.dumps(users)
                        dataFile.write(writeString)
                        dataFile.close()
                        sendObj["info"] = "Yes"
                    else:
                        sendObj["info"] = "Duplicate"
                else:
                    sendObj["info"] = "Full"
                # I will unlock it now
                del locks[user]
                # write my unlock to lockdb
                dataFile = open("textDb/locks.txt","w")
                writeString = json.dumps(locks)
                dataFile.write(writeString)
                dataFile.close()

            elif(queryObj["command"] == "delete"):
                user = queryObj["user"]
                session = queryObj["session"]
                photoName = queryObj["photo"]
                # if the same user is uploading or deleting something
                if user in locks:
                    # loop until the user is done
                    while(True):
                        #wait for some time
                        time.sleep(1)
                        # Get all the locks now
                        dataFile = open("textDb/locks.txt","r")
                        readStr = dataFile.read().strip()
                        if readStr != "":
                            locks = json.loads(readStr)
                            dataFile.close()
                        # if the user has not locked
                        if user not in locks:
                            # break and do our uploading
                            break
                    # else the other user session has still locked it, keep waiting

                # Outside the while loop Ill lock it now
                locks[user] = session
                # write my lock to lockdb
                dataFile = open("textDb/locks.txt","w")
                writeString = json.dumps(locks)
                dataFile.write(writeString)
                dataFile.close()
                # prepare for deletion
                # check if users disk is not empty
                numPhotos = len(users[user]["photos"])
                # There is space
                if(numPhotos > 0):
                    if photoName in users[user]["photos"]:
                        # get the directory
                        dirPath = directoryStructure + user + "/" + photoName
                        # delete the image file
                        os.remove(dirPath)
                        # remove the record
                        del users[user]["photos"][photoName]
                        # we made a change to this users data, update in sessions
                        userSession = sessions[user]
                        for key in userSession:
                            userSession[key] = 1
                        sessions[user] = userSession
                        dataFile = open("textDb/sessions.txt","w")
                        writeString = json.dumps(sessions)
                        dataFile.write(writeString)
                        dataFile.close()
                        # update user records
                        dataFile = open("textDb/userData.txt","w")
                        writeString = json.dumps(users)
                        dataFile.write(writeString)
                        dataFile.close()
                        sendObj["info"] = "Yes"
                    else:
                        sendObj["info"] = "doesntExist"
                else:
                    sendObj["info"] = "empty"
                # I will unlock it now
                del locks[user]
                # write my unlock to lockdb
                dataFile = open("textDb/locks.txt","w")
                writeString = json.dumps(locks)
                dataFile.write(writeString)
                dataFile.close()




            if len(sendObj) != 0:
                sendStr = json.dumps(sendObj)
            print ("Content-Type: text/plain")
            print ("Content-Length: "+str(len(sendStr))+"\n")
            print (sendStr)


    else:
        print ("Content-Type: text/plain\r\n")
        print ("ERROR")
else:
    print ("Content-Type: text/plain\r\n")
    print ("ERROR")
