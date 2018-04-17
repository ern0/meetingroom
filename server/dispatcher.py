#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True
import os
import time
import json
import datetime
import subprocess
import fnmatch
import hashlib


class Dispatcher:


	def main(self):

		self.about()
		self.loadConfig(sys.argv[1])
		self.createWorkDir()

		self.importData()
		self.checkChanges()
		self.formatData()


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
			+ "/agenda-"
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


	def mkReqFnam(self,index):
		return self.reqPrefix + str(index) + ".json"


	def mkDataFnam(self,room):
		return self.dataPrefix + room + ".json"


	def mkHashFnam(self,room):
		return self.dataPrefix + room + ".hash"


	def importData(self):

		self.updateStamp()

		importIndex = 0
		for importItem in self.config["import"]:
			importItem["index"] = importIndex
			importItem["production"] = self.config["production"]
			self.fetchImportItem(importItem)
			importIndex += 1


	def fetchImportItem(self,importItem):

		if not importItem["active"]: return
		self.noteFetchImportItem(importItem)
		self.performFetchImportItem(importItem)


	def noteFetchImportItem(self,importItem):

		importItemName = (
			"import"
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


	def checkChanges(self):

		self.changes = {}

		for importItem in self.config["import"]:
			if not importItem["active"]: continue
			for mappingItem in importItem["mapping"]:
				room = mappingItem["room"]
				fnam = self.mkDataFnam(room)
				hnam = self.mkHashFnam(room)

				with open(fnam,"r") as dataFile:
					data = dataFile.read()
				actualHash = hashlib.md5(data.encode()).hexdigest()

				try: 
					with open(hnam,"r") as hashFile:
						lastHash = hashFile.read().replace("\n","")
				except FileNotFoundError:
					lastHash = None
		
				if lastHash == actualHash: continue

				with open(hnam,"w") as hashFile:
					hashFile.write(actualHash)

				self.changes[room] = None


	def noteFormatDeviceItem(self,deviceItem):

		self.note(
			"format"
			+ " renderer=" + deviceItem["render"]
			+ " group=" + deviceItem["group"]
		)


	def formatData(self):

		for deviceItem in self.config["devices"]:

			if not deviceItem["active"]: continue
			if deviceItem["room"] not in self.changes: continue

			render = deviceItem["render"]
			if render == "image":
				self.noteFormatDeviceItem(deviceItem)
				json = self.formatDataImage(deviceItem)
			elif render == "led":
				self.noteFormatDeviceItem(deviceItem)
				json = self.formatDataLed(deviceItem)
			else:
				continue


	def formatDataImage(self,deviceItem):

		print(deviceItem)


	def formatDataLed(self,deviceItem):
		pass # TODO


if __name__ == "__main__":
	try:
		(Dispatcher()).main()
	except KeyboardInterrupt:
		print(" - aborted")
