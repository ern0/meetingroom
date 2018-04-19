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
		self.checkDataChanges()
		self.formatData()
		self.transmitToDevices()


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
			+ "/a-agenda-request-"
		)
		self.dataPrefix = os.path.abspath(
			self.config["workdir"]
			+ "/b-agenda-"
		)
		self.rawPrefix = os.path.abspath(
			self.config["workdir"]
			+ "/c-raw-"
		)
		self.fmtPrefix = os.path.abspath(
			self.config["workdir"]
			+ "/d-fmt-"
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


	def mkRequestFnam(self,index):
		return self.reqPrefix + str(index) + ".json"


	def mkAgendaDataFnam(self,room):
		return self.dataPrefix + room + ".json"


	def mkAgendaHashFnam(self,room):
		return self.dataPrefix + room + ".hash"


	def mkRawDataFnam(self,room):
		return self.rawPrefix + room + ".json"


	def mkRawHashFnam(self,room):
		return self.rawPrefix + room + ".hash"


	def mkFmtFnam(self,room):
		return self.fmtPrefix + room + ".json"


	def mkFmtHashFnam(self,room):
		return self.fmtPrefix + room + ".hash"


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
		self.performFetchImportItem(importItem)


	def performFetchImportItem(self,importItem):

		# insert output file names into config
		for mappingItem in importItem["mapping"]:
			fnam = self.mkAgendaDataFnam( mappingItem["room"] )
			mappingItem["filename"] = fnam

		# create request file
		reqFileName = self.mkRequestFnam( importItem["index"] )
		with open(reqFileName,"w") as reqFile:
			json.dump(importItem,reqFile,indent=2)


		# call import app
		app = os.path.abspath(importItem["fetcher"])
		r = self.callApp(app,reqFileName)

		# delete request file
		if self.config["production"]:
			os.remove(reqFileName)
		else:
			print(r,end="")


	def callApp(self,app,fnam1,fnam2 = None):

		line = app
		line += " " + fnam1
		if fnam2 is not None: line += " " + fnam2

		return subprocess.check_output(
			line
			,shell = True
		).decode("utf-8")


	def checkDataChanges(self):

		self.changes = {}

		for importItem in self.config["import"]:
			if not importItem["active"]: continue
			for mappingItem in importItem["mapping"]:
				room = mappingItem["room"]
				fnam = self.mkAgendaDataFnam(room)
				hnam = self.mkAgendaHashFnam(room)

				if not self.checkChanges(fnam,hnam): continue
		
				self.changes[room] = None


	def checkChanges(self,fnam,hnam):

		with open(fnam,"r") as dataFile:
			data = dataFile.read()
		actualHash = hashlib.md5(data.encode()).hexdigest()

		try:
			with open(hnam,"r") as hashFile:
				lastHash = hashFile.read().replace("\n","")
		except FileNotFoundError:
			lastHash = None

		if lastHash == actualHash: return False

		with open(hnam,"w") as hashFile:
			hashFile.write(actualHash)

		return True


	def formatData(self):

		for deviceItem in self.config["devices"]:
			room = deviceItem["room"]

			if not deviceItem["active"]: continue
			if room not in self.changes: continue

			renderType = deviceItem["type"]
			if renderType == "image":
				itemChanged = self.formatImage(deviceItem)
			elif renderType == "led":
				itemChanged = self.formatLed(deviceItem)
			elif renderType == "lamp":
				itemChanged = self.formatLamp(deviceItem)
			else:
				itemChanged = False

			if not itemChanged:
				del self.changes[room]


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

		room = deviceItem["room"]

		result = {}
		self.formatImageAgenda(deviceItem,result)
		self.formatImageSlots(deviceItem,result)

		rawFileName = self.mkRawDataFnam(room)
		with open(rawFileName,"w") as rawFile:
			json.dump(result,rawFile,indent=2)

		hashFileName = self.mkRawHashFnam(room)
		if not self.checkChanges(rawFileName,hashFileName): 
			return False

		app = os.path.abspath(deviceItem["formatter"])
		fmtFileName = self.mkFmtFnam(room)
		r = self.callApp(app,rawFileName,fmtFileName)
		if not self.config["production"]: print(r,end="")

		hashFileName = self.mkFmtHashFnam(room)
		if not self.checkChanges(fmtFileName,hashFileName): 
			return False

		return True


	def formatImageAgenda(self,deviceItem,result):

		fnam = self.mkAgendaDataFnam(deviceItem["room"])

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


	def formatLamp(self,deviceItem):
		pass # TODO


	def transmitToDevices(self):

		print(self.changes)


if __name__ == "__main__":
	try:
		(Dispatcher()).main()
	except KeyboardInterrupt:
		print(" - aborted")
