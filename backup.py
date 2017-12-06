import os
import shutil
import time
import sys

#requires pysmb and therefore pyasn1

theLog = ""
thePrintedString = ""

depth = 0
progress = []


def stringPrint(s):
    global thePrintedString
    thePrintedString += s
    if (len(thePrintedString) > 256):
        os.system('cls')
        print(thePrintedString)
        thePrintedString = ""

def makeFolder(outname):
    folders = outname.split("/")
    dstfolder = "."
    folders.pop()
    for f in folders:
        dstfolder += "/"+f
        if (not os.path.exists(dstfolder)):
            os.mkdir(dstfolder)
            #log += "[CF:"+dstfolder+"]"
    

def backup(filename):
    outname = "Backup{}".format(filename.replace("//","/"))
    copy = True;
    print ".",
    log = filename+": "
    if (os.path.exists(outname)):
        if (time.ctime(os.path.getmtime(outname)) != time.ctime(os.path.getmtime(filename))) :
            log += "{} has different date.".format(outname)
            copy = True
        elif (os.path.getsize(outname) != os.path.getsize(outname)):
            log += "{} has different size.".format(outname)
            copy = True
        else:
            log += "{} is identical".format(outname)
            copy = False
    if (copy == True):
        makeFolder(outname);
        try:
            shutil.copy2(filename,outname)
            log += " [copied]\n"
        except:
            log += " [error]\n"
    else:
        log += " [skipped]\n"
    return log

def ScanDir(df,depth=0, verbose=True):
    global depth
    depth +=1
    dot = 1
    #print "[Scanning "+df,
    rv = []
    files = os.listdir(df)
    stringPrint("{%d}"%depth)
    
    for f in files:
        if (verbose == True):
            print "\n[%s %d/%d]"%(f,dot,len(files)),
        if (dot % 64 == 0):
            print ".",
        dot+=1
        if (os.path.isdir(df+"/"+f) == True):
            rv += ScanDir(df+"/"+f,depth+1,False)
        else:
            rv += [df+"/"+f]
    #print "]"
    depth -=1
    return rv    

def RemoveExtra(fileList,prefix):
    files = ScanDir("Backup")
    for f in files:
        mf = f.replace("Backup/","//",1)
        delete = True
        for df in fileList:
            if (df == mf):
                delete = False
                break
        if (delete == True):
            outname = "Trash{}/{}".format(prefix,f)
            makeFolder(outname)
            shutil.move(f,outname)
            print "Deleting:",f

def RemoveEmpties(base):
    fileList = ScanDir(base)
    if not os.listdir(base):
        print ("Removing:"+base)
        os.rmdir(base)
        return True
    else:
        for f in os.listdir(base):
            if (os.path.isdir(base+"/"+f) == True):
                if (RemoveEmpties(base+"/"+f) == True):
                    os.rmdir(base)
                    return True
    return False

def TimeToString(t):
    return "%04d/%02d/%02d %02d:%02d"%(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min)
    

startTime = time.localtime();
theLog += "Start Time: "+TimeToString(startTime)+"\n"

timestamp = "%04d%02d%02d%02d%02d%02d"%(startTime.tm_year,startTime.tm_mon,startTime.tm_mday,startTime.tm_hour,startTime.tm_min,startTime.tm_sec)
print "Bulding File List",

fileList = []
f = open("backup.txt", "r")
lines = f.readlines()
f.close()

for toadd in lines:
    toadd = toadd.strip("\n")
    if (os.path.isdir(toadd)):
        theLog += "Adding dir:"+toadd+"\n"
        fileList += ScanDir(toadd)
    else:
        theLog += "Adding file:"+toadd+"\n"
        fileList += [toadd]

print "done!"
scanTime = time.localtime();
theLog += "Scanning Complete At: "+TimeToString(scanTime)+"\n"

print "Removing extra files",
RemoveExtra(fileList,timestamp)
removeTime = time.localtime();
theLog += "Scanning Complete At: "+TimeToString(removeTime)+"\n"

print "done!"
print "Backing up"

i = 0;
for f in fileList:
    if (i%100 == 0):
        print "[%d/%d]"%(i,len(fileList))
    i+=1
    theLog += backup(f)
print "Cleaning up",

backupTime = time.localtime();
theLog += "Backup Complete At: "+TimeToString(backupTime)+"\n"

RemoveEmpties("Backup")
print "done!"
removeETime = time.localtime();
theLog += "Remove Empties Complete At: "+TimeToString(removeETime)+"\n"

f = open("Logs/Backup"+timestamp+".txt", "w")
f.write(theLog)
f.close()

