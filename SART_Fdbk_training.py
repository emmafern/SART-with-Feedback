# SART with audio feedback, and performance feedback
# Written by Emma May 2012
# no letter blocks
# 56 trials per block
# 30 total blocks
# breaks after every 5 blocks (5 breaks total)

# TO DO
# 1) if there is no response by the end of a block, program crashes


############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import Text
from VisionEgg.WrappedText import WrappedText
##from VisionEgg.ResponseControl import *
from VisionEgg.MoreStimuli import *
##from VisionEgg.GUI import *

import time
from platform import platform
import random
import numpy as np

import sys
import audiere  # for audio feedback
sys.path.append('../VEextras')

# the following modules are from VEextras
import inputGui
from instruct import showInstruct, makeWrappedVP

#checks what operating system it's running on and adapts to it
p = platform()
if(p[0:3] == 'Win'):
    dirStr = "\\"
    timeFunc = time.clock
else:
    dirStr = "/"
    timeFunc = time.time

#########################################
#  Define task input file and variables #
#########################################

# Create the input gui
inputGUI = inputGui.getInput()
inputGUI.mainloop() # Call the mainloop of Tk

# Get input and output files
outFid = open(inputGUI.outputFile, "w")

# choose a radial button that picks the task list, e.g., "MainNumberOnly.txt"
inputFile = inputGUI.taskMap[inputGUI.block.get()]
inFid = open(("Tasks" + dirStr + inputFile), "r") # opens task trial order from text file using this path
sub = inputGUI.subNum.get()     # the subject number is entered into the GUI and saved here

taskName = inputFile.split(".")
taskName = taskName[0]

# Done with the input gui
inputGUI.destroy()

#################################
# Set trial timing variables    #
#################################

# Times set in seconds
cueDur = 2.40
fixDur = 0.40
digitDur = 0.25 #should be .25
mask2Dur = .900
iti = (0.750, 0.850, 0.950, 1.050)

#############################
# Set up feedback variables #
#############################

# AUDIO FEEDBACK
# if RT difference is > or < the mean RT diff during baseline training for 4/6
# trials in a row, give a beep
prevTrials = 6 # the number of previous trials that are averaged for baseline RT
testTrials = 6 # the number of next trials that are compared to the baseline
compareBuffer = 0 # indicates whether a compareBuffer is made
freeTrialBuffer = 4 # after a beep, give 10 free trials (4+6) before keeping track of RT for feedback
freeBufferCount = 4 # will be compared to trialBuffer. start out with feedback eligible
nearTargetBuffer = 2 # before or after a target, 2 tone-free trials.
prevNearTarget = []  # keeps track of trials before a target
nextNearTarget = []  # keeps track of trials after a target

# PERFORMANCE FEEDBACK
baselinePerf = float(raw_input("Enter the performance level from practice (ex: 0.5): "))
baselineRT = float(raw_input("Enter the RT speed from practice (ex: 0.500): "))

# Commission Errors
listOfComErrors = [[],[],[],[],[],[]]  # 1 list per 5 blocks
# Opportunities for Commission Errors (Number of Targets)
listOfOpps = [[],[],[],[],[],[]]  # 1 list per 5 blocks
# Performance Ratio
listOfPerfRatio = [baselinePerf]  # will eventually have 6 ratios

# RTs
listOfGORTs = [[],[],[],[],[],[]] # 1 list per 5 blocks
# Average RT
listOfAvgRTs = [baselineRT] # will eventually have 6 averages

#################################
# Set up digit lists from file  #
#################################

allLists = []
digitList = []

#read in stimulus lists
stimList = inFid.read().split("\n")
inFid.close()

for line in stimList:
    if(line[0:5] == "block"):
        line.split(";")
        allLists.append(digitList)
        digitList = []
    elif(line != ''):
        digitList.append(int(line))

allBlocks = range(len(allLists))

#####################################
#  Initialize OpenGL window/screen  #
#####################################

VisionEgg.config.VISIONEGG_SCREEN_W = 1152
VisionEgg.config.VISIONEGG_SCREEN_H = 864
VisionEgg.config.VISIONEGG_FULLSCREEN = 0

lighterGray = (0.7, 0.7, 0.7, 1.0)
lightGray = (0.2, 0.2, 0.2, 1.0)
black = (0.0, 0.0, 0.0, 0.0)
white = (1.0, 1.0, 1.0, 1.0)
lightBlue = (0.7, 0.8, 0.9, 1.0)
green = (0.0, 1.0, 0.0, 1.0)
red = (1.0, 0.0, 0.0, 1.0)

exptScreen = get_default_screen()
exptScreen.parameters.bgcolor = black # make black (Red, Green, Blue, Alpha)

x = exptScreen.size[0]/2    # center x coordinate
y = exptScreen.size[1]/2    # center y coordinate

######################################
#  Create Stimulus                   #
######################################

targetDigit = 3

# start screen
startScreen = "This is the digit task.\n\n\t[i] Instructions\n\t[s] Start"
startStim = WrappedText(text = startScreen,
                        color = lightGray,
                        position = (x - (x/3),y),
                        font_size = 60)
#fixation
fixStim = Text(text = "X", # this changes throughout the script ("get ready...", "+")
               color = lightGray,
               position = (x, y),
               font_size = 100,
               anchor = 'center')

# changing digit size
digitStim1 = Text(text = "9",
                  color = lightGray,
                  position = (x, y),
                  font_size = 190,    
                  anchor = 'center')

digitStim2 = Text(text="9",
                  color = lightGray,
                  position = (x, y),
                  font_size = 160,    
                  anchor = 'center')

digitStim3 = Text(text = "9",
                  color = lightGray,
                  position = (x, y),
                  font_size = 85,    
                  anchor = 'center')

digitStim4 = Text(text = "9",
                  color = lightGray,
                  position = (x, y),
                  font_size = 100,    
                  anchor = 'center')

digitStim5 = Text(text = "9",
                  color = lightGray,
                  position = (x, y),
                  font_size = 130,    
                  anchor = 'center')

# mask stimuli
maskStim = Text(text="X",
                 color = lightGray,
                 position = (x, y),
                 font_size = 140,
                 anchor = 'center')

mask2Stim = Text(text = "O",
                  color = lightGray,
                  position = (x, y),
                  font_size = 190,
                  anchor = 'center')

# restbreak stim
restStim = Text(text = "BLOCK 1",  # will increment
                color = lightGray,
                position = (x, y),
                font_size = 100,    
                anchor = 'center')

breakScreen = "Please take a short break (less than 1 minute). \nPress the [s] key to continue."
breakStim = WrappedText(text = breakScreen,
                        color = lightGray,
                        position = (x - (x / 2), y),
                        font_size = 40)

# feedback stim
feedbackRect = Target2D(color = white,
                        anchor = 'center',
                        on = True,
                        orientation = 0.0,
                        position = (x, y + y/2),
                        size = (400.0, 80.0))

feedbackOutLine = Target2D(color = lightGray,  # makes a gray outline for the rectangle
                           anchor = 'center',
                           on = True,
                           orientation = 0.0,
                           position = (x, y + y/2),
                           size = (440.0, 120.0))

feedbackLine = Target2D(color = lighterGray,
                        anchor = 'center',
                        on = True,
                        orientation = 0.0,
                        position = (x, y + y/2),  # will be updated based on performance of previous block
                        size = (2.0, 100.0))

feedbackMark = Target2D(color = green,
                        anchor = 'center',
                        on = True,
                        orientation = 45.0,
                        position = (x, y + y/2),  # will be updated based on current performance
                        size = (30.0, 30.0))

feedbackRect2 = Target2D(color = white,
                        anchor = 'center',
                        on = True,
                        orientation = 0.0,
                        position = (x, y),
                        size = (400.0, 80.0))

feedbackOutLine2 = Target2D(color = lightGray,  # makes a gray outline for the rectangle
                           anchor = 'center',
                           on = True,
                           orientation = 0.0,
                           position = (x, y),
                           size = (440.0, 120.0))

feedbackLine2 = Target2D(color = lighterGray,
                        anchor = 'center',
                        on = True,
                        orientation = 0.0,
                        position = (x, y),  # will be updated based on performance of previous block
                        size = (2.0, 100.0))

feedbackMark2 = Target2D(color = green,
                        anchor = 'center',
                        on = True,
                        orientation = 45.0,
                        position = (x, y),  # will be updated based on current performance
                        size = (30.0, 30.0))

feedbackStim = WrappedText(text = 'Feedback temp',
                           color = white,
                           position = (x - x/3, y - y/2),
                           font_size = 30)

worseStim = Text(text = "WORSE",
                 color = lighterGray,
                 position = (x/3, y + y/2),
                 font_size = 50,
                 anchor = 'center')

betterStim = Text(text = "BETTER",
                  color = lighterGray,
                  position = (x + (x*2/3), y + y/2),
                  font_size = 50,
                  anchor = 'center')

slowerStim = Text(text = "SLOWER",
                 color = lighterGray,
                 position = (x/3, y),
                 font_size = 50,
                 anchor = 'center')

fasterStim = Text(text = "FASTER",
                  color = lighterGray,
                  position = (x + (x*2/3), y),
                  font_size = 50,
                  anchor = 'center')

# end screen
endText = "You're done! \n\nPlease notify the experimenter."
endStim = WrappedText(text = endText,
                      color = lightGray,
                      position = (x - (x / 2), y),
                      font_size = 50)

# Audio Stimulus
d = audiere.open_device()
soundFile = "beep-3.wav"
tone = d.open_file("Sounds" + dirStr + soundFile)

#################################################################
#  Create viewports - intermediaries between stimuli and screen #
#################################################################

viewport_startText = Viewport(screen = exptScreen, stimuli = [startStim])
viewport_fix = Viewport(screen = exptScreen, stimuli = [fixStim])
viewport_digit1 = Viewport(screen = exptScreen, stimuli = [digitStim1])
viewport_digit2 = Viewport(screen = exptScreen, stimuli = [digitStim2])
viewport_digit3 = Viewport(screen = exptScreen, stimuli = [digitStim3])
viewport_digit4 = Viewport(screen = exptScreen, stimuli = [digitStim4])
viewport_digit5 = Viewport(screen = exptScreen, stimuli = [digitStim5])
viewport_mask = Viewport(screen = exptScreen, stimuli = [maskStim, mask2Stim])
viewport_rest = Viewport(screen = exptScreen, stimuli = [restStim])
viewport_break = Viewport(screen = exptScreen, stimuli = [breakStim])
viewport_fbrect = Viewport(screen = exptScreen, stimuli = [feedbackRect])
viewport_fbline = Viewport(screen = exptScreen, stimuli = [feedbackLine])
viewport_fboline = Viewport(screen = exptScreen, stimuli = [feedbackOutLine])
viewport_fbmark = Viewport(screen = exptScreen, stimuli = [feedbackMark])
viewport_fbrect2 = Viewport(screen = exptScreen, stimuli = [feedbackRect2])
viewport_fbline2 = Viewport(screen = exptScreen, stimuli = [feedbackLine2])
viewport_fboline2 = Viewport(screen = exptScreen, stimuli = [feedbackOutLine2])
viewport_fbmark2 = Viewport(screen = exptScreen, stimuli = [feedbackMark2])
viewport_feedback = Viewport(screen = exptScreen, stimuli = [feedbackStim])
viewport_worse = Viewport(screen = exptScreen, stimuli = [worseStim])
viewport_better = Viewport(screen = exptScreen, stimuli = [betterStim])
viewport_slower = Viewport(screen = exptScreen, stimuli = [slowerStim])
viewport_faster = Viewport(screen = exptScreen, stimuli = [fasterStim])
viewport_end = Viewport(screen = exptScreen, stimuli = [endStim])
        
###################################
#  Function for logging data      #
###################################

def log_block(block, onTimes, offTimes, digits, rts, coError, omError, coCount, iti, fdbk, notes):
    if(block == 0):
        outFid.write(r"Run, Block, Event, TimeOn, TimeOff, Digit, RT,"
                     "Commission, Omission, TotalCommission, ITI, Fdbk, Notes \n")     
    out = []
    cue = "%s,%d,cue,%.5f,%.5f,%d,%.5f,%d,%d,%d,%s,%d,%d" % (taskName,
                                                       block + 1,
                                                       onTimes[0],
                                                       offTimes[0],
                                                       0, 0, 0, 0, 0,
                                                       mask2Dur, 0, 0)
    out.append(cue)
    for d in range(len(digits)):
        cur = "%s,%d,digit,%.5f,%.5f,%d,%.5f,%d,%d,%d,%s,%d,%s" % (taskName,
                                                             block + 1,
                                                             onTimes[d + 1],
                                                             offTimes[d + 1],
                                                             digits[d], rts[d],
                                                             coError[d],
                                                             omError[d],
                                                             coCount, itis[d],
                                                             fdbk[d], notes[d])
        out.append(cur)
    outFid.write("\n".join(out))
    outFid.write("\n")

##########################################
# Function for running the instructions  #
##########################################

def runInstruct():
    text1 = (r"During this task you will see a series of numbers appear on"
             " the screen one at a time. \n\nEvery time you see a number, with the exception"
             " of the number 3, press the spacebar. \n\nIf you see a 3, do not press the spacebar,"
             " simply wait for the next number. \n\nPlease try to keep up with the rhythm"
             " of the task, while at the same time trying to make as few errors (pressing the"
             " spacebar when you see a 3) as possible.")
    showInstruct(makeWrappedVP(text1, x, y, 50, exptScreen), exptScreen)
    text2 = (r"Every so often you will hear a short beep. This beep serves as a reminder"
             " for you to clear your mind and refocus on the task. \n\nYour aim is to find"
             " the balancing point, or sweet spot, between responding as quickly as possible"
             " but making as few errors as possible.")
    showInstruct(makeWrappedVP(text2, x, y, 50, exptScreen), exptScreen)
    text3 = (r"At every break you will be given feedback on your performance."
             " \n\nYou will find out whether you got more or less errors and whether"
             " you got faster or slower, compared to the previous set of blocks."
             " \n\nPlease use this information to guide your future performance.")
    showInstruct(makeWrappedVP(text3, x, y, 50, exptScreen), exptScreen)

#################################################
# Function to calculate the mean difference and #
# sd of mean difference of list of numbers      #
#################################################

def calcDiff(dlist):
    diffs = [] # should be len(list)-1 in length
    listLen = len(dlist)
    for item in range(listLen):
        if not item >= (listLen-1): # make sure we stop at 2nd to last item
            tmpdiff = abs(dlist[item] - dlist[item+1]) # calculate absolute value of diff
            diffs.append(tmpdiff)
    return diffs
        
####################################################
# Function for indicating whether list of numbers  #
# is all less than or more than baseline RT        #
####################################################

def moreless(dlist, listAVG, listSD):

    listLen = len(dlist)
    print ' '
    print 'Mean RT Diff of %d baseline trials: %.3f' % (listLen+1, listAVG)
    print 'STD of Diff of %d baseline trials: %.3f' % (listLen+1, listSD)

    lessCount = 0
    moreCount = 0
    for item in range(listLen):
        if dlist[item] <= (listAVG - .75 * listSD):  # if RT is 1 SDs below cutoff
            print ' '
            print 'below cutoff'
            print dlist[item]
            lessCount = lessCount + 1
        elif dlist[item] >= (listAVG + .75 * listSD): # if RT is 1 SDs above cutoff
            print ' '
            print 'above cutoff'
            print dlist[item]
            moreCount = moreCount + 1

    # check if 4/X items in list are more or less than baseline RT
    if lessCount + moreCount >= 4: 
        print ' '
        print '*~*~*~*~*~*~*~*~'
        print 'feedback tone'
        print ('number of small RT diffs is %s' % lessCount)
        print ('number of big RT diffs is %s' % moreCount)
        print '----------------'
        print ' '
        print ('the %d test trials RT diffs: ' % listLen) # show the list of RT diffs
        print dlist
        print '*~*~*~*~*~*~*~*~'
        tone.play()
        while tone.playing:
            time.sleep(1.1)
            tone.playing = 0
        tone.stop()
        return True
    else:
        print ' '
        print '*~*~*~*~*~*~*~*~'
        print 'no tone'
        print ('number of small RT diffs is %s' % lessCount)
        print ('number of big RT diffs is %s' % moreCount)
        print '*~*~*~*~*~*~*~*~'
        return False

#################################
# Run all the blocks and trials #
#################################

coCount = 0 # instantiate errors count, written to output file
lastXRT = [] # a list to store the last X trials' RT
nextXRT = [] # a list to store the next X trials' RT

exptScreen.clear()
viewport_startText.draw() # loads the viewport with startScreen
swap_buffers()

# wait for response to start or show instructions
noPress = 1
while(noPress): # if there is no response, wait for one
    for event in pygame.event.get():
        if event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_s: # if "s" is pressed, start experiment
                #set up fixation screen
                exptScreen.clear()
                fixStim.parameters.text = "get ready..."
                viewport_fix.draw()
                noPress = 0
            elif event.key == pygame.locals.K_i: # if "i" is pressed
                runInstruct() # show instructions
                exptScreen.clear()
                viewport_startText.draw()
                swap_buffers()
                                        
swap_buffers()          # switch to fixation screen

# set up next frame (doesn't actually show yet)
exptScreen.clear()
viewport_rest.draw()    # "BLOCK 1"

time.sleep(3)           # pause for 3 seconds on "get ready..."

swap_buffers()          # switch to text saying what block it is
cueTime = timeFunc()    # mark time of switch to "BLOCK 1"

for block in allBlocks:

    print ' '
    print ("start of block %d" % (block + 1))

    rts = []                    # instantiates vector for RTs, saved in output file
    coError = []                # instantiates vector for comission errors, saved in output file
    omError = []                # instantiates vector for omission errors, saved in output file
    itis = []                   # instantiates vector for ITIs, saved in output file
    fdbk = []                   # instantiates vector for feedback, saved in output file
    notes = []                  # instantiates vector for notes, saved in output file
    onTimes = []                # instantiates on times of rest stim or digits, saved in output file
    offTimes = []               # instantiates off times of rest stim or digits, saved in output file

    onTimes.append(cueTime)     # onTimes vector begins with the time of the switch to the block stim
                                # this is the first ON of the block (cue)
        
    # set up first frame of block (doesn't acually show yet)
    exptScreen.clear()
    digitList = allLists[block]
    digitStim1.parameters.text = str(digitList[0])
    
    # REST STIM ON SCREEN (block number) wait til cue duration is up and check for escape key
    while(timeFunc() < (cueTime + cueDur)):
       for event in pygame.event.get():
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    outFid.write(("Task quit with escape key at %.5f" % timeFunc()))
                    outFid.close()
                    exptScreen.close()

    # load viewport with fixation
    exptScreen.clear()
    fixStim.parameters.text = "+"
    viewport_fix.draw()     
    swap_buffers()          # show fixation cue to start block
    
    # load viewport with the digit
    exptScreen.clear()
    viewport_digit1.draw()

    # FIXATION ON SCREEN
    while(timeFunc() < (cueTime + cueDur + fixDur)):  # wait til fixation duration is up
        for event in pygame.event.get():
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE: # and check for escape key
                    outFid.write("Task quit with escape key at %.5f" % timeFunc())
                    outFid.close()
                    exptScreen.close() 

    swap_buffers()                  # shows first digit 
    digitStart = timeFunc()         # mark time of buffer switch to digit onset
    offTimes.append(digitStart)     # records time of switch (offtime of fixation cross)
                                    # this is the first OFF of the block (should be cueDur + fixDur)
        
    # LOOP FOR SART TRIALS
    for i in range(len(digitList)):       # loops through the number of items in digitList

        print ' '
        print ('trial %d' % (i + 1))
        noteCur = ('trial %d' % (i + 1))
        
        fsize = random.randrange(5) + 1 # this is the size of letters, could be 1 of 5 sizes
        mask2Dur = random.choice(iti)
        onTimes.append(digitStart) # records time of switch (digit ON)

        # Keep track of targets so feedback is not given 2 trials before or after
        if(digitList[i] == targetDigit): # if this is a target trial
            nextNearTarget = [i+1, i+2]
            print ("2 trials after Target: %s" % nextNearTarget)
            listOfOpps[block/10].append(1)
        elif (i <= len(digitList)-2) and (digitList[i+1] == targetDigit): # if the next trial has a target
            prevNearTarget = [i-1, i]
            print ("2 trials before Target: %s" % prevNearTarget)
        elif (i <= len(digitList)-3) and (digitList[i+2] == targetDigit): # if there is a target in two trials
            prevNearTarget = [i, i+1]
            print ("2 trials before Target: %s" % prevNearTarget)

        # load viewport with the mask
        exptScreen.clear()
        viewport_mask.draw()
                                        
        rtCur = 0
        coCur = 0
        omCur = 0
        fbCur = 0
                    
        # NUMBER ON SCREEN wait for digit dur to pass and check for key presses
        while(timeFunc() < (digitStart + digitDur)):
            for event in pygame.event.get():
                if event.type == pygame.locals.KEYDOWN:
                    t = timeFunc()
                    if((rtCur == 0) & (event.key != pygame.locals.K_5)):
                        rtCur = t - digitStart #calculates RT!
                        if(digitList[i] == targetDigit):
                            coCur = 1
                            coCount = coCount + 1
                            # Keep track of Commission errors for feedback
                            listOfComErrors[block/10].append(coCur)  
                        else:                         # if it isn't a targetDigit trial
                            listOfGORTs[block/10].append(rtCur) # keep track of RTs
                            
                            # DETERMINE WHETHER AUDIO FEEDBACK IS REQUIRED
                            if freeBufferCount >= freeTrialBuffer:      # has the free buffer passed?

                                # 1) CREATE THE compareBuffer (new, and after feedback)
                                if not compareBuffer and rtCur:         # if the compareBuffer has not been made (=0) and there was a response
                                    lastXRT.append(rtCur)               # add rt to list
                                    noteCur = "baseline"
                                    if (len(lastXRT) >= prevTrials):        # if we have 6 or more previous trial RTs stored
                                        tmp = [float(r) for r in lastXRT]   # converts to float
                                        diffs = calcDiff(tmp)               # returns list of mean differences
                                        meanDiff = np.mean(diffs)
                                        sdMeDiff = np.std(diffs)
                                        noteCur = str(meanDiff)             # the 6th baseline will show the mean RT
                                        compareBuffer = 1                   # this flag means the compareBuffer has been made
                                    continue                                # so it doesn't count the current RT as both 'last' and 'next'

                                # 2) CREATE THE testBuffer (will be compared to compareBuffer), and create compareBuffer for after no feedback
                                if compareBuffer and rtCur:             # if compareBuffer already made and there was a response
                                    nextXRT.append(rtCur)               # add rt to list
                                    noteCur = "test"
                                    # compare testBuffer to mean
                                    # if we have 6 or more new trials stored
                                    # AND a target did not occur in previous 2 trials
                                    # AND a target will not occur in next 2 trials
                                    if len(nextXRT) >= testTrials and (i not in prevNearTarget) and (i not in nextNearTarget): 
                                        tmp = [float(r) for r in nextXRT]   # converts to float
                                        diffs = calcDiff(tmp) 
                                        if moreless(diffs, meanDiff, sdMeDiff): # if true (feedback given)
                                            noteCur = "tone"
                                            fbCur = 1
                                            lastXRT = []        # resets the previous 6 baseline trials
                                            nextXRT = []        # resets the next 6 test trials
                                            compareBuffer = 0   # need to create new compareBuffer
                                            freeBufferCount = 0 # resets the 10 feedback-free trials
                                        else:   # if false (no feedback)
                                            lastXRT = nextXRT # sets the baseline to the previous 6 trials
                                            nextXRT = []      # resets the next 6 trials
                                            compareBuffer = 1 # already have a compareBuffer
                                            tmp = [float(r) for r in lastXRT]   # converts to float
                                            diffs = calcDiff(tmp)               # returns list of mean differences
                                            meanDiff = np.mean(diffs)
                                            sdMeDiff = np.std(diffs)
                                            noteCur = str(meanDiff)             # if no tone, show new mean RT

                            else:
                                freeBufferCount = freeBufferCount + 1
                                noteCur = "free"
                                                                               
        offTimes.append(timeFunc()) # records time of switch (digit OFF)
        swap_buffers()              # show mask
        exptScreen.clear()
                                                                             
        #set up the next digit 
        if(i < (len(digitList) - 1)):# if we haven't come to the end of the block
            lastStimInBlock = 0
            if fsize == 1:
                digitStim1.parameters.text = str(digitList[i + 1])
                viewport_digit1.draw()  # store the number
            elif fsize == 2:
                digitStim2.parameters.text = str(digitList[i + 1])
                viewport_digit2.draw()
            elif fsize == 3:
                digitStim3.parameters.text = str(digitList[i + 1])
                viewport_digit3.draw()
            elif fsize == 4:
                digitStim4.parameters.text = str(digitList[i + 1])
                viewport_digit4.draw()
            elif fsize == 5:
                digitStim5.parameters.text = str(digitList[i + 1])
                viewport_digit5.draw()
        else:# if there are no more stimuli to present in the block, then load the rest stim
            lastStimInBlock = 1

        # MASK ON SCREEN wait for remaining mask dur to pass and check for key presses
        while(timeFunc() < (digitStart + digitDur + mask2Dur)):
            for event in pygame.event.get():
                if event.type == pygame.locals.KEYDOWN:
                    t = timeFunc()
                    if((rtCur == 0) & (event.key != pygame.locals.K_5)):
                        rtCur = t - digitStart #calculates RT!
                        if(digitList[i] == targetDigit):
                            coCur = 1
                            coCount = coCount + 1
                            # Keep track of Commission errors for feedback
                            listOfComErrors[block/10].append(coCur) 
                        else:                         # if it isn't a targetDigit trial
                            listOfGORTs[block/10].append(rtCur) # keep track of RTs
                            # DETERMINE WHETHER AUDIO FEEDBACK IS REQUIRED
                            if freeBufferCount >= freeTrialBuffer:      # has the free buffer passed?

                                # 1) CREATE THE compareBuffer (new, and after feedback)
                                if not compareBuffer and rtCur:         # if the compareBuffer has not been made (=0) and there was a response
                                    lastXRT.append(rtCur)               # add rt to list
                                    noteCur = "baseline"
                                    if (len(lastXRT) >= prevTrials):        # if we have 6 or more previous trial RTs stored
                                        tmp = [float(r) for r in lastXRT]   # converts to float
                                        diffs = calcDiff(tmp)               # returns list of mean differences
                                        meanDiff = np.mean(diffs)
                                        sdMeDiff = np.std(diffs)
                                        noteCur = str(meanDiff)             # the 6th baseline will show the mean RT
                                        compareBuffer = 1                   # this flag means the compareBuffer has been made
                                    continue                                # so it doesn't count the current RT as both 'last' and 'next'

                                # 2) CREATE THE testBuffer (will be compared to compareBuffer), and create compareBuffer for after no feedback
                                if compareBuffer and rtCur:             # if compareBuffer already made and there was a response
                                    nextXRT.append(rtCur)               # add rt to list
                                    noteCur = "test"
                                    # compare testBuffer to mean
                                    # if we have 6 or more new trials stored
                                    # AND a target did not occur in previous 2 trials
                                    # AND a target will not occur in next 2 trials
                                    if len(nextXRT) >= testTrials and (i not in prevNearTarget) and (i not in nextNearTarget): 
                                        tmp = [float(r) for r in nextXRT]   # converts to float
                                        diffs = calcDiff(tmp) 
                                        if moreless(diffs, meanDiff, sdMeDiff): # if true (feedback given)
                                            noteCur = "tone"
                                            fbCur = 1
                                            lastXRT = []        # resets the previous 6 baseline trials
                                            nextXRT = []        # resets the next 6 test trials
                                            compareBuffer = 0   # need to create new compareBuffer
                                            freeBufferCount = 0 # resets the 10 feedback-free trials
                                        else:   # if false (no feedback)
                                            lastXRT = nextXRT # sets the baseline to the previous 6 trials
                                            nextXRT = []      # resets the next 6 trials
                                            compareBuffer = 1 # already have a compareBuffer
                                            tmp = [float(r) for r in lastXRT]   # converts to float
                                            diffs = calcDiff(tmp)               # returns list of mean differences
                                            meanDiff = np.mean(diffs)
                                            sdMeDiff = np.std(diffs)
                                            noteCur = str(meanDiff)             # if no tone, show new mean RT

                            else:
                                freeBufferCount = freeBufferCount + 1
                                noteCur = "free"
                                 
        if (rtCur == 0) & (digitList[i] != targetDigit):
            omCur = 1

        if not lastStimInBlock:      # checks to see if the last digit displayed was the last in the block
            digitStart = timeFunc()  # mark time of buffer switch
            swap_buffers()           # show next digit
        
        itis.append(mask2Dur)
        rts.append(rtCur)
        fdbk.append(fbCur)
        notes.append(noteCur)
        coError.append(coCur)
        omError.append(omCur)
        
    exptScreen.clear()
    
    #log the current block
    log_block(block, onTimes, offTimes, digitList, rts, coError, omError, coCount, mask2Dur, fdbk, notes)

    # check if we need a break
    if int((block + 1) % 5) == 0: # if block number divisable by 5 (5, 10, 15, 20, 25)                                                                          
        if not int((block + 1) % 30) == 0: # and it is not the last block

            # show error feedback            
            totalErrors = len(listOfComErrors[block/10])
            print ("total errors: %d" % totalErrors)
            totalOpps = len(listOfOpps[block/10])
            print ("total opportunities: %d" % totalOpps)
            PerfRatio = float(totalErrors) / float(totalOpps)
            print ("performance ratio: %.2f" % PerfRatio)
##            CompareRatio = listOfPerfRatio[-1]  # takes the last item in the comparison list
            CompareRatio = np.mean(listOfPerfRatio)  # takes the mean of the comparison list
            print ("comparison ratio: %.2f" % CompareRatio)
            
            if PerfRatio == 0.0:
                feedback = "You made no errors, amazing!"
                print feedback
                feedbackMark.parameters.color = green
            elif PerfRatio < CompareRatio:
                feedback = "You made less errors, great job!"
                print feedback
                feedbackMark.parameters.color = green
            elif PerfRatio > CompareRatio:
                feedback = "You made more errors, but keep trying!"
                print feedback
                feedbackMark.parameters.color = red
            elif PerfRatio == CompareRatio:
                feedback = "You held steady on errors, good job!"
                print feedback
                feedbackMark.parameters.color = green

            newpos1 = (feedbackRect.parameters.size[0]/2) - (feedbackRect.parameters.size[0]*(1-CompareRatio))
            feedbackLine.parameters.position = (x - newpos1, y + y/2) # updated based on previous performance

            newpos2 = (feedbackRect.parameters.size[0]/2) - (feedbackRect.parameters.size[0]*(1-PerfRatio))
            feedbackMark.parameters.position = (x - newpos2, y + y/2)  # updated based on current performance

            listOfPerfRatio.append(PerfRatio) # add the performance ratio to the comparison list for the next feedback

            # show RT feedback
            avgRT = np.mean(listOfGORTs[block/10])
            print ("average RT: %d ms" % (int(avgRT * 1000)))
            CompareRT = np.mean(listOfAvgRTs)

            if CompareRT-.05 < avgRT < CompareRT+.05:
                feedback2 = "You maintained your response time, good job!"
                print feedback2
                feedbackMark2.parameters.color = green
                feedbackMark2.parameters.position = (x, y)
            elif avgRT < CompareRT:
                feedback2 = "You got faster, great job!"
                print feedback2
                feedbackMark2.parameters.color = green
                feedbackMark2.parameters.position = (x + 100, y)
            elif avgRT > CompareRT:
                feedback2 = "You got slower, but keep trying!"
                print feedback2
                feedbackMark2.parameters.color = red
                feedbackMark2.parameters.position = (x - 100, y)

            listOfAvgRTs.append(avgRT) # add the average rt to the comparisons list for the next feedback

##            feedbackText = ("%s \n\n%s\n\nPress the [s] key to begin block %d/%d."
##                            % (feedback, feedback2, (block + 2), len(allBlocks)))

            feedbackText = ("Press the [s] key to begin block %d/%d." % ((block + 2), len(allBlocks)))
            feedbackStim.parameters.text = feedbackText

            viewport_feedback.draw()
            viewport_worse.draw()   # Errors
            viewport_better.draw()
            viewport_fboline.draw()
            viewport_fbrect.draw()
            viewport_fbline.draw()
            viewport_fbmark.draw()
            viewport_slower.draw()  # RT
            viewport_faster.draw()
            viewport_fboline2.draw()
            viewport_fbrect2.draw()
            viewport_fbline2.draw()
            viewport_fbmark2.draw()
            swap_buffers()
            print "break"
            
            # wait for button press
            noPress = 1
            while(noPress): 
                for event in pygame.event.get():
                    if event.type == pygame.locals.KEYDOWN:
                        t = timeFunc()
                        if event.key == pygame.locals.K_ESCAPE:
                            print ("Task quit at trial %d with escape key at %.5f" % (i, t))
                            outFid.write("Task quit with escape key at %.5f" % t)
                            outFid.close()
                            exptScreen.close()
                        elif event.key == pygame.locals.K_s: # set up the next block
                            exptScreen.clear()
                            noPress = 0

    # if it's not time for a break
    if(block < len(allLists) - 1):      # if we haven't come to the end of the run
        exptScreen.clear()              # set up the next block
        restStim.parameters.text = ("BLOCK %d" % (block + 2))  # show next block
        viewport_rest.draw()                                                                     
        cueTime = timeFunc()
        swap_buffers()
    else:       # if we have come to the end of the last block of the run

        # show feedback            
        totalErrors = len(listOfComErrors[block/10])
        print ("total errors: %d" % totalErrors)
        totalOpps = len(listOfOpps[block/10])
        print ("total opportunities: %d" % totalOpps)
        PerfRatio = float(totalErrors) / float(totalOpps)
        print ("performance ratio: %.2f" % PerfRatio)
##        CompareRatio = listOfPerfRatio[-1]  # takes the last item in the comparison list
        CompareRatio = np.mean(listOfPerfRatio)  # takes the mean of the comparison list
        print ("comparison ratio: %.2f" % CompareRatio)
        
        if PerfRatio == 0.0:
            feedback = "You did perfectly, amazing!"
            print feedback
            feedbackMark.parameters.color = green
        elif PerfRatio < CompareRatio:
            feedback = "You did better, great job!"
            print feedback
            feedbackMark.parameters.color = green
        elif PerfRatio > CompareRatio:
            feedback = "You did a little worse, but thanks for trying!"
            print feedback
            feedbackMark.parameters.color = red
        elif PerfRatio == CompareRatio:
            feedback = "You held steady, good job!"
            print feedback
            feedbackMark.parameters.color = green

        listOfPerfRatio.append(PerfRatio) # add the performance ratio to the comparison list for the next feedback
        print listOfPerfRatio

##        feedbackText = ("%s \n\nYou're done! Please notify the experimenter." % feedback)
        feedbackText = "You're done! Please notify the experimenter."
        feedbackStim.parameters.text = feedbackText

        newpos1 = (feedbackRect.parameters.size[0]/2) - (feedbackRect.parameters.size[0]*(1-CompareRatio))
        feedbackLine.parameters.position = (x - newpos1, y + y/2) # updated based on previous performance
        
        newpos2 = (feedbackRect.parameters.size[0]/2) - (feedbackRect.parameters.size[0]*(1-PerfRatio))
        feedbackMark.parameters.position = (x - newpos2, y + y/2)  # updated based on current performance

        # show RT feedback
        avgRT = np.mean(listOfGORTs[block/10])
        print ("average RT: %d ms" % (int(avgRT * 1000)))
        CompareRT = np.mean(listOfAvgRTs)

        if CompareRT-.05 < avgRT < CompareRT+.05:
            feedback2 = "You maintained your response time, good job!"
            print feedback2
            feedbackMark2.parameters.color = green
            feedbackMark2.parameters.position = (x, y)
        elif avgRT < CompareRT:
            feedback2 = "You got faster, great job!"
            print feedback2
            feedbackMark2.parameters.color = green
            feedbackMark2.parameters.position = (x + 100, y)
        elif avgRT > CompareRT:
            feedback2 = "You got slower, but keep trying!"
            print feedback2
            feedbackMark2.parameters.color = red
            feedbackMark2.parameters.position = (x - 100, y)

        listOfAvgRTs.append(avgRT) # add the average rt to the comparisons list for the next feedback
        print listOfAvgRTs

##            feedbackText = ("%s \n\n%s\n\nPress the [s] key to begin block %d/%d."
##                            % (feedback, feedback2, (block + 2), len(allBlocks)))

##        feedbackText = ("Press the [s] key to begin block %d/%d." % ((block + 2), len(allBlocks)))
##        feedbackStim.parameters.text = feedbackText

        viewport_feedback.draw()
        viewport_worse.draw()   # Errors
        viewport_better.draw()
        viewport_fboline.draw()
        viewport_fbrect.draw()
        viewport_fbline.draw()
        viewport_fbmark.draw()
        viewport_slower.draw()  # RT
        viewport_faster.draw()
        viewport_fboline2.draw()
        viewport_fbrect2.draw()
        viewport_fbline2.draw()
        viewport_fbmark2.draw()
        swap_buffers()
        print "end"

        # wait for button press
        noPress = 1
        while(noPress): 
            for event in pygame.event.get():
                if event.type == pygame.locals.KEYDOWN:
                    t = timeFunc()
                    if event.key == pygame.locals.K_ESCAPE:
                        print ("Task quit at trial %d with escape key at %.5f" % (i, t))
                        outFid.write("Task quit with escape key at %.5f" % t)
                        outFid.close()
                        exptScreen.close()
                    elif event.key == pygame.locals.K_s: # set up the next block
                        exptScreen.clear()
                        noPress = 0

# Close output file and Vision Egg screen
outFid.close()
exptScreen.close()
