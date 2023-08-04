import os
import argparse

from influx_client import parser_influx

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--exp", type=str, required=True)
    parser.add_argument("--start_time", required=True,
                        help='datetime in UTC conforming to RFC3339, Ex: 2023-02-14T06:35:00Z')
    parser.add_argument("--end_time", required=True,
                        help='datetime in UTC conforming to RFC3339, Ex: 2023-02-14T06:35:00Z')
    
    args = parser.parse_args()
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