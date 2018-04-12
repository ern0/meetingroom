#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os

from importmodule import importmodule
import render.render


class Application:


	def main(self):

		self.about()
		self.loadConfig(sys.argv[1])


	def fatal(self,msg):
		print(msg)
		os._exit(1)


	def about(self):

		if len(sys.argv) == 2: return

		self.fatal(
			os.path.basename(sys.argv[0])
			+ " <config.json>"
		)


	def loadConfig(self,fnam):

		try:
			self.config = importmodule(fnam)
		except:
			self.fatal(
				"bad config: " 
				+ fnam 
				+ " - "
				+ str( sys.exc_info()[1] )
			)


		print(self.config.imports)
		print(self.config.devices)


if __name__ == "__main__":
	try:
		(Application()).main()
	except KeyboardInterrupt:
		print(" - aborted")
