#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time
import json
import datetime
import subprocess
import fnmatch


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

		self.reqPrefix = os.path.abspath(
			self.config["workdir"] 
			+ "/agenda-request-"
		)
		self.dataPrefix = os.path.abspath(
			self.config["workdir"] 
			+ "/agenda-data-"
		)


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

		importIndex = 0
		for importItem in self.config["import"]:
			importItem["index"] = importIndex
			importItem["production"] = self.config["production"]
			self.fetchImportItem(importItem)
			importIndex += 1

		for importItem in self.config["import"]:
			for mappingItem in importItem["mapping"]:
				fnam = self.mkDataFnam( mappingItem["room"] )
				print(fnam)


	def mkReqFnam(self,index):
		return self.reqPrefix + str(index) + ".json"


	def mkDataFnam(self,room):
		return self.dataPrefix + room + ".json"


	def fetchImportItem(self,importItem):

		self.noteFetchImportItem(importItem)
		if not importItem["active"]: return
		self.performFetchImportItem(importItem)


	def noteFetchImportItem(self,importItem):

		if importItem["active"]: importItemName = "perform"
		else: importItemName = "skip"

		importItemName += (
			" import"
			+ " fetcher=" + importItem["fetcher"]
			+ " url=" + importItem["url"]
		)

		self.note(importItemName)


	def performFetchImportItem(self,importItem):

		# insert output file names into config
		for mappingItem in importItem["mapping"]:
			fnam = self.mkDataFnam( mappingItem["room"] )
			mappingItem["filename"] = fnam

		# create request file
		reqFileName = self.mkReqFnam( importItem["index"] )
		with open(reqFileName,"w") as reqFile:
			json.dump(importItem,reqFile)

		# call import app
		app = os.path.abspath(importItem["fetcher"]) 
		subprocess.check_output(
			app + " " + reqFileName
			,shell = True
		).decode("utf-8")

		# delete request file
		if self.config["production"]:
			os.remove(reqFileName)


if __name__ == "__main__":
	try:
		(Dispatcher()).main()
	except KeyboardInterrupt:
		print(" - aborted")
