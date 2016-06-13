#!/usr/bin/env python

# Processing bell data gathered by Belfry Slueth

#   Author:  Richard Major  June 2016

# x readings are only used to detect clappering
# y readings used to detect bell up and clappering
# z readings used to detect BDC and clappering
# Clappering is indicated by a high slew rate between sucsessive readings.
# The nature of this signal is such that the best channel is random so
#   sum all three.
# BDC is detected when z changes sign.
#False detection within the noise is likely
#   so set a minimum limit on delays that will be accepted.
#  N.B.  The direction of the zero crossing can be used to determine hand and back stroke.
import math
import numpy

# Set up control variables
# Yup   the y value needs to be above this level when up.
# UpSamples     The number of contiguous up samples signifying the bell is set.
Yup = 8.5
UpSamples=250

#  ClappeSlew  The value between sucsessive reading of x, y or z summed to indicate noise as the bell sounds.
Noise=7
#  DelayMin  Sets the minimum acceptable delay allowed (needed to reject false positives generated in the noise region).
DelayMin=25

# A user interface to change these values could be inserted here.


# Open file
Next_File_Number=input("File Number ?")
FileName="/home/pi/adxl345-python/Data/Data"+str(Next_File_Number)+".dat"
fo = open(FileName, "r")
#  Read first 250 samples and use these to determine the z offset from zero
Zero=0
for i in range (249):
    INFO=fo.readline()
    list1=INFO.split(" ")
    x=float(list1[0])
    y=float(list1[1])
    z=float(list1[2])
    Zero=Zero+z

Zero=Zero/250
# Subtract this value from all z values as they come in.

# Search for the bell being up
BellUp=False
UpCount=0
while UpCount<UpSamples:
    INFO=fo.readline()
    list1=INFO.split(" ")
    x=float(list1[0])
    y=float(list1[1])
    z=float(list1[2])-Zero
    if (y>Yup):
        UpCount=UpCount+1
    else:
        UpCount=0
    i=i+1
print "Bell is up ",i
BDC=0
LastReport=0
NoiseGap=200
HandSum=0
HandCount=0
BackSum=0
BackCount=0
Hand=0
stroke =""
# The bell has been detected as up so now search for the start of ringing
while y>Yup:
    INFO=fo.readline()
    list1=INFO.split(" ")
    x=float(list1[0])
    y=float(list1[1])
    z=float(list1[2])-Zero
    i=i+1
#  Bell has strted to move down so ringing has started.
print "Start of Ringing ",i
# Start of ringing detected so start full analysis.
#  and a search will be conducted for UpSamples of bell up indicating the end of analysis.
#  Start by storing results for comparison
UpCount=0
while UpCount<UpSamples:
    #  Read in Data
    strike=0
    xLast=x
    yLast=y
    zLast=z
    INFO=fo.readline()
    list1=INFO.split(" ")
    x=float(list1[0])
    y=float(list1[1])
    z=float(list1[2])-Zero
    if (y>Yup):
        UpCount=UpCount+1
    else:
        UpCount=0
    i=i+1
    slewnow=math.fabs(x-xLast)+math.fabs(y-yLast)+math.fabs(z-zLast)
    #Check for a sign change in z as a posible BDC
    if numpy.sign(z)<>numpy.sign(zLast):
        #There should not be noise at BDC so check this.
        if slewnow<=Noise:
            BDC=i
            # Check for Hand or Back
            if (z-zLast)>0:
                Hand=0
                stroke="Hand "
            else:
                Hand=1
                stroke="                            Back "      
    #  Now check for clappering
    if BDC<>0:
        strike=0
        if slewnow>Noise:
           strike = 1 
        if strike<>0:
            StrikeTime=i-BDC
            #  This will have some detections in the noise so reject short time returne
            if (i-LastReport)>NoiseGap:
                if StrikeTime >DelayMin:
                   print stroke,StrikeTime,BDC,(i-LastReport)
                   BDC=0
                   LastReport=i
                   if Hand == 0:
                        HandSum=HandSum+StrikeTime
                        HandCount=HandCount+1
                   else:
                        BackSum=BackSum+StrikeTime
                        BackCount=BackCount+1
                    
    zLast=z
print "End of ringing",i

#Report avaraged results
print HandCount," Handstrokes detected with mean value ",HandSum/HandCount
print BackCount," Backstrokes detected with mean value ",BackSum/BackCount

#   Now read to the end of the file to find the bell ID if it is recorded.
Bell=""
while Bell<>"Bell":
    INFO=fo.readline()
    if INFO<>"":
        list1=INFO.split(" ")
        Bell=str(list1[0])
        y=str(list1[1])
        z=str(list1[2])
    else:
        y=" not defined."
        z=""
        Bell = "Bell"
print Bell,y,z

fo.close()
