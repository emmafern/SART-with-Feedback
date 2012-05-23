# Analysis code for Pilot #4, SART with audio feedback
# Numbers appear in sequence
# Task: press spacebar on every trial except for number 3

# Analysis
# 1) calculate overall mean RT and error rate for go and no-go trials, sum of feedback tones
#   - 1 summary file containing all subject means
# 2) calculate sum of commission errors and feedback per block
#   - 1 additional file per subject
# 3) save mean RT difference from notes column

# a complete data set from one subject
# 1) subXXX_d1_R1_MainNumber.csv  (tuesday)
# 1) subXXX_d2_R2_MainNumber.csv  (wednesday)
# 2) subXXX_d3_R3_MainNumber.csv  (thursday)

# Import Modules
import os
import csv
import numpy as np
from platform import platform

# checks what operating system it's running on and adapts to it
p = [platform()]
if(p[0] == 'Win'):
    dirStr = "\\"
else:
    dirStr = "/"

# Define Variables
dayNum = ['1','2','3']
##dayNum = ['1']
numBlocks = 30

subNum = ['054','055','056','057'] # add each subject as they are collected
taskName = 'AudFdbk'
task = 'MainNumber'

#output file for day averages
with open('SART_' + taskName + '_DaySummary.csv', 'wb') as f:
    subDaySummary = csv.writer(f)
    row = (('SubNum','Task','Day','NumberRT','TargetRT','NumberOM','TargetCOM',
            'NumberFdbk')) # header row
    subDaySummary.writerow(row)

#output file for block averages
with open('SART_' + taskName + '_BlockSummary.csv', 'wb') as g:
    subBlockSummary = csv.writer(g)
    row = (('SubNum','Task','Day','Block','NumberRT','TargetRT','NumberOM','TargetCOM',
            'NumberFdbk')) # header row
    subBlockSummary.writerow(row)

# Loop through each subject
for sub in range(len(subNum)):

    # Loop through each day for each subject
    for day in range(len(dayNum)):  
        
        # Instantiate Day Lists
        day_number_rt = []
        day_number_om = []
        day_target_rt = []
        day_target_com = []
        day_number_fdbk = []
    
        # Instantiate DV Lists
        block = []      # block #
        event = []      # cue or digit
        digit = []      # what was on screen
        rt = []         # rt regardless of trial
        comission = []  # target trial errors
        omission = []   # non-target trial errors
        fdbk = []       # did feedback occur?
##        notes = []      # desc. of what occurred
        
        # Get to correct directory
        dataDir = 'Data' + dirStr + 'sub' + subNum[sub]
                
        # Read from data file "Data\subXXX\subXXX_d1_R1_MainNumber.csv"
        rowCount = 0

        with open(dataDir + dirStr + 'sub' + subNum[sub] + '_d' + dayNum[day] + '_' + task + '.csv', 'rb') as h:
            print h
            reader = csv.reader(h, delimiter = ',')
            
            for row in reader:
                if rowCount > 0:  # the 0th row is header information
                    block.append(int(row[1]))
                    event.append(row[2])
                    digit.append(row[5])
                    rt.append(row[6])  # RT is in the 7th col
                    comission.append(row[7])
                    omission.append(row[8])
                    fdbk.append(int(row[11]))
##                    notes.append(row[12])
                rowCount = rowCount + 1

        numTrials = len(event)

        # Sort the RTs and accuracy by condition in order to do overall averages
        for trial in range(numTrials):
            if event[trial].strip() == 'digit':
                if digit[trial].strip() == '3':
                    if float(rt[trial]) != 0:  # check to make sure there was a response
                        day_target_rt.append(float(rt[trial]))
                    day_target_com.append(int(comission[trial])) # add the contents of the commission column, 1 or 0
                elif digit[trial].strip() != '0': # every other number trial, except for the interblock interval
                    if float(rt[trial]) != 0:  # check to make sure there was a response
                        day_number_rt.append(float(rt[trial]))      # convert to float and add to list
                    day_number_om.append(int(omission[trial]))  # convert to integer and add to list
        
        # Save each day's data separately
        if day == 0:  # if day 1
            day1_number_rt = np.mean(day_number_rt)
            day1_number_om = np.sum(day_number_om)
            day1_target_rt = np.mean(day_target_rt)
            day1_target_com = np.sum(day_target_com)
            day1_number_fdbk = np.sum(fdbk)
        elif day == 1:  # if day 2
            day2_number_rt = np.mean(day_number_rt)
            day2_number_om = np.sum(day_number_om)
            day2_target_rt = np.mean(day_target_rt)
            day2_target_com = np.sum(day_target_com)
            day2_number_fdbk = np.sum(fdbk)
        elif day == 2: # if day 3
            day3_number_rt = np.mean(day_number_rt)
            day3_number_om = np.sum(day_number_om)
            day3_target_rt = np.mean(day_target_rt)
            day3_target_com = np.sum(day_target_com)
            day3_number_fdbk = np.sum(fdbk)

        # Sort the RTs and accuracy by block in order to do block averages
        for bl in range(1, numBlocks + 1):  # goes through blocks 1-30

            # Instantiate Block Lists
            block_number_rt = []
            block_number_om = []
            block_target_rt = []
            block_target_com = []
            block_number_fdbk = []

            blindex = (ind for ind,x in enumerate(block) if x == bl) # finds the index all all trials in each block
            for ind in blindex:  # goes through all trials within each block
                if event[ind].strip() == 'digit':
                    block_number_fdbk.append(int(fdbk[ind]))
                    if digit[ind].strip() == '3':
                        if float(rt[ind]) != 0: # check to make sure there was a response
                            block_target_rt.append(float(rt[ind]))
                        block_target_com.append(float(comission[ind]))
                    elif digit[ind].strip() != '0':
                        if float(rt[ind]) != 0: # check to make sure there was a response
                            block_number_rt.append(float(rt[ind]))
                        block_number_om.append(int(omission[ind]))
                        
            # average each block
            number_rt = np.mean(block_number_rt)

            if block_target_rt != []: # check to make sure there were responses
                target_rt = np.mean(block_target_rt)
                
            else:       # if not, return empty lists
                target_rt = ''
                target_com = ''

            number_om = np.sum(block_number_om)
            target_com = np.sum(block_target_com)
            sum_fdbk = np.sum(block_number_fdbk)

            # write to csv
            with open('SART_' + taskName + '_BlockSummary.csv', 'ab') as f:
                subDaySummary = csv.writer(f)
            ##    row = (('SubNum','Task','Day','Block','NumberRT','TargetRT','NumberOM','TargetCOM',
            ##            'NumberFdbk')) # header row
                row = (['sub' + subNum[sub], taskName, dayNum[day], bl, number_rt, target_rt,
                         number_om, target_com, sum_fdbk])
                subDaySummary.writerow(row)

            
    with open('SART_' + taskName + '_DaySummary.csv', 'ab') as f:
        subDaySummary = csv.writer(f)
##            row = (('SubNum','Task','Day','NumberRT','TargetRT', 'NumberOM','TargetCOM','NumberFdbk')) # header row
        rows = (['sub' + subNum[sub], taskName, '1', day1_number_rt, day1_target_rt,
                 day1_number_om, day1_target_com, day1_number_fdbk],
                ['sub' + subNum[sub], taskName, '2', day2_number_rt, day2_target_rt, 
                 day2_number_om, day2_target_com, day2_number_fdbk],
                ['sub' + subNum[sub], taskName, '3', day3_number_rt, day3_target_rt, 
                 day3_number_om, day3_target_com, day3_number_fdbk])
        subDaySummary.writerows(rows)

f.close()
g.close()
h.close()
