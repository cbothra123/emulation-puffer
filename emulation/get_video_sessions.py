import os
import argparse
import datetime

from influx_client import parser_influx

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=str)
    parser.add_argument("type", type=str)    
    parser.add_argument("host", type=str)
    parser.add_argument("--start_time",
                        help='datetime in UTC conforming to RFC3339, Ex: 2023-02-14T06:35:00Z')
    parser.add_argument("--end_time",
                        help='datetime in UTC conforming to RFC3339, Ex: 2023-02-14T06:35:00Z')
    parser.add_argument("--smart", required=False, type=int, choices=[0, 1])
    args = parser.parse_args()
    if not args.smart:
        if not args.start_time or not args.end_time:
            print("Need to pass start time and end time.")
    else:
        d = open(args.experiment + '/readme', 'r').readlines()
        args.start_time = d[-3].split(": ")[1].split(".")[0] + 'Z'
        args.end_time = d[-2].split(": ")[1].split(".")[0] + 'Z'
    
    args.exp = os.path.join(args.experiment, args.type)
    return args

def main():

    args = parse_arguments()

    if os.path.exists(args.exp):
        print("Experiment exists!")
        exit()
        
    os.mkdir(args.exp)
    video_streaming_target = os.path.join(args.exp, args.host)
    os.mkdir(video_streaming_target)

    parser_influx(args.host, args.start_time, args.end_time, video_streaming_target)

if __name__ == "__main__":
	main()
