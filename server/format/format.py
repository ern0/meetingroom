#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time
import json


class Application:


	def main(self):

		inputFileName = sys.argv[1]
		outputFileName = sys.argv[2]

		pass


if __name__ == "__main__":
	try:
		(Application()).main()
	except KeyboardInterrupt:
		print(" - aborted")
