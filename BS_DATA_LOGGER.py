
#!/usr/bin/env python
#
#
# author:  Richard Major
# 
# 
# This is a Raspberry Pi Python implementation.
# Physical setup :
# ADXL345 board connected to SDA and SCL as waell as power and ground.
# GPIO 18 ----- switch   GPIO 24 ------ Green LED    GPIO 04 ----Red LED
# GPIO 17 Bagley sensor if required.
# Designed for use without normal input/output devices.
#
# Green LED lights when Pi is powered up and this software is running.
#
# Designed to detect a switch press greater than 1s
# Short presses used to increment bell number (opens with 1 as default and increments through to 8
# Red LED flashes to indicate bell number.
# Long press used to start recording.
# Red LED held on during recording.
# Final presses stops recording.
# Both LEDs turn off on completion.

# To use:
# Mount Pi on headstock and clamp ADXL345 to crown staple nut.
# Mounting convention:  Components towards rope drop & writing upside down.
# Apply power to Pi and wait for green LED
# Use switch to define bell number and start data logging
# Go through the following sequence:
#   Pause for at least 3s
#   Ring up
#   Set bell and pause for at least 5s
#   Ring normally for about 10 whole pulls
#   Set bell and pause for at least 5s
#   Ring down
#   Use swithch to stop data logging
#   Pause before removing power to ensure buffer is written to file.
# Power down
# Removw hardware.
# Analyse file.
#   
import RPi.GPIO as GPIO
import time
import os, sys, stat
#import the adxl345 module
import adxl345

#create ADXL345 object
accel = adxl345.ADXL345()

GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(04, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(18, GPIO.IN)
GPIO.setup(17, GPIO.IN)
RET=0 #Rising Edge Time
FET=0 #Falling Edge Time
def my_callback(channel):
  if GPIO.input(17):
    #print"risingedge"
    #RET=time.time()
    #print str(RET)
    return RET
  
GPIO.add_event_detect(17, GPIO.BOTH, callback=my_callback)

#initialise

# LED control - Green on Red off

GPIO.output(24, True)
GPIO.output(04, False)
#time.sleep(1)
#GPIO.output(24, False)
#time.sleep(20)
#GPIO.output(24, True)
Bell_Number=1
Max_Bells=8
NextFileNumber=1


# Switch test -------------------------------------------------
# Wait for a 3s switch press. (This needs to be at least 5s inpractice.)
#  Use shorter presses to increment bell number

SwitchTime=0
Latch = 0
while True:
  # Test for input going low
  Switch=GPIO.input(18)
  if (Switch == 0)and (Latch == 0):
    StartTime=time.time()
    Latch = 1
    time.sleep(0.05)
    print ("Switch pressed")
    # Wait for it to change
    while True:
      Switch=GPIO.input(18)
      if (Switch == 1)and(Latch == 1):
        SwitchTime=(time.time()-StartTime)
        Latch = 0
        time.sleep(0.05)
        print ("Switch released")
        print (SwitchTime)
        break
    if SwitchTime > 3:
      break
    else:
      Bell_Number=Bell_Number+1
      if Bell_Number>Max_Bells:
        Bell_Number=1
      print ("Bell Number "+ str(Bell_Number))
      # Flash LEDs
      GPIO.output(04, False)
      GPIO.output(24, True)
      time.sleep(.15)
      for i in range (1,(Max_Bells+1)):
        if i < (Bell_Number+1):
          #Flash LED
          GPIO.output(04,True)
          time.sleep(.15)
        # Turn off for remainder
        GPIO.output(04,False)
        time.sleep(.15)
  if SwitchTime > 3:
    break
  
  
#  Command to start recording has been given
#  Change LEDs
GPIO.output(04, True)
GPIO.output(24, False)

#  Do things here
# Until simpleswitch action
#------------Main Data Read ----------------------

# Open NextFileNumber to read
# A next file number ensures all files have a unique identifier.
fo = open("/home/pi/adxl345-python/Data/NextFileNumber.dat", "r")
Last_File_Number=fo.readline()
fo.close()
# Open NextFileNumber to write
fo = open("/home/pi/adxl345-python/Data/NextFileNumber.dat", "w")
Next_File_Number = int(Last_File_Number )+ 1
file_string=str(Next_File_Number)
fo.write( file_string);
fo.close()
# Open final data file
FileName="/home/pi/adxl345-python/Data/Data"+str(Next_File_Number)+".dat"
fo = open(FileName, "w")
#  Manage permissions
os.chmod(FileName,stat.S_IRWXO)
i=256
#Getreadings
while True:
    Timenow =time.time()
    Timetarget = Timenow +.01 # Set delay to read at 100Hz
    # Take readings
    axes = accel.getAxes(False)
    #put the axes into variables
    x = axes['x']
    y = axes['y']
    z = axes['z']
    RetTime=0
    if GPIO.event_detected(17):
      print"Got it"
      RetTime= time.time()
      print str(RetTime) 
    file_string = str(x)+" "+str(y)+" "+str(z)+" "+str(Timenow)+" "+str(i)+" "+str(RetTime)+"\n"
    try:
      fo.write( file_string);
    except:
      # Tutn on Both LEDs
      GPIO.output(24, True)
      GPIO.output(04, True)
    # Now wait until delay time is up.  The value of i on exit gives an indication of spare processing time (large is best)
    i=0
    while time.time() < Timetarget:
        i=i+1
    #print i
    RET=0
    # Test for switch action
    Switch=GPIO.input(18)
    if (Switch == 0):
      break
# Write bell number
file_string ="Bell  "+str(Bell_Number)+"\n"
try:
  fo.write( file_string);
except:
  # Tutn on Both LEDs
  GPIO.output(24, True)
  GPIO.output(04, True)
# Close opened file
try:
  fo.close()
except:
  GPIO.output(24, True)
  GPIO.output(4, True)
  
#print("Closing...")
#  Now fully test switch commands
#  This can be used to provide additional processing options/
# Switch test ------------------------------------------
SwitchTime=0
Latch = 0
while True:
  # Test for input going low
  Switch=GPIO.input(18)
  if (Switch == 0)and (Latch == 0):
    StartTime=time.time()
    Latch = 1
    time.sleep(0.05)
    print ("Switch pressed")
    # Wait for it to change
    while True:
      Switch=GPIO.input(18)
      if (Switch == 1)and(Latch == 1):
        SwitchTime=(time.time()-StartTime)
        Latch = 0
        time.sleep(0.05)
        print ("Switch released")
        print (SwitchTime)
        break
    if SwitchTime > 1:
      break
  if SwitchTime > 1:
    break
# Turn Off Red LED
GPIO.output(04, False)
#  Identify bell
print "Bell ",Bell_Number

fo.close()
# wait until buffer is empty and file is closed
while fo.closed==False:
  # Turn on Both LEDs
  GPIO.output(24, True)
  GPIO.output(04, True)
# File is now properly closed.
# Turn off Both LEDs
GPIO.output(24, False)
GPIO.output(04, False)  




