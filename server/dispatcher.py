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
		self.rawPrefix = os.path.abspath(
			self.config["workdir"]
			+ "/raw-"
		)
		self.fmtPrefix = os.path.abspath(
			self.config["workdir"]
			+ "/fmt-"
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


	def mkRawFnam(self,room):
		return self.rawPrefix + room + ".json"


	def mkFmtFnam(self,room):
		return self.fmtPrefix + room + ".json"


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
			json.dump(importItem,reqFile,indent=2)

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
				json = self.formatImage(deviceItem)
			elif render == "led":
				self.noteFormatDeviceItem(deviceItem)
				json = self.formatLed(deviceItem)
			else:
				continue


	def stampAdd(self,stamp1,stamp2):

		hour1 = int( stamp1.split(":")[0] )
		min1 = int( stamp1.split(":")[1] )
		hour2 = int( stamp2.split(":")[0] )
		min2 = int( stamp2.split(":")[1] )

		hour3 = hour1 + hour2
		min3 = min1 + min2
		if min3 >= 60:
			min3 -= 60
			hour3 += 1

		return str(hour3).zfill(2) + ":" + str(min3).zfill(2)


	def stampToInt(self,stamp):

		r = int( stamp.split(":")[0] ) * 100
		r += int( stamp.split(":")[1] )

		return r


	def formatImage(self,deviceItem):

		result = {}
		self.formatImageAgenda(deviceItem,result)
		self.formatImageSlots(deviceItem,result)

		rawFileName = self.mkRawFnam(deviceItem["room"])
		with open(rawFileName,"w") as rawFile:
			json.dump(result,rawFile,indent=2)


	def formatImageAgenda(self,deviceItem,result):

		fnam = self.mkDataFnam(deviceItem["room"])

		try:
			agenda = json.load(open(fnam))
		except:
			result["agenda"] = {}
			return

		result["agenda"] = agenda["agenda"]


	def formatImageSlots(self,deviceItem,result):

		result["rows"] = {}
		slot = deviceItem["slot-start"]
		rel = "past"

		now = datetime.datetime.now()
		now = str(now.hour) + ":" + str(now.minute)
		now = self.stampToInt(now)

		lastResultItem = None
		nowPassed = False
		for sliceItem in deviceItem["slices"]:
			for row in range(0,sliceItem["rows"]):

				if not nowPassed:
					if now <= self.stampToInt(slot):
						rel = "future"
						if lastResultItem is not None:
							lastResultItem["rel"] = "now"
						nowPassed = True

				result["rows"][slot] = {
					"rel": rel,
					"width": sliceItem["cols"]
				}
				lastResultItem = result["rows"][slot]

				slot = self.stampAdd(slot,deviceItem["slot-length"])


	def formatLed(self,deviceItem):
		pass # TODO


if __name__ == "__main__":
	try:
		(Dispatcher()).main()
	except KeyboardInterrupt:
		print(" - aborted")
