#!/bin/bash
clear

xvfb-run -a --server-args="-screen 0, 800x600x24" /usr/bin/wkhtmltoimage -q meetingroom.html _raw.png

convert _raw.png \
	-resize 50% \
	-crop 200x200+0+0 \
	+dither \
	-colors 2 \
	-quality 100 \
	-type bilevel \
	meetingroom.png

convert meetingroom.png \
	-define histogram:unique-colors=true \
	-format %c histogram:info:-

file meetingroom.png

rm _raw.png
