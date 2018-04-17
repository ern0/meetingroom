#!/bin/bash
clear

if [[ -f /usr/bin/xvfb-run ]]; then
	xvfb-run -a --server-args="-screen 0, 800x600x8" \
		wkhtmltoimage -q meetingroom.html _raw.png
else
	wkhtmltoimage -q meetingroom.html _raw.png
fi

rm -f meetingroom.png

convert _raw.png \
	-crop 200x200+0+0 \
	-dither None \
	-remap palette.png \
	meetingroom.png

convert meetingroom.png \
	-define histogram:unique-colors=true \
	-format %c histogram:info:- \
	| wc -l

file meetingroom.png

rm _raw.png
