#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os


class Render:


	def main(self):

		self.about()


	def about(self):
		if len(sys.argv) == 2: return
		print(
			os.path.basename(sys.argv[0])
			+ " <data.json> <output.png>"
		) 


if __name__ == "__main__":
	try:
		(Render()).main()
	except KeyboardInterrupt:
		print(" - aborted")