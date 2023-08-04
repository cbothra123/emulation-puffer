from __future__ import division
import os
import math
import pandas as pd
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_sessions_dir", type=str, required=True)   
    parser.add_argument("--baseline_dir", type=str, required=True)   
    args = parser.parse_args()
    return args

def cluster_parser(trace_name, output_name):
	print(trace_name)
	f=open(trace_name, 'r')
	lines = f.readlines()
	overall_start = lines[1].split(',')[1]

	lastEnd=0.
	lastindex=-1
	lastBW=0.

	first=1
	newTrace=True
	count=0 #number of traces
	trace=""
	startVideo=0
	second=0 #sec within the trace

	for line in lines:
		if first:
			first=0
			continue
		data=line.split(',')
		start=(pd.to_datetime(data[1]) - pd.to_datetime(overall_start)).total_seconds()
		tmp=(pd.to_datetime(data[2]) - pd.to_datetime(overall_start)).total_seconds()
		end = tmp - start
		BW = (float(data[3])/float(data[4]))*8000 #Kbps
		index = int(data[0])
		if math.fabs(lastindex-index)>=3 or newTrace: #new trace
			newTrace=False

			if len(trace)>0: #write trace on file
				fh = open(output_name+"_"+repr(count)+".txt","w")
				if second > 500:
					fh.write(trace)
				else:
					adding = second/100
					fh.write(trace*(6-int(adding)))
				fh.close()
				count=count+1

			lastStart=0
			lastEnd=end-start
			lastindex=index
			lastBW=BW
			startVideo=start
			trace=""
			second=0
			while second <= int(end-start) :
				trace=trace+"%d"%second+","+"%.2f"%BW+"\n"
				second=second+1
			continue

		start=start-startVideo #Time must be relative to the start of the video
		end=end-startVideo


		while start > second: #if there is a gap. i.e [0-3.2] BW=5, [4.2-6.3] BW = 8, Then there is a gap @ second 4.
			gapbw=lastBW+(second-lastEnd)*((BW-lastBW)/(start-lastEnd)) #linear interploation

			trace=trace+"%d"%second+","+"%.2f"%gapbw+"\n"
			second=second+1

		while second <= end:
			trace=trace+"%d"%second+","+"%.2f"%BW+","+"\n"
			second=second+1

		lastStart=start
		lastEnd=end
		lastindex=index
		lastBW=BW


	if len(trace)>0: #write last trace on file
		fh = open(output_name+"_"+repr(count)+".txt","w")
		if second < 720:
			while second <= 720:
				trace = trace + "%d" % second + "," + "%.2f" % lastBW + "," + "\n"
				second += 1
		fh.write(trace)
		fh.close()
		count=count+1

def main():

	args = parse_arguments()

	hosts = os.listdir(args.video_sessions_dir)

	if os.path.exists(args.baseline_dir):
		print("Baseline exists!")

	os.mkdir(args.baseline_dir)

	for host in hosts:
		os.mkdir(os.path.join(args.baseline_dir, host))

		traces = os.listdir(os.path.join(args.video_sessions_dir, host))
		for trace in traces:
				
			trace_name = os.path.join(args.video_sessions_dir, host, trace)
			output_name = os.path.join(args.baseline_dir, host, trace)
			cluster_parser(trace_name, output_name)

if __name__ == "__main__":
	main()

