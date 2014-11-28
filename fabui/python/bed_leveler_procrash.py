#bed leveling tool
import time
import sys, os
import serial
from subprocess import call
import numpy as np

#Args
try:
	logfile=str(sys.argv[1]) #param for the log file
	log_trace=str(sys.argv[2])	#trace log file
	
except:
	print "Missing Log reference"
	
#vars


#num of probes each point
num_probes=4

s_warning=s_error=s_skipped=0

screw_height_raw=[["" for x in range(0,num_probes)] for y in range(0,4)]

#points to probe
probed_points=np.array([[5+17,5+61.5,0],[5+17,148.5+61.5,0],[178+17,148.5+61.5,0],[178+17,5+61.5,0]])
#first screw offset (lower left corner)
screw_offset=[8.726,10.579,0]

serial_reply=""


def trace(string):
	global log_trace
	out_file = open(log_trace,"a+")
	out_file.write(str(string) + "\n")
	out_file.close()
	#headless
	print string
	return
	
def printlog():
	global logfile
	global screw_height
	str_log='{"bed_calibration":{'
	
	
	for screwNr in range(0,len(probed_points)):
		str_log += '"screw_height_raw_'+str(screwNr)+'":'
		str_log += ' ['
		for measurementNr in range (0, num_probes):
			str_log += '"'+screw_height_raw[screwNr][measurementNr]+'"'
			if (measurementNr < num_probes-1):
				str_log += ','
		str_log += ']'
		if (screwNr<len(probed_points)-1):
			str_log +=', '
	
	str_log+='}}'

	#write log
	handle=open(logfile,'w+')
	print>>handle, str_log
	return	

	
def read_serial(gcode):
	serial.flushInput()
	serial.write(gcode + "\r\n")
	time.sleep(0.1)
	
	#return serial.readline().rstrip()
	response=serial.readline().rstrip()
	
	if response=="":
		return "NONE"
	else:
		return response
		
def macro(code,expected_reply,timeout,error_msg,delay_after,warning=False,verbose=True):
	global s_error
	global s_warning
	global s_skipped
	serial.flushInput()
	if s_error==0:
		serial_reply=""
		macro_start_time = time.time()
		serial.write(code+"\r\n")
		if verbose:
			trace(error_msg)
		time.sleep(0.3) #give it some tome to start
		while not (serial_reply==expected_reply or serial_reply[:4]==expected_reply):
			#Expected reply
			#no reply:
			if (time.time()>=macro_start_time+timeout+5):
				if serial_reply=="":
					serial_reply="<nothing>"
				if not warning:
					s_error+=1
					trace(error_msg + ": Failed (" +serial_reply +")")
				else:
					s_warning+=1
					trace(error_msg + ": Warning! ")
				return False #leave the function
			serial_reply=serial.readline().rstrip()
			#add safety timeout
			time.sleep(0.2) #no hammering
			pass
		time.sleep(delay_after) #wait the desired amount
	else:
		trace(error_msg + ": Skipped")
		s_skipped+=1
		return False
	return serial_reply

def bed_leveling_initialisation():
    global serial
    
    trace("Manual Bed Calibration Wizard Initiated")
    port = '/dev/ttyAMA0'
    baud = 115200
    
    #initialize serial
    serial = serial.Serial(port, baud, timeout=0.6)

    serial.flushInput()

    macro("M741","TRIGGERED",2,"Front panel door control",1, verbose=False)	
    macro("M402","ok",2,"Retracting Probe (safety)",1, warning=True, verbose=False)	
    macro("G27","ok",100,"Homing Z - Fast",0.1)	

    macro("G90","ok",5,"Setting abs mode",0.1, verbose=False)
    macro("G92 Z241.2","ok",5,"Setting correct Z",0.1, verbose=False)
    #M402 #DOUBLE SAFETY!
    macro("M402","ok",2,"Retracting Probe (safety)",1, verbose=False)	
    macro("G0 Z60 F5000","ok",5,"Moving to start Z height",10) #mandatory!

def bed_leveling_rough():
    global probed_points
    global serial_reply
    point_nr = 0

    for (p,point) in enumerate(probed_points):
    
        #real carriage position
        x=point[0]-17
        y=point[1]-61.5
        macro("G0 X"+str(x)+" Y"+str(y)+" Z45 F10000","ok",15,"Moving to Pos",3, warning=True,verbose=False)		
        msg="Measuring point " +str(p+1)+ "/"+ str(len(probed_points)) + " (" +str(num_probes) + " times)"
        trace(msg)
        #Touches 1 time the bed in the same position
        probes=1 #temp
        for i in range(0,num_probes):
            # Raise probe first, to level out errors of probe retracts?!?
            macro("M402","ok",2,"Raising Probe",1, warning=True, verbose=False)	
    
            #M401
            macro("M401","ok",2,"Lowering Probe",1, warning=True, verbose=False)	
            
            serial.flushInput()
            #G30	
            serial.write("G30\r\n")
            #time.sleep(0.5)			#give it some to to start	
            probe_start_time = time.time()
            while not serial_reply[:22]=="echo:endstops hit:  Z:":
                serial_reply=serial.readline().rstrip()	
                #issue G30 Xnn Ynn and waits reply.
                if (time.time() - probe_start_time>80):	#timeout management
                    trace("Probe failed on this point")
                    probes-=1 #failed, update counter
                    screw_height_raw[point_nr][i] = "N/A"
                    break	
                pass
                
            #print serial_reply
            #get the z position
            if serial_reply!="":
                z=float(serial_reply.split("Z:")[1].strip())
                screw_height_raw[point_nr][i]=str(z)
                #trace("probe no. "+str(i+1)+" = "+str(z) )
                probed_points[p,2]+=z # store Z
                
            serial_reply=""
            serial.flushInput()
            
            #G0 Z40 F5000
            macro("G0 Z50 F5000","ok",10,"Rising Bed",1, warning=True, verbose=False)
            
        #mean of the num of measurements
        probed_points[p,0]=probed_points[p,0]
        probed_points[p,1]=probed_points[p,1]
        probed_points[p,2]=probed_points[p,2]/probes; #mean of the Z value on point "p"
        
        point_nr = point_nr +1
                    
        macro("M402","ok",2,"Raising Probe",1, warning=True, verbose=False)	
        
        #G0 Z40 F5000
        macro("G0 Z50 F5000","ok",2,"Rising Bed",0.5, warning=True, verbose=False)
        
    #now we have all the 4 points.
    macro("G0 X5 Y5 Z50 F10000","ok",2,"Idle Position",0.5, warning=True, verbose=False)
    
    macro("M18","ok",2,"Motors off",0.5, warning=True, verbose=False)
    
    #offset from the first calibration screw (lower left)
    probed_points=np.add(probed_points,screw_offset)


#we retrieve the height of the probe.
# serial.flushInput()
# serial.write("M503\r\n")
# data=serial.read(1024)
# z_probe=float(data.split("Z Probe Length: ")[1].split("\n")[0])


bed_leveling_initialisation()
bed_leveling_rough()
#save everything
printlog()
macro("M300","ok",1,"Done!",1,verbose=False) #end print signal
#end
trace("Done!")
sys.exit()