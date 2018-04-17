#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time
import json
import datetime
import random


class Import:


	def main(self):

		now = datetime.datetime.now()
		self.date = (
			str(now.year)
			+ str(now.month).zfill(2)
			+ str(now.day).zfill(2)
		)

		result = {
			"agenda": [

				{
					"begin": "10:00",
					"end": "10:30",
					"desc": "This is a meeting"
				},
				{
					"begin": "12:00",
					"end": "13:30",
					"desc": "This is another meeting"
				}

			]
		}

		importItem = json.load(open(sys.argv[1]))

		for mappingItem in importItem["mapping"]:

			room = mappingItem["room"]
			fnam = mappingItem["filename"]

			result["room"] = room
			result["date"] = self.date

			# simulate some change
			if room == "kilo":
				r = str(random.randrange(300))
				result["agenda"][0]["desc"] += " - " + r

			with open(fnam,"w") as outFile:
				json.dump(result,outFile)


if __name__ == "__main__":
	try:
		(Import()).main()
	except KeyboardInterrupt:
		print(" - aborted")
