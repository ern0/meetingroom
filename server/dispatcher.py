#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time
import json
import datetime
import subprocess


class Dispatcher:


	def main(self):

		self.about()
		self.loadConfig(sys.argv[1])
		self.createWorkDir()

		self.fetchImportData()


	def note(self,msg):

		msg = "dispatcher: " + msg

		if sys.exc_info()[1] is None:
			print(msg)
		else:
			print(msg + " - " + str( sys.exc_info()[1] ))


	def fatal(self,msg):

		self.note(msg)
		os._exit(1)


	def about(self):

		if len(sys.argv) == 2: return
		self.fatal("config not specified")


	def loadConfig(self,fnam):

		try:
			self.config = json.load(open(fnam))
		except json.decoder.JSONDecodeError:
			self.fatal("malformed json: " + fnam)

		self.configFileName = os.path.abspath(fnam)


	def createWorkDir(self):

		try: wd = self.config.workdir
		except: wd = "/tmp/meetingroom"

		try:
			os.makedirs(wd)
		except FileExistsError:
			pass
		except:
			self.fatal("failed to create workdir: " + wd)


	def updateStamp(self):

		now = datetime.datetime.now()
		self.stamp = (
			str(now.year)
			+ str(now.month).zfill(2)
			+ str(now.day).zfill(2)
		)


	def fetchImportData(self):

		self.updateStamp()
		for importItem in self.config["import"]:
			self.fetchImportItem(importItem)


	def fetchImportItem(self,importItem):

		self.noteFetchImportItem(importItem)
		if not importItem["active"]: return
		self.performFetchImportItem(importItem)


	def noteFetchImportItem(self,importItem):

		if importItem["active"]: importItemName = "perform"
		else: importItemName = "skip"

		importItemName += (
			" import"
			+ " app=" + importItem["app"]
			+ " url=" + importItem["url"]
		)

		self.note(importItemName)


	def performFetchImportItem(self,importItem):

		app = os.path.abspath( importItem["app"] )
		url = importItem["url"]

		subprocess.check_output([app,self.configFileName])
		print([app,self.configFileName])

		# check md5
		# call format app


if __name__ == "__main__":
	try:
		(Dispatcher()).main()
	except KeyboardInterrupt:
		print(" - aborted")
