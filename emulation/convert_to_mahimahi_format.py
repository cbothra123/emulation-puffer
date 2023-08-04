import os
import numpy as np
import sys

IN_FILE = './' + sys.argv[1]+ '/'
OUT_FILE = './' + sys.argv[2] + '/'
FILE_SIZE = 200
BYTES_PER_PKT = 1500.0
MILLISEC_IN_SEC = 1000.0
EXP_LEN = 5000.0  # millisecond

if not os.path.exists(sys.argv[2]):
    os.mkdir(sys.argv[2])

def main():
	files = os.listdir(IN_FILE)
	for trace_file in files:
		if os.stat(IN_FILE + trace_file).st_size >= FILE_SIZE:
			with open(IN_FILE + trace_file, 'r') as f, open(OUT_FILE + trace_file, 'w') as mf:
				millisec_time = 0
				mf.write(str(millisec_time) + '\n')
				for line in f:
					throughput = float(line.split()[0])
					pkt_per_millisec = throughput / BYTES_PER_PKT / MILLISEC_IN_SEC

					millisec_count = 0
					pkt_count = 0
					while True:
						millisec_count += 1
						millisec_time += 1
						to_send = (millisec_count * pkt_per_millisec) - pkt_count
						to_send = np.floor(to_send)

						for i in range(int(to_send)):
							mf.write(str(millisec_time) + '\n')

						pkt_count += to_send

						if millisec_count >= EXP_LEN:
							break


if __name__ == '__main__':
	main()
