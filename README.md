SART-with-Feedback
==================

This is a Python script written using the Vision Egg module, which displays a psychology experiment with audio and visual feedback called the Sustained Attention to Response Task (SART).

Note: Vision Egg (http://www.visionegg.org/) is a module used primarily to produce visual stimuli for psychology and vision experiments. It isn't updated very often and can only run in conjunction with Python 2.6.x or earlier.

This script also used a module called PyAudiere, which may not be updated anymore. You can still download the dependencies from http://www.softpedia.com/progDownload/PyAudiere-Download-126096.html.

RUNNING THE TRAINING
====================

Background: The SART was first used by Robertson, Manly, Andrade, Baddeley & Yiend (1997, Neuropsychologia). It is a task that requires sustained attention to perform optimally, and involves witholding key presses to rare targets. The degree that one produces commission errors (pressing the key when you are supposed to withold) on this task has been found to be correlated with everyday attention failures in normal control subjects. Commission errors may also be predicted by faster response times just before the appearance of a target, indicating that errors may be a result of a gradual drift from controlled processing to automatic responding.

Purpose: The purpose of this modified version of the SART is to train people in becoming more in control of their sustained attention. It aims to do this in several ways.

1) When response time (RT) variability exceeds a pre-defined threshold, a short tone is played. The tone serves as a reminder to clear one's head and refocus on the task (the link between the tone and RT is not made to the subject in order to avoid "overthinking" it). Baseline variability is calculated as the mean of RT differences from one trial to the next, over 6 trials. The following 6 trials are considered the test trials, and if a majority of those 6 trials have RT differences that exceed 0.75 standard deviations from the baseline variability measure, then the tone is played. If the RT differences are within the accepted range, then the mean of those differences become the new baseline variability. The tone is not played 2 trials within the appearance of a target to avoid distracting the subject.

2) A running average of RT is also made throughout the experiment. At every break (there are 4), subjects are given visual feedback as to whether their RT on the last block was faster, slower or about the same on average than the mean of all previous blocks.

3) A running count of the number of commission errors is also made throughout the experiment. At every break subjects are given visual feedback as to whether the number of errors they made was more, less or about the same as the mean number of errors of all previous blocks.

PROCESSING THE DATA
===================
Included is a script for processing and doing some light analysis of the data. It assumes 3 training files per subject. It outputs a csv file with the average RT and number of errors per subject, per day of training. This csv file can easily be used for further analysis in Python, Excel or SPSS (with slight modification).