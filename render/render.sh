#!/bin/bash
clear


function main {

	if [[ -f /usr/bin/xvfb-run ]]; then
		xvfb-run -a --server-args="-screen 0, 800x600x24" \
			wkhtmltoimage -q meetingroom.html _raw.png
	else
		wkhtmltoimage -q meetingroom.html _raw.png
	fi

	#############
	c1
	#############

	convert meetingroom.png \
		-define histogram:unique-colors=true \
		-format %c histogram:info:-

	file meetingroom.png

	rm _raw.png
}


function c1 {

	convert _raw.png \
		-resize 50% \
		-crop 200x200+0+0 \
		+dither \
		-colors 2 \
		-quality 100 \
		-type bilevel \
		meetingroom.png
}


function c2 {

	convert _raw.png \
		-resize 50% \
		-crop 200x200+0+0 \
		-colors 2 \
		-quality 100 \
		-type bilevel \
		meetingroom.png
}


main