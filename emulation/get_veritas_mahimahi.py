import os
import numpy as np
import sys
import argparse

BYTES_PER_PKT = 1500.0
MILLISEC_IN_SEC = 1000.0
BITS_IN_BYTE = 8.0

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=str) 
    parser.add_argument("veritas_samples_dir", type=str)   
    parser.add_argument("transition_time_step", type=int, help="in seconds")   
    
    args = parser.parse_args()
    args.veritas_mahimahi_dir = os.path.join(args.experiment, "mm-veritas")
    return args

def main():

    args = parse_arguments()

    EXP_LEN = args.transition_time_step * 1000

    if os.path.exists(args.veritas_mahimahi_dir):
        print("Veritas Mahimahi exists!")
        exit()
        
    os.mkdir(args.veritas_mahimahi_dir)


    files = os.listdir(args.veritas_samples_dir)

    for f in files:
        file_path = os.path.join(args.veritas_samples_dir, f)
        output_path = os.path.join(args.veritas_mahimahi_dir, f)

        print(file_path)

        with open(file_path, 'r') as f, open(output_path, 'w') as mf:
            throughput_all = []
            for line in f:
                parse = line.split('\n')
                # 	break
                throughput_all.append(float(parse[0]) * 1000 / 8)

            throughput_all = np.array(throughput_all)

            millisec_time = 0
            mf.write(str(millisec_time) + '\n')

            for i in range(len(throughput_all)):
                throughput = throughput_all[i]

                pkt_per_millisec = throughput / BYTES_PER_PKT

                millisec_count = 0
                pkt_count = 0

                while True:
                    millisec_count += 1
                    millisec_time += 1
                    to_send = (millisec_count *
                                pkt_per_millisec) - pkt_count
                    to_send = np.floor(to_send)

                    for j in range(int(to_send)):
                        mf.write(str(millisec_time) + '\n')

                    pkt_count += to_send

                    if millisec_count >= EXP_LEN:
                        break

if __name__ == '__main__':
    main()
