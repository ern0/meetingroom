
workdir = "/tmp/meetingroom/"


imports = [
		
		{
			"url": "calendar.google.com/xyz",
			"parser": "google",
			"mapping": [
					{ "google": "23", "room": "kilo" },
					{ "google": "25", "room": "lima" },
					{ "google": "77", "room": "alpha" }
				]
		},

		{
			"url": "calendar.google.com/aaa",
			"parser": "wiki",
			"mapping": [
				{ "row": 1, "room": "bingo" },
				{ "row": 2, "room": "hotel"}
			]

		}
]


HALF_HOUR_SLOTS = [ 
	 800,   830,  900,  930, 1000, 1030, 1100, 1130, 
	 1200, 1230, 1300, 1330, 1400, 1430, 1500, 1530, 
	 1600, 1630, 1700, 1730, 1800, 1830, 1900, 1930
]


devices = [

		{
			"device": "kilo-epaper",
			"room": "kilo",
			"render": {
				"type": "image",
				"title": "Kilo",
				"cols": 23,
				"rows": 15,
			}
		},

		{
			"device": "kilo-led",
			"room": "kilo",
			"render": {
				"type": "led",
				"title": "Kilo",
				"brightness": 30,
				"slots": HALF_HOUR_SLOTS,
			}
		},

]