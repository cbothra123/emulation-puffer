import os
import pandas as pd
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--veritas_transform_dir", type=str, required=True) 
    parser.add_argument("--veritas_samples_dir", type=str, required=True)   
    parser.add_argument("--transition_time_step", type=int, required=True)   
    parser.add_argument("--emulation_session_len", type=float, default=350.0)   
    
    args = parser.parse_args()
    return args

def main():
    
    args = parse_arguments()

    EXP_LEN = args.transition_time_step

    if os.path.exists(args.veritas_samples_dir):
        print("Samples directory exists!")
        exit()
        
    os.mkdir(args.veritas_samples_dir)
    
    loc = os.path.join(args.veritas_transform_dir, 'sample')
    
    all = os.listdir(loc)
    for name in all:
        sample_dir = os.path.join(loc, name)
        if os.path.isdir(sample_dir):
            if 'duration' in name:
                duration = float(name.split('duration_')[1].replace('.txt', ''))
            else:
                duration = args.emulation_session_len
            
            samples = os.path.join(loc, name, 'sample_full.csv')
            df = pd.read_csv(samples)
            df = df.head(int(duration/EXP_LEN))
            
            for column in df.columns:
                df[column].to_csv(os.path.join(args.veritas_samples_dir, name + '-sample-' + column + '.csv'), index=False, header=False)
                    
if __name__ == '__main__':
    	main()
                    
