#!/usr/bin/python2.7

import sys
import os
import re
import uuid
import urllib
import json

users = {} # dictionary that stores username and password
sessions = {}
cookies = {} # will store all the cookies
fields = {}
directoryStructure = "cloudDb/"

if("HTTP_COOKIE" in os.environ):
	for cookie in os.environ['HTTP_COOKIE'].split( ';' ):
		cookie = cookie.strip()
		aCookie = cookie.split('=',1)
		cookies[aCookie[0]] = aCookie[1]

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

def userHasSession(uName, sessionId):
	print "Content-type: text/html"
	print "Set-Cookie: guestid="+uName
	print "Set-Cookie: sessionid="+sessionId
	print
	print("<!DOCTYPE html><html><head>")
	print("<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css'>")
	print("<link href='https://fonts.googleapis.com/css?family=Ubuntu' rel='stylesheet'>")
	print("<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js'></script>")
	print("<script src='https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js'></script>")
	print("<script src='/~patelm5/js/view.js'></script>")
	print("<link rel='stylesheet' href='/~patelm5/css/viewStyle.css'>")
	print("<title>Browse Drive</title></head>")
	print("<body style='background-color: #e6e6e6'>")
	print("<nav class='navbar navbar-inverse' style='border-radius: 0px'>")
	print("<div class='container-fluid'>")
	print("<div class='navbar-header'>")
	print("<a class='navbar-brand' onclick='openNav()' href='#'>&plusb; PhotoBox&#174;</a></div>")
	print("<ul class='nav navbar-nav'>")
	print("<li><a href='#' onclick='showOuter(\"home\")'>Home</a></li>")
	print("<li><a href='#' onclick='showOuter(\"upload\")'>Upload</a></li>")
	print("<li><a href='/~patelm5/cgi-bin/forget.cgi'>Logout</a></li>")
	print("</ul></div></nav>")
	print("<div id='modalDiv'></div>")
	print("<div id='home' class='initialHide' style='text-align-last: center;'>")
	print("<h1 >PhotoBox&#174; For "+uName+"</h1><div>")
	print("<h3>Your Usage Quota</h3>")
	print("<p>There is a maximum of 10 files you can store</p>")
	print("<p id='usedSpace'>Used Space (BLACK): </p>")
	print("<p id='freeSpace'>Free Space (PURPLE): </p>")
	print("<div class='piechart'  id='myPieChart' onclick='openNav()'></div></div></div>")
	print("<div id='upload' class='initialHide' style='text-align-last: center;'>")
	print("<h1 >Upload An Image</h1>")
	print("<div class='file-input' style='border: dashed 2px #222;'>")
	print("<input id='uploadFile' type='file'>")
	print("<span class='button' style='background: #222;color: white;' >Choose</span>")
	print("<span id='fileLablel' class='label' style='opacity: unset;'>No file selected</label></div>")
	print("<button type='button' style='margin-left: 20px;background-color: black;color: white' class='btn btn-outline-dark' onclick='uploadImage()'>Upload</button>")
	print("<div id='theImageDisplay' class='uploadSect'>")
	print("<img id='dvPreview' src=''>	</img></div></div>")
	print("<div id='drawer' class='container'>")
	print("<div id='mySidenav' class='sidenav'>")
	print("<a href='javascript:void(0)' class='closebtn' onclick='closeNav()'>&times;</a></div>")
	print("<div id='main'></div></div></body></html>")

def mustLogIn():
	print("Content-type: text/html")
	print "Set-Cookie: guestid="
	print "Set-Cookie: sessionid="
	print
	print('<html>')
	print('<!--Login Template adapted from https://speckyboy.com/login-pages-html5-css/ -->')
	print('<head>')
	print('<link rel="stylesheet" href="/~patelm5/css/style.css">')
	print('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>')
	print('<link href="https://fonts.googleapis.com/css?family=Ubuntu" rel="stylesheet">')
	print('<script src="/~patelm5/js/identifier.js"></script>')
	print('<title>Sign in</title>')
	print('</head>')
	print('<body>')
	print('<h1 align="center" style="font-size: 3.0em" class="sign"><strong>Welcome To PhotoBox&#174;<strong></h1>')
	print('<div class="main">')
	print('<div id="signIn">')
	print('<p class="sign" align="center">Sign in</p>')
	print('<form class="form1" method="POST" action="/~patelm5/cgi-bin/identifier.cgi">')
	print('<input class="un " type="text" name = "username" align="center" placeholder="Username" required>')
	print('<input class="pass" type="password" name = "password" align="center" placeholder="Password" required><p align="center" style="color: red;font-size: 0.7em" >You must log in first!</p>')
	print('<input class="submit" type="submit" align="center" value="Sign in">')
	print('</form>')
	print('<p class="sign" style="font-size: 1.0em ;cursor: pointer;padding-top: 10px;text-decoration: underline;" align="center" onclick="clickedfor(\'#registerUser\', \'#signIn\')">Register<p>')
	print('</div>')
	print('<div id="registerUser" style="display: none">')
	print('<p class="sign" align="center">Register</p>')
	print('<form class="form1" method="POST" action="/~patelm5/cgi-bin/identifier.cgi">')
	print('<input class="un " type="text" align="center" name = "username" placeholder="Username" required>')
	print('<input class="pass" type="password" name = "password" align="center" placeholder="Password" required>')
	print('<input class="pass" type="password"  name = "confirmpassword" align="center" placeholder="Confirm Password" required>')
	print('<input class="submit" type="submit" align="center" value="Register">')
	print('</form>')
	print('<p class="sign" style="font-size: 1.0em ;cursor: pointer;padding-top: 10px;text-decoration: underline;" align="center" onclick="clickedfor(\'#signIn\', \'#registerUser\')">Sign In<p>')
	print('</div>')
	print('</div>')
	print('</body>')
	print('</html>')


if "guestid" in cookies and cookies["guestid"] in users and cookies["guestid"] in sessions and "sessionid" in cookies and cookies["sessionid"] in sessions[cookies["guestid"]]:
	userHasSession(cookies["guestid"], cookies["sessionid"])
else:
	queryText = sys.stdin.readline()
	if not queryText:
		mustLogIn()
	else:
		keyAndValues = queryText.split("&")	#split form fields
		for field in keyAndValues:
			keyValuePair = field.strip().split("=")	# key, value
			fields[keyValuePair[0]] = keyValuePair[1] # Store

		username = urllib.url2pathname(fields["username"])
		username = username.strip()
		username = username.replace('+', ' ')
		password = urllib.url2pathname(fields["password"])
		password = password.strip()
		password = password.replace('+', ' ')

		if(len(fields) == 3):
			confirmpassword = urllib.url2pathname(fields["confirmpassword"])
			confirmpassword = confirmpassword.strip()
			confirmpassword = confirmpassword.replace('+', ' ')
		if (len(fields) == 2 and (username not in users or (username in users and users[username]["password"] != password))):
			print("Content-type: text/html")
			print "Set-Cookie: guestid="
			print "Set-Cookie: sessionid="
			print
			print('<html>')
			print('<!--Login Template adapted from https://speckyboy.com/login-pages-html5-css/ -->')
			print('<head>')
			print('<link rel="stylesheet" href="/~patelm5/css/style.css">')
			print('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>')
			print('<link href="https://fonts.googleapis.com/css?family=Ubuntu" rel="stylesheet">')
			print('<script src="/~patelm5/js/identifier.js"></script>')
			print('<title>Sign in</title>')
			print('</head>')
			print('<body>')
			print('<h1 align="center" style="font-size: 3.0em" class="sign"><strong>Welcome To PhotoBox&#174;<strong></h1>')
			print('<div class="main">')
			print('<div id="signIn">')
			print('<p class="sign" align="center">Sign in</p>')
			print('<form class="form1" method="POST" action="/~patelm5/cgi-bin/identifier.cgi">')
			print('<input class="un " type="text" name = "username" align="center" placeholder="Username" required>')
			print('<input class="pass" type="password" name = "password" align="center" placeholder="Password" required><p align="center" style="color: red;font-size: 0.7em" >Username or Password Incorrect</p>')
			print('<input class="submit" type="submit" align="center" value="Sign in">')
			print('</form>')
			print('<p class="sign" style="font-size: 1.0em ;cursor: pointer;padding-top: 10px;text-decoration: underline;" align="center" onclick="clickedfor(\'#registerUser\', \'#signIn\')">Register<p>')
			print('</div>')
			print('<div id="registerUser" style="display: none">')
			print('<p class="sign" align="center">Register</p>')
			print('<form class="form1" method="POST" action="/~patelm5/cgi-bin/identifier.cgi">')
			print('<input class="un " type="text" align="center" name = "username" placeholder="Username" required>')
			print('<input class="pass" type="password" name = "password" align="center" placeholder="Password" required>')
			print('<input class="pass" type="password"  name = "confirmpassword" align="center" placeholder="Confirm Password" required>')
			print('<input class="submit" type="submit" align="center" value="Register">')
			print('</form>')
			print('<p class="sign" style="font-size: 1.0em ;cursor: pointer;padding-top: 10px;text-decoration: underline;" align="center" onclick="clickedfor(\'#signIn\', \'#registerUser\')">Sign In<p>')
			print('</div>')
			print('</div>')
			print('</body>')
			print('</html>')
		elif (len(fields) == 2 and username in users and users[username]["password"] == password):
			newSession = str(uuid.uuid4())
			if username in sessions:
				sessions[username][newSession] = 1
			else:
				sessions[username] = {newSession : 1}
			dataFile = open("textDb/sessions.txt","w")
			writeString = json.dumps(sessions)
			dataFile.write(writeString)
			dataFile.close()
			userHasSession(username, newSession)
		elif len(fields) == 3:
			if username in users or password != confirmpassword:
				if username in users:
					errorMsg = "User Already Exists, try another username"
				else:
					errorMsg = "Passwords Don't Match"

				print("Content-type: text/html")
				print "Set-Cookie: guestid="
				print "Set-Cookie: sessionid="
				print
				print('<html>')
				print('<!--Login Template adapted from https://speckyboy.com/login-pages-html5-css/ -->')
				print('<head>')
				print('<link rel="stylesheet" href="/~patelm5/css/style.css">')
				print('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>')
				print('<link href="https://fonts.googleapis.com/css?family=Ubuntu" rel="stylesheet">')
				print('<script src="/~patelm5/js/identifier.js"></script>')
				print('<title>Sign in</title>')
				print('</head>')
				print('<body>')
				print('<h1 align="center" style="font-size: 3.0em" class="sign"><strong>Welcome To PhotoBox&#174;<strong></h1>')
				print('<div class="main">')
				print('<div id="signIn" style="display: none">')
				print('<p class="sign" align="center">Sign in</p>')
				print('<form class="form1" method="POST" action="/~patelm5/cgi-bin/identifier.cgi">')
				print('<input class="un " type="text" name = "username" align="center" placeholder="Username" required>')
				print('<input class="pass" type="password"  name = "password" align="center" placeholder="Password" required>')
				print('<input class="submit" type="submit" align="center" value="Sign in">')
				print('</form>')
				print('<p class="sign" style="font-size: 1.0em ;cursor: pointer;padding-top: 10px;text-decoration: underline;" align="center" onclick="clickedfor(\'#registerUser\', \'#signIn\')">Register<p>')
				print('</div>')
				print('<div id="registerUser" >')
				print('<p style="padding-top: 20px;" class="sign" align="center">Register</p>')
				print('<form class="form1" method="POST" action="/~patelm5/cgi-bin/identifier.cgi">')
				print(' <input class="un " type="text" align="center" name = "username" placeholder="Username" required>')
				print('<input class="pass" type="password" name = "password" align="center" placeholder="Password" required>')
				print('<input style="margin-bottom: 10px;" class="pass" type="password"  name = "confirmpassword" align="center" placeholder="Confirm Password" required><p align="center" style="color: red;font-size: 0.7em" >{0}</p>'.format(errorMsg))
				print('<input class="submit" type="submit" align="center" value="Register">')
				print('</form>')
				print('<p class="sign" style="font-size: 1.0em ;cursor: pointer;padding-top: 10px;text-decoration: underline;" align="center" onclick="clickedfor(\'#signIn\', \'#registerUser\')">Sign In<p>')
				print('</div>')
				print('</div>')
				print('</body>')
				print('</html>')

			else:
				# make directory, add user to list, write to userfile and close
				# Create target directory & all intermediate directories if don't exists
				newDirectory = directoryStructure + username
				if not os.path.exists(newDirectory):
					os.makedirs(newDirectory)
					users[username] = {}
					users[username]["password"] = password
					users[username]["photos"] = {}
					dataFile = open("textDb/userData.txt","w")
					writeString = json.dumps(users)
					dataFile.write(writeString)
					dataFile.close()
					newSession = str(uuid.uuid4())
					if username in sessions:
						sessions[username][newSession] = 1
					else:
						sessions[username] = {newSession : 1}
					dataFile = open("textDb/sessions.txt","w")
					writeString = json.dumps(sessions)
					dataFile.write(writeString)
					dataFile.close()
					userHasSession(username, newSession)
				else:
					mustLogIn()
		else:
			mustLogIn()
