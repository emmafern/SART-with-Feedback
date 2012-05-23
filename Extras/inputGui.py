#!/usr/bin/env python

############################
#  Import various modules  #
############################

#import VisionEgg
#VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()
from VisionEgg.GUI import *

import Tkinter
import string
from platform import platform

p = platform()
if(p[0:3] == 'Win'):
        dirStr = "\\"
else:
        dirStr = "/"

class getInput(AppWindow):
    def checkStart(self):
    	tmp = self.taskMap[self.block.get()].split(".")
    	inFile = tmp[0]
        self.outputFile = "Data" + dirStr + "sub" + self.subNum.get() + "_" + inFile + ".csv"
##        self.outputFile = "Data" + dirStr + "sub" + self.subNum.get() + "_" + exptName + "_" + inFile + ".csv"
        if(os.path.exists(self.outputFile)):
			Tkinter.Label(self, text = ("Warning:\n" + self.outputFile + "\nalready exists"),fg = "red").pack()
			Tkinter.Button(self, text = "Start anyway", command = self.quit).pack()
        else:
        	self.quit()
        
    def __init__(self,master = None,**cnf):

        AppWindow.__init__(self,master,**cnf)
        self.winfo_toplevel().title('TaskInput')
        self.pack(expand = 1,fill = Tkinter.BOTH)
        
        Tkinter.Label(self,text = "Subject Number:").pack()
        self.subNum = Tkinter.StringVar()
        self.subNum.set("000")
        Tkinter.Entry(self, textvariable = self.subNum).pack()
        
        Tkinter.Label(self,text = "Block:").pack()
        self.block = Tkinter.IntVar()
        self.block.set(0)
        
        allTasks = os.listdir('Tasks')
        self.taskMap = []
        count = 0
        for t in allTasks:
        	if(t[0] != '.'):
        		Tkinter.Radiobutton(self, text = t, variable = self.block, value = count).pack(anchor = Tkinter.W)
        		self.taskMap.append(t)
        		count = count + 1
        
        Tkinter.Button(self, text="Start", command=self.checkStart).pack()
