#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os


class Render:


	def main(self):

		self.about()
		self.process(sys.argv[1],sys.argv[2])


	def about(self):

		if len(sys.argv) == 2: return

		print(
			os.path.basename(sys.argv[0])
			+ " <data.json> <output.png>"
		)
		os._exit(1)


	def process(self,jfn,rfn):

		self.jsonFileName = jfn
		self.resultFileName = rfn

		print("blah blah, processing... " + jfn + " => " + rnf)


if __name__ == "__main__":
	try:
		(Render()).main()
	except KeyboardInterrupt:
		print(" - aborted")
