import os
import numpy as np
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=str)    
    parser.add_argument("fcc_cooked", type=str)   
    parser.add_argument("video_sessions_dir", type=str) 
    args = parser.parse_args()
    args.veritas_dir = os.path.join(args.experiment, "veritas")
    return args

def main():
    
    args = parse_arguments()

    if os.path.exists(args.veritas_dir):
        print("Veritas directory exists!")
        exit()

    os.mkdir(args.veritas_dir)

    ground_truth_capacity = os.path.join(args.veritas_dir, 'ground_truth_capacity')
    os.mkdir(ground_truth_capacity)

    video_streams = os.path.join(args.veritas_dir, 'video_session_streams')
    os.mkdir(video_streams)

    delta = np.timedelta64(5,'s')

    for loc in os.listdir(args.video_sessions_dir):
        sessions = os.path.join(args.video_sessions_dir, loc)
        for session in os.listdir(sessions):
            trace = ("_".join(session.split('_')[0:4])).replace('fake_','')
            
            if os.path.exists(args.fcc_cooked + '/' + trace):
                g_file = open(args.fcc_cooked + '/' + trace, 'r')
                data = g_file.readlines()
            
                start_file = open(os.path.join(sessions, session), 'r')
                time = np.datetime64(start_file.readlines()[1].split(',')[1])
                dst = open(os.path.join(ground_truth_capacity, session), 'w')
                dst.write('start_time,bandwidth\n')

                for bw in data:
                    dst.write(str(time) + ',' + str(float(bw)*8/1000000) + '\n')
                    time = time + delta
                dst.close()
                start_file.close()
                
                start_file = open(os.path.join(sessions, session), 'r')
                video_data = start_file.readlines()
                video_dst = open(os.path.join(video_streams, session), 'w')
                
                for line in video_data:
                    if 'index' in line:
                        to_copy = line.split(',')[1:12]
                    else:
                        impt = line.split(',')
                        trans_time = float(impt[4])
                        ssthresh = float(impt[8])
                        to_copy = impt[1:4] + [str(trans_time)] + impt[5:8] + [str(ssthresh)] + impt[9:12]
                    video_dst.write(",".join(to_copy) + "\n")
                video_dst.close()
                start_file.close()
            else:
                print("File: ", trace, ' does not exist in FCC logs.')
                
if __name__ == '__main__':
    	main()
