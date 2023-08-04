import os
import numpy as np
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline_dir", type=str, required=True)   
    parser.add_argument("--mahimahi_dir", type=str, required=True)   
    args = parser.parse_args()
    return args

BYTES_PER_PKT = 1500.0
MILLISEC_IN_SEC = 1000.0
BITS_IN_BYTE = 8.0

LINES = 420

def main():

	args = parse_arguments()

	if os.path.exists(args.mahimahi_dir):
		print("Mahimahi dir exists!")
		exit()
		
	os.mkdir(args.mahimahi_dir)
	hosts = os.listdir(args.baseline_dir)

	for host in hosts:
		os.mkdir(args.mahimahi_dir + '/' + host)
		DATA_PATH = os.path.join(args.baseline_dir, host)
		OUTPUT_PATH = os.path.join(args.mahimahi_dir, host)

		files = os.listdir(DATA_PATH)
		
		for f in files:
			file_path = os.path.join(DATA_PATH, f)
			output_path = os.path.join(OUTPUT_PATH, '000.' + f)

			print (file_path)

			with open(file_path, 'r') as f, open(output_path, 'w') as mf:
				time_ms = []
				recv_time = []
				throughput_all = []
				for line in f:
					parse = line.split(",")
					time_ms.append(float(parse[0]) * 1000)
					throughput_all.append(float(parse[1]) / 8)
					if len(time_ms) > 1:
						recv_time.append(float(parse[0]) - recv_time[-1])
					else:
						recv_time.append(0)

				time_ms = np.array(time_ms)
				throughput_all = np.array(throughput_all)
				recv_time = np.array(recv_time)

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
						to_send = (millisec_count * pkt_per_millisec) - pkt_count
						to_send = np.floor(to_send)

						for j in range(int(to_send)):
							mf.write(str(millisec_time) + '\n')

						pkt_count += to_send

						if millisec_count >= 1000:
							break

if __name__ == '__main__':
	main()

