#!/usr/bin/env python

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.Text import Text

########################################
# Functions for running the instructions #
########################################

def makeWrappedVP(string, x, y, wrap, screen):
	fSize = 30
	str = string.split("\n")
	if(wrap > 0):
		newStr = []
		for s in str:
			tmp = s
			while(len(tmp) > wrap):
				pivit = tmp[wrap]
				c = 0
				while(pivit != " "):
					pivit = tmp[wrap - c]
					c = c + 1
				newStr.append(tmp[:((wrap - c) + 1)])
				tmp = tmp[((wrap - c) + 1):]
			newStr.append(tmp)
	else:
		newStr = str
	
	alltStim = []
	for s in range(len(newStr)):
		tStim = Text(text=newStr[s], color=(160.0,160.0,160.0), position=(x,y + ((len(newStr)*fSize)/2 - (s*fSize)/1.5)), font_size = fSize, anchor='center')
		alltStim.append(tStim)
	return Viewport(screen=screen, stimuli=alltStim)
	
#show instruction and wait for a key press
def showInstruct(viewport, screen):
	screen.clear()
	viewport.draw()
	swap_buffers()
	
	#wait for button press
	noPress = 1
	while(noPress):
		for event in pygame.event.get():
			if event.type == pygame.locals.KEYDOWN:
					noPress = 0
