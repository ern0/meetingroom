#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import json


class Format:


	def main(self):

		inputFileName = sys.argv[1]
		outputFileName = sys.argv[2]

		print("format raw=" + inputFileName + " fmt=" + outputFileName)

		result = [
			{ "stamp":"07:00", "desc":"", "join":False, "hilite":False },
			{ "stamp":"07:30", "desc":"", "join":False, "hilite":False },
			{ "stamp":"08:00", "desc":"", "join":False, "hilite":True },
			{ 
				"stamp":"08:30", "desc":"Long, boring meeting",  
				"join":True, "hilite":False 
			},
			{ 
				"stamp":"", "desc": "with long description", 
				"join":False, "hilite":False 
			},
			{ "stamp":"09:30", "desc":"", "join":False, "hilite":False },
			{ 
				"stamp":"10:00", "desc":"Actual meeting", 
				"join":False, "hilite":True 
			},
			{ "stamp":"10:30", "desc":"", "join":False, "hilite":False },
			{ "stamp":"11:00", "desc":"", "join":False, "hilite":False }
		]

		with open(outputFileName,"w") as outFile:
			json.dump(result,outFile,indent=2)


if __name__ == "__main__":
	try:
		(Format()).main()
	except KeyboardInterrupt:
		print(" - aborted")
