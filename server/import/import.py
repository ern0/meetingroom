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
		outputFileName = self.config["workdir"] + "/" + stamp + "/agenda-"

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

				fnam = outputFileName + room + ".json"
				with open(fnam,"w") as outfile:
					json.dump(fake,outfile)


if __name__ == "__main__":
	try:
		(Application()).main()
	except KeyboardInterrupt:
		print(" - aborted")
