#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time
import json
import datetime
import pytz
import urllib.request


class GoogleCalendarImport:


	def main(self):

		self.config = json.load(open(sys.argv[1]))
		print(self.config)
		self.fetch()

		for mappingItem in self.config["mapping"]:

			room = mappingItem["room"]
			result = self.parsePage(room)

			result["room"] = room
			result["date"] = self.config["date"]

			fnam = mappingItem["filename"]
			with open(fnam,"w") as outFile:
				json.dump(
					result,
					outFile,
					indent=2,
					ensure_ascii=False
				)


	def fetch(self):

		if True:
			f = open("import/gcal-sample.txt","r")
			self.page = f.read()
			f.close()

		else:
			req = urllib.request.urlopen(self.config["url"])
			self.page = str(req.read())

		self.lines = self.page.split("\n")


	def parsePage(self,room):

		result = {}
		result["agenda"] = []

		inside = False
		for line in self.lines:

			a = line.split(":")
			token = a[0].lower()
			try: value = a[1]
			except IndexError: value = ""
			line = line.lower()

			if line == "begin:vevent":
				inside = True
				desc = ""
				begin = None
				end = None

			elif token == "description" or token == "summary":
				if value == "": continue
				if desc != "": desc += " "
				desc += value

			elif token == "dtstart":
				begin = self.parseStampWithTodayCheck(value)

			elif token == "dtend":
				end = self.parseStampWithTodayCheck(value)

			elif line == "end:vevent":
				inside = False

				if desc == "": continue
				if begin is None: continue
				if end is None: end = begin

				result["agenda"].append({
					"begin": begin,
					"end": end,
					"desc": desc
				})


		return result


	def parseStampWithTodayCheck(self,value):

		ye = int(value[0:4])
		mo = int(value[4:6])
		da = int(value[6:8])
		ho = int(value[9:11])
		mi = int(value[11:13])
		se = int(value[13:15])
		utc =	datetime.datetime(ye,mo,da,ho,mi,se)

		tz = pytz.timezone("Europe/Bratislava")
		loc = utc.replace(tzinfo=pytz.utc).astimezone(tz)

		if self.config["date"] != loc.isoformat()[0:10]:
			return None

		stamp = loc.isoformat()[0:16]
		return stamp


if __name__ == "__main__":
	try:
		(GoogleCalendarImport()).main()
	except KeyboardInterrupt:
		print(" - aborted")
