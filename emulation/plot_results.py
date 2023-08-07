import os
from subprocess import PIPE, run, check_output
import ast
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import argparse
import pandas as pd


plt.rcParams.update({
    "text.usetex": True,
    'legend.fontsize': 20,
    'axes.labelsize': 36,
    'xtick.labelsize': 36,
    'ytick.labelsize': 36,
    'font.family': 'serif',
    'font.serif': ['Times'],
    'axes.grid' : False,
    'grid.linestyle': 'dashed',
    'lines.linewidth': 4
})

colors = {
    'deployment': 'darkgreen',
    'in_the_wild': 'darkgreen',
    'veritas': 'darkblue',
    'baseline': 'red',
    'autoveritas': 'blue',
    'autobaseline': 'darkred',
    'veritasl': 'black',
    'veritash': 'darkblue',
    'groundtruth': 'darkgreen',
}


linestyles = {
    'deployment': ('solid', 'solid'),
    'in_the_wild': ('solid', 'solid'),
    'veritas': ('dotted', 'dotted'),
    'baseline': ('dashed', 'dashed'),
    'autoveritas': ('dotted', 'dotted'),
    'autobaseline': ('dashed', 'dashed'),
    'veritasl': ('dashed', 'dashed'),
    'veritash': ('dashed', 'dashed'),
    'groundtruth': ('solid', 'solid'),
}

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=str)    

    args = parser.parse_args()
    args.readme = os.path.join(args.experiment, "readme")
    return args

def get_config(readme):
    output = {}
    lines = open(readme, 'r').readlines()
    print(lines)
    for l in range(0, len(lines)):
        if 'deployment' in lines[l]:
            start_time = lines[l+1].split(": ")[1].split(".")[0] + 'Z'
            end_time = lines[l+2].split(": ")[1].split(".")[0] + 'Z'
            output['deployment'] = (['locahost'], start_time, end_time)
        if 'baseline' in lines[l]:
            start_time = lines[l+1].split(": ")[1].split(".")[0] + 'Z'
            end_time = lines[l+2].split(": ")[1].split(".")[0] + 'Z'
            output['baseline'] = (['locahost'], start_time, end_time)

        if 'groundtruth' in lines[l]:
            start_time = lines[l+1].split(": ")[1].split(".")[0] + 'Z'
            end_time = lines[l+2].split(": ")[1].split(".")[0] + 'Z'
            output['groundtruth'] = (['locahost'], start_time, end_time)
        if 'veritas' in lines[l]:
            start_time = lines[l+1].split(": ")[1].split(".")[0] + 'Z'
            end_time = lines[l+2].split(": ")[1].split(".")[0] + 'Z'
            output['veritas'] = (['locahost'], start_time, end_time)
    print(output)
    return output

def get_metrics(data, experiment, step):
    results = {}
    hosts = data[0]
    start_time = data[1]
    end_time = data[2]
    
    for host in hosts:
        cmd = "python3 /opt/puffer/src/scripts/plot_ssim_rebuffer.py --from {} --to {} -o random.png /opt/puffer/src/veritas-highest.yml".format(start_time, end_time)
        
        try: 
            path = experiment + '/step-' + str(step) + '-' + host + '.json'
            if os.path.isfile(path):
                raw_result = open(path, 'r').read()
                result = raw_result.split('\\n')
            else:   
                raw_result = run(cmd, shell=True, capture_output=True).stdout.decode('utf-8')
                print(raw_result)
                save_step_to_file(experiment, host, step, raw_result)
                result = raw_result.split('\n')
            if result[1] != 'Missed':
                results[host] = ast.literal_eval(result[1].split('QoE:  ')[1])
            else:
                results[host] = ast.literal_eval(result[2].split('QoE:  ')[1])
        except Exception as e:
            print(e, cmd)
            continue
    return results
    
def save_step_to_file(experiment, host, step, data):
    file = open(experiment + '/step-' + str(step) + '-' + host + '.json', 'w')
    file.write(json.dumps(data))
    file.close()
    
def get_cumulative(data, experiment, type):
    
    rebuf = []
    ssim = []
    total_ssim = 0
    total_len = 0
    total_rebuf = 0
    total_play = 0
    
    total_traces = 0
    
    if type == 'veritas':
        conservative_rebuf = []
        conservative_ssim = []
        veritas = {}
        for host in data:
            for abr in data[host]:
                for trace in data[host][abr]:
                    name = 'fake' + trace[0].split('.fake')[1].split('-sample')[0] 
                    if name not in veritas:
                        veritas[name] = {'ssim': [], 'rebuf': []}
                    
                    normal_ssim = data[host][abr][trace]['total_ssim'] / data[host][abr][trace]['len']
                    normal_rebuf = data[host][abr][trace]['total_rebuf'] / data[host][abr][trace]['total_play']
                    veritas[name]['rebuf'].append(normal_rebuf)
                    veritas[name]['ssim'].append(normal_ssim)
                    
        for name in veritas:
            crebuf = max(veritas[name]['rebuf'])
            cssim = min(veritas[name]['ssim'])
            conservative_rebuf.append(crebuf)
            conservative_ssim.append(cssim)
            
    for host in data:
        for abr in data[host]:
            for trace in data[host][abr]:
                normal_ssim = data[host][abr][trace]['total_ssim'] / data[host][abr][trace]['len']
                normal_rebuf = data[host][abr][trace]['total_rebuf'] / data[host][abr][trace]['total_play']
                rebuf.append(normal_rebuf)
                ssim.append(normal_ssim)
                total_ssim += data[host][abr][trace]['total_ssim']
                total_len += data[host][abr][trace]['len']
                total_rebuf += data[host][abr][trace]['total_rebuf']
                total_play += data[host][abr][trace]['total_play']
                total_traces += 1
                if type == 'gt' and (normal_rebuf > 0.1):
                    print(trace)
    
    summary_ssim = total_ssim / total_len
    summary_rebuf = total_rebuf / total_play

    print(experiment, type, summary_ssim, summary_rebuf, total_traces)
    
    if type == 'veritas':
        return ssim, rebuf, summary_ssim, summary_rebuf, total_traces, conservative_ssim, conservative_rebuf
    else:
        return ssim, rebuf, summary_ssim, summary_rebuf, total_traces

def get_stats(method, feature, input):
    print(("{},{},{},median: {},{},{},{},{},{}\n".format(method, feature,
            np.mean(input), np.percentile(input, 50), 
            np.percentile(input, 5), np.percentile(input, 25), 
            np.percentile(input, 75), np.percentile(input, 95), np.percentile(input, 99))))
    return ("{},{},{},{},{},{},{},{},{}\n".format(method, feature,
            np.mean(input), np.percentile(input, 50), 
            np.percentile(input, 5), np.percentile(input, 25), 
            np.percentile(input, 75), np.percentile(input, 95), np.percentile(input, 99)))


def main():
    
    args = parse_arguments()

    experiment = args.experiment
    print(experiment)

    config = get_config(args.readme)

    if not os.path.isdir(experiment):
        os.mkdir(experiment)

    groundtruth_ssim, groundtruth_rebuf, \
        groundtruth_summary_ssim, groundtruth_summary_rebuf, \
            groundtruth_total = get_cumulative(get_metrics(config['groundtruth'], experiment, 3), experiment, 'gt')
    
    veritas_ssim, veritas_rebuf, \
        veritas_summary_ssim, veritas_summary_rebuf, \
            veritas_total, consverative_ssim, consverative_rebuf = get_cumulative(get_metrics(config['veritas'], experiment, 4), experiment, 'veritas')
           
    baseline_ssim, baseline_rebuf, \
        baseline_summary_ssim, baseline_summary_rebuf, \
            baseline_total =  get_cumulative(get_metrics(config['baseline'], experiment, 2), experiment, 'baseline')
    
    def convert_to_db(data):
        results = []
        for i in data:
            results.append(-10 * np.log10(1-i))
        return results

    groundtruth_ssim = convert_to_db(groundtruth_ssim)
    veritas_ssim = convert_to_db(veritas_ssim)
    baseline_ssim = convert_to_db(baseline_ssim)
    consverative_ssim = convert_to_db(consverative_ssim)
    print(groundtruth_ssim, veritas_ssim, baseline_ssim)
    sns.ecdfplot(groundtruth_ssim, label='Ground Truth', color=colors['groundtruth'], linestyle=linestyles['groundtruth'][1])
    sns.ecdfplot(veritas_ssim, label='Veritas', color=colors['veritas'], linestyle=linestyles['veritas'][1])
    sns.ecdfplot(baseline_ssim, label='Baseline', color=colors['baseline'], linestyle=linestyles['baseline'][1])

    get_stats("Groundtruth", 'ssim', groundtruth_ssim)
    get_stats("Veritas", 'ssim', veritas_ssim)
    get_stats("Baseline", 'ssim', baseline_ssim)
    
    plt.tight_layout()
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

    plt.ticklabel_format(style="plain", useOffset=False)

    plt.xlabel('SSIM (dB)')
    plt.ylabel('Proportion of sessions')
    plt.savefig(experiment + '/overall_cdf_ssim.pdf', format='pdf', bbox_inches="tight")
    plt.close()
    exit()
    
    sns.ecdfplot(groundtruth_rebuf, label='Ground Truth', color=colors['groundtruth'], linestyle=linestyles['groundtruth'][1])
    sns.ecdfplot(veritas_rebuf, label='Veritas', color=colors['veritas'], linestyle=linestyles['veritas'][1])
    sns.ecdfplot(baseline_rebuf, label='Baseline', color=colors['baseline'], linestyle=linestyles['baseline'][1])

    get_stats("Groundtruth", 'rebuf', groundtruth_rebuf)
    get_stats("Veritas", 'rebuf', veritas_rebuf)
    get_stats("Baseline", 'rebuf', baseline_rebuf)
        
    plt.tight_layout()
    plt.legend()

    plt.xlabel('Rebuf ratio')
    plt.ylabel('Proportion of sessions')
    plt.savefig(experiment + '/overall_cdf_rebuf_ratio.pdf', format='pdf', bbox_inches="tight")
    plt.close()
    
if __name__ == "__main__":
	main()
