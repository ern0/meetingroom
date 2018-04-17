#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time
import json
import datetime


class Import:


	def main(self):

		configFileName = sys.argv[1]
		self.config = json.load(open(configFileName))

		now = datetime.datetime.now()
		self.date = (
			str(now.year)
			+ str(now.month).zfill(2)
			+ str(now.day).zfill(2)
		)

		outputDir = self.config["workdir"]
		try: os.makedirs(outputDir)
		except: pass

		fake = {
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

		for importItem in self.config["import"]:
			for mappingItem in importItem["mapping"]:
				room = mappingItem["room"]
				fake["room"] = room
				fake["date"] = self.date

				fnam = outputDir + "/agenda-data-" + room + ".json"
				with open(fnam,"w") as outFile:
					json.dump(fake,outFile)


if __name__ == "__main__":
	try:
		(Import()).main()
	except KeyboardInterrupt:
		print(" - aborted")
