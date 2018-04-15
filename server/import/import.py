#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time
import json


class Application:


	def main(self):

		configFileName = sys.argv[1]
		stamp = sys.argv[2]

		self.config = json.load(open(configFileName))

		outputDir = self.config["workdir"] + "/" + stamp
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
				fake["stamp"] = stamp

				fnam = outputDir + "/agenda-" + room + ".json"
				with open(fnam,"w") as outFile:
					json.dump(fake,outFile)


if __name__ == "__main__":
	try:
		(Application()).main()
	except KeyboardInterrupt:
		print(" - aborted")
