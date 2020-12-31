#!/usr/bin/python2.7

import os
import sys
import json
import re


sessions = {}
cookies = {} # will store all the cookies

# Get all the data from the DB
dataFile = open("textDb/sessions.txt","r")
readStr = dataFile.read().strip()
if readStr != "":
    sessions = json.loads(readStr)
    dataFile.close()

if("HTTP_COOKIE" in os.environ):
	for cookie in os.environ['HTTP_COOKIE'].split( ';' ):
		cookie = cookie.strip()
		aCookie = cookie.split('=',1)
		cookies[aCookie[0]] = aCookie[1]

if "guestid" in cookies and "sessionid" in cookies:
  if cookies["guestid"] in sessions:
    if cookies["sessionid"] in sessions[cookies["guestid"]]:
      del sessions[cookies["guestid"]][cookies["sessionid"]]
      dataFile = open("textDb/sessions.txt","w")
      writeString = json.dumps(sessions)
      dataFile.write(writeString)
      dataFile.close()

print "Content-type: text/html"
print "Set-Cookie: guestid="
print "Set-Cookie: sessionid="
print
print "<html><head>"
print "<title></title>"
print "<META HTTP-EQUIV=\"REFRESH\" CONTENT=\"0;URL=http://www-test.cs.umanitoba.ca/~patelm5/cgi-bin/identifier.cgi\">"
print "</head></html>"
