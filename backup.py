import os
import shutil
import time
import sys
import time
import json
import fnmatch
#requires pysmb and therefore pyasn1

the_log = ""
the_printed_string = ""

depth = 0
progress_by_depth = []

report_noise = 100
report_iterator = 0

entry_progress = ""

start_timer = time.time()

def print_report():
    global report_iterator
    global report_noise
    global entry_progress
    global start_timer


    if (report_iterator%report_noise == 0):
        os.system('cls')

        current_timer = time.time() - start_timer
        print( "%02d:%02d|"%(current_timer/60, current_timer%60), end="" )

        outStr = ""
        for i in progress_by_depth:
            if (outStr != ""):
                outStr += "->"
            outStr += i
        print(entry_progress+outStr)
    report_iterator +=1

def backup(filename):
    in_name = "{}/{}".format(source_root, filename)
    out_name = "{}/{}".format(destination_root, filename)
    copy = True;
    print ("."),
    log = filename+": "
    if (os.path.exists(out_name)):
        time_date_a = time.ctime(os.path.getmtime(out_name))
        time_date_b = time.ctime(os.path.getmtime(in_name))
        
        if (time.ctime(os.path.getmtime(out_name)) != time.ctime(os.path.getmtime(in_name))) :
            log += "{} has different date.".format(out_name)
            copy = True
        elif (os.path.getsize(out_name) != os.path.getsize(out_name)):
            log += "{} has different size.".format(out_name)
            copy = True
        else:
            log += "{} is identical".format(out_name)
            copy = False
    if (copy == True):
        out_dir = os.path.dirname(out_name)
        try:
            os.makedirs(out_dir);
        except:
            pass
        try:
            shutil.copy(in_name,out_dir)
            shutil.copystat(in_name,out_name)
            log += " [copied]\n"
        except:
            log += " [error]\n"
    else:
        log += " [skipped]\n"
    return log

def scan_dir(df,depth=0, verbose=True, patterns = ["*.*"]):
    global the_log

    rv = []
    nb_files = 0
    for root,subdirs,files in os.walk(df):
        for f in files:
            for p in patterns:
                if (fnmatch.fnmatch(f, p)):
                    rv += [os.path.normpath("{}/{}".format(root, f))]
                    break
    return rv    

def remove_extra(file_list,prefix):
    files = scan_dir(destination_root, patterns)

    for f in files:
        stripped_file = os.path.relpath(f, destination_root)
        #normpath = os.path.normpath("{}/{}".format(source_root, stripped_file))
        if (stripped_file not in file_list):
            outname = "Trash{}/{}".format(prefix,f)
            try:
                os.makedirs(os.path.dirname(outname))
            except:
                pass
            shutil.move(f,outname)
            print ("Deleting:",f)

def remove_empties(base):
    try:
        if not os.listdir(base):
            print ("Removing:"+base)
            os.rmdir(base)
            return True
        else:
            for f in os.listdir(base):
                if (os.path.isdir(base+"/"+f) == True):
                    if (remove_empties(base+"/"+f) == True):
                        os.rmdir(base)
                        return True
    except FileNotFoundError:
        pass
    return False

def time_to_string(t):
    return "%04d/%02d/%02d %02d:%02d"%(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min)
    

start_time = time.localtime();
the_log += "Start Time: "+time_to_string(start_time)+"\n"

timestamp = "%04d%02d%02d%02d%02d%02d"%(start_time.tm_year,start_time.tm_mon,start_time.tm_mday,start_time.tm_hour,start_time.tm_min,start_time.tm_sec)
print ("Bulding File List",)

file_list = []
try:
    f = open("backup.txt", "r")
    lines = f.readlines()
    f.close()

    entry_prog = 0

    for toadd in lines:
        entry_prog += 1
        entry_progress = "%d/%d:"%(entry_prog,len(lines))
        toadd = toadd.strip("\n")
        if (os.path.isdir(toadd)):
            the_log += "Adding dir:"+toadd+"\n"
            file_list += scan_dir(toadd)
        else:
            the_log += "Adding file:"+toadd+"\n"
            file_list += [toadd]

except FileNotFoundError:
    json = json.load(open("backup.json", "r"))
    patterns = json["patterns"]
    source_root = json["source_root"]
    for source in json["sources"]:
        file_list += scan_dir("{}/{}".format(source_root, source), patterns = patterns)
    destination_root = json["destination_root"]
    
    #patterns = json["patterns"]


for k, v in enumerate(file_list):
    file_list[k] = os.path.relpath(file_list[k], source_root)

print ("done!")
scan_time = time.localtime();
the_log += "Scanning Complete At: "+time_to_string(scan_time)+"\n"

print ("Removing extra files",)
remove_extra(file_list,timestamp)
remove_time = time.localtime();
the_log += "Scanning Complete At: "+time_to_string(remove_time)+"\n"

print ("done!")
print ("Backing up")

i = 0;
for f in file_list:
    if (i%100 == 0):
        print ("[%d/%d]"%(i,len(file_list)))
    i+=1
    the_log += backup("{}".format(f))
print ("Cleaning up",)

backup_time = time.localtime();
the_log += "Backup Complete At: "+time_to_string(backup_time)+"\n"

remove_empties(destination_root)
print ("done!")
remove_end_time = time.localtime();
the_log += "Remove Empties Complete At: "+time_to_string(remove_end_time)+"\n"

try:
    os.makedirs("Logs")
except:
    pass

f = open("Logs/Backup"+timestamp+".txt", "w")
f.write(the_log)
f.close()

