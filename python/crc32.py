#!/usr/bin/env python

#------------------------------------------------------------------#
# LuizoPiloto(c) 2020/05/09                                        #
# CRC32 Script Tool                                                #
# This file is distributed under the terms of the GNU 3.0 license. #
#------------------------------------------------------------------#

import os
import zlib
import argparse
from sys import exit
from glob import glob
from signal import signal, SIGINT

#---------------------------------#
#Structure class type definition. #
#---------------------------------#
class Struct(dict):
  def __init__(self, **kwargs):
    super(Struct, self).__init__(**kwargs)
    self.__dict__ = self
    
#-----------------------------------------------#
#Capture CTRL+C signal and terminate execution. #
#-----------------------------------------------#
def hSig(sig, frame):
  print(" Stopping…")
  exit(1)
signal(SIGINT, hSig)

#--------------------------------------------------#
#Calculate the CRC32 hash of the given file path. #
#--------------------------------------------------#
def crc32(f):
  maxsize=65536
  if not os.path.isfile(f):     #Verify if it's a file.
    return 0
  elif os.access(f, os.R_OK):   #Verify access to the file. 
    with open(f, "rb") as file: #Read file in binary mode - 'rb'.
      buffr=file.read(maxsize)  #Load the first chunk of the file.
      hash=0
      while len(buffr)>0:       #Keep loading until the end of the file.
        hash=zlib.crc32(buffr, hash)
        buffr=file.read(maxsize)
      return hash #Return a U_INT32 value.
  else:
    return -1     #Return -1 in case the file is not reachable.

#------------------------------------------#
#Convert the given integer to hexadecimal. #
#------------------------------------------#
def tohex(h):
  return format(h & 0xFFFFFFFF, "08X")

#Get script name.
sname=os.path.basename(__file__)

#String for additional info and examples.
epilog_t="""example:
  {0} foo.txt <CRC32 of a single file>
  {0} foo.txt bar.txt <Multiple files can be calculated>
  {0} *.zip *.rar *.* <Wildcards can be used>
  Returns NULL if the file is not reachable/valid""".format(sname)
  
#Argument parser declaration.
argp=argparse.ArgumentParser(prog=sname,
                             description="Simple CRC32 hash tool.",
                             epilog=epilog_t,
                             formatter_class=argparse.RawDescriptionHelpFormatter)

#Arguments to be used with the parser.
argp.add_argument("file",
                  nargs="+",
                  metavar="FILE",
                  type=str,
                  help="Input file, multiple files can be calculated.")
argp.add_argument("-v",
                  "--verbose",
                  action="count",
                  default=0,
                  help="Display additional information.")
argp.add_argument("-o",
                  action="store_true",
                  help="Omit file path. Overridden by \'-v\'")

#Parse arguments.
args=argp.parse_args()

#The list to store all the hashed stuff.
lst=[]

#Iterate trough each file passed to the script,
#verify validity and load into the list.
for arg in args.file:
  for f in glob(arg): #Iterate trough wildcard entries.
    c=crc32(f) #Store the hash result of the file path.
    
    #Verify hash validity and append to the list accordingly.
    if c!=0:
      if args.verbose>0: #Verbose is enabled.
        lst.append(Struct(file=f, crc=tohex(c) if c>0 else "Permission denied"))
      elif not args.o: #File name is not omitted.
        lst.append(Struct(file=os.path.basename(f), crc=tohex(c) if c>0 else "Permission denied"))
      else: #Omit file name from the list.
        lst.append(Struct(file="", crc=tohex(c) if c>0 else "Permission denied"))
        
#Verify if anything was processed.
if len(lst)>0:
  for item in lst: #Print results.
    print("{0} {1}".format(item.file, item.crc))
  if args.verbose>0:
    print("{0} file{1} processed.".format(len(lst), "s" if len(lst)>1 else ""))
else: #https://thumbs.gfycat.com/TeemingWarmheartedEasternglasslizard-mobile.mp4
  print("File(s) not found...")
