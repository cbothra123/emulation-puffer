import seaborn as sns
import matplotlib.pyplot as plt

#Exp 211: step 1 original settings with ground truth (LMH, MPC, buffer 15s)
#Exp 204 : step 2 modified settings with baseline (LMH, BBA)
#Exp 214: step 3 modified settings with ground truth (LMH, BBA, buffer 15s)
#Exp 208: step 4 modified setting with const stddev HMM output (LMH, BBA, buffer 15s)

colors = {
    'deployment': 'green',
    'in_the_wild': 'green',
    'veritas': 'blue',
    'baseline': 'red',
    'autoveritas': 'blue',
    'autobaseline': 'red',
    'veritasl': 'black',
    'veritash': 'blue',
    'groundtruth': 'green',
    'causalsim': 'orange'
}


def get_traces_from_steps(step):
    traces = {}
    for host in step:
        for abr in step[host]:
            for trace in step[host][abr]:
                name = trace[0]
                traces[name] = step[host][abr][trace]
    return traces

def step_4_processing(step_4):
    traces = {}
    for host in step_4:
        for abr in step_4[host]:
            for trace in step_4[host][abr]:
                name = trace[0]
                unsampled_name = "_".join(name[9:].split('_')[0:4])
                
                # unsampled_id = name.split('sample')[1].split('.')[0][1:]
                if unsampled_name not in traces:
                    traces[unsampled_name] = {}
                    traces[unsampled_name]['qoe'] = []
                    traces[unsampled_name]['rebuf'] = []
                    traces[unsampled_name]['ssim'] = []
                    traces[unsampled_name]['diff_ssim'] = []

                traces[unsampled_name]['qoe'].append(
                    step_4[host][abr][trace]['value'] / step_4[host][abr][trace]['len'])
                traces[unsampled_name]['ssim'].append(
                    step_4[host][abr][trace]['total_ssim'] / step_4[host][abr][trace]['len'])
                traces[unsampled_name]['rebuf'].append(
                    step_4[host][abr][trace]['total_rebuf'] / step_4[host][abr][trace]['total_play'])
                traces[unsampled_name]['diff_ssim'].append(
                    step_4[host][abr][trace]['diff_ssim'] / step_4[host][abr][trace]['len'])

    step_4_l = {}
    step_4_h = {}

    for trace in traces:
        step_4_l[trace] = {}
        step_4_h[trace] = {}

        qoes = (traces[trace]['qoe'])
        qoes.sort()
        ssims = (traces[trace]['ssim'])
        ssims.sort()
        diff_ssims = (traces[trace]['diff_ssim'])
        diff_ssims.sort()
        rebufs = (traces[trace]['rebuf'])
        rebufs.sort()

        low = 1
        high = -1

        step_4_l[trace]['qoe'] = qoes[low]
        step_4_l[trace]['ssim'] = ssims[low]
        step_4_l[trace]['diff_ssim'] = diff_ssims[low]
        step_4_l[trace]['rebuf'] = rebufs[low]

        step_4_h[trace]['qoe'] = qoes[high]
        step_4_h[trace]['ssim'] = ssims[high]
        step_4_h[trace]['diff_ssim'] = diff_ssims[high]
        step_4_h[trace]['rebuf'] = rebufs[high]

        """
        if len(qoes) == 5:

            step_4_l[trace]['qoe'] = qoes[1]
            step_4_l[trace]['ssim'] = ssims[1]
            step_4_l[trace]['diff_ssim'] = diff_ssims[1]
            step_4_l[trace]['rebuf'] = rebufs[1]

            step_4_h[trace]['qoe'] = qoes[3]
            step_4_h[trace]['ssim'] = ssims[3]
            step_4_h[trace]['diff_ssim'] = diff_ssims[3]
            step_4_h[trace]['rebuf'] = rebufs[3]

        elif len(qoes) == 4:

            step_4_l[trace]['qoe'] = qoes[1]
            step_4_l[trace]['ssim'] = ssims[1]
            step_4_l[trace]['diff_ssim'] = diff_ssims[1]
            step_4_l[trace]['rebuf'] = rebufs[1]

            step_4_h[trace]['qoe'] = qoes[2]
            step_4_h[trace]['ssim'] = ssims[2]
            step_4_h[trace]['diff_ssim'] = diff_ssims[2]
            step_4_h[trace]['rebuf'] = rebufs[2]

        elif len(qoes) == 3:

            step_4_l[trace]['qoe'] = qoes[0]
            step_4_l[trace]['ssim'] = ssims[0]
            step_4_l[trace]['diff_ssim'] = diff_ssims[0]
            step_4_l[trace]['rebuf'] = rebufs[0]

            step_4_h[trace]['qoe'] = qoes[2]
            step_4_h[trace]['ssim'] = ssims[2]
            step_4_h[trace]['diff_ssim'] = diff_ssims[2]
            step_4_h[trace]['rebuf'] = rebufs[2]
        """
    return step_4_l, step_4_h

def get_the_graphs(step_1, step_2, step_3, step_4, output_dir, step_2_type):
    step_1_traces = get_traces_from_steps(step_1)
    step_2_traces = get_traces_from_steps(step_2)
    step_3_traces = get_traces_from_steps(step_3)
    step_4_l_traces, step_4_h_traces = step_4_processing(step_4)

    plot_data = {}
    plot_data['step1'] = {}
    plot_data['step2'] = {}
    plot_data['step3'] = {}
    plot_data['step4_l'] = {}
    plot_data['step4_h'] = {}


    plot_data['step1']['qoe'] = []
    plot_data['step1']['ssim'] = []
    plot_data['step1']['rebuf'] = []
    plot_data['step1']['diff_ssim'] = []
    plot_data['step2']['qoe'] = []
    plot_data['step2']['ssim'] = []
    plot_data['step2']['rebuf'] = []
    plot_data['step2']['diff_ssim'] = []
    plot_data['step3']['qoe'] = []
    plot_data['step3']['ssim'] = []
    plot_data['step3']['rebuf'] = []
    plot_data['step3']['diff_ssim'] = []
    plot_data['step4_l']['qoe'] = []
    plot_data['step4_l']['ssim'] = []
    plot_data['step4_l']['rebuf'] = []
    plot_data['step4_l']['diff_ssim'] = []
    plot_data['step4_h']['qoe'] = []
    plot_data['step4_h']['ssim'] = []
    plot_data['step4_h']['rebuf'] = []
    plot_data['step4_h']['diff_ssim'] = []

    group = {}
    group['qoe'] = []
    group['ssim'] = []
    group['diff_ssim'] = []
    group['rebuf'] = []

    for trace_all in step_2_traces:
        trace = trace_all[:-2]
        trace = "_".join(trace_all[9:].split('_')[0:4])
        if trace in step_1_traces:
            if trace in step_3_traces:
                if trace in step_4_l_traces:
                    plot_data['step1']['qoe'].append(step_1_traces[trace]['value']/step_1_traces[trace]['len'])
                    plot_data['step1']['ssim'].append(step_1_traces[trace]['total_ssim']/step_1_traces[trace]['len'])
                    plot_data['step1']['rebuf'].append(step_1_traces[trace]['total_rebuf'] *100/ step_1_traces[trace]['total_play'] )
                    plot_data['step1']['diff_ssim'].append(step_1_traces[trace]['diff_ssim']/step_1_traces[trace]['len'])
                    plot_data['step2']['qoe'].append(step_2_traces[trace_all]['value']/step_2_traces[trace_all]['len'])
                    plot_data['step2']['ssim'].append(step_2_traces[trace_all]['total_ssim']/step_2_traces[trace_all]['len'])
                    plot_data['step2']['rebuf'].append(step_2_traces[trace_all]['total_rebuf']*100 / step_2_traces[trace_all]['total_play'])
                    plot_data['step2']['diff_ssim'].append(step_2_traces[trace_all]['diff_ssim']/step_2_traces[trace_all]['len'])
                    plot_data['step3']['qoe'].append(step_3_traces[trace]['value']/step_3_traces[trace]['len'])
                    plot_data['step3']['ssim'].append(step_3_traces[trace]['total_ssim']/step_3_traces[trace]['len'])
                    plot_data['step3']['rebuf'].append(step_3_traces[trace]['total_rebuf']*100 / step_3_traces[trace]['total_play'])
                    plot_data['step3']['diff_ssim'].append(step_3_traces[trace]['diff_ssim']/step_3_traces[trace]['len'])
                    plot_data['step4_l']['qoe'].append(step_4_l_traces[trace]['qoe'])
                    plot_data['step4_l']['ssim'].append(step_4_l_traces[trace]['ssim'])
                    plot_data['step4_l']['rebuf'].append(step_4_l_traces[trace]['rebuf']*100)
                    plot_data['step4_l']['diff_ssim'].append(step_4_l_traces[trace]['diff_ssim'])
                    plot_data['step4_h']['qoe'].append(step_4_h_traces[trace]['qoe'])
                    plot_data['step4_h']['ssim'].append(step_4_h_traces[trace]['ssim'])
                    plot_data['step4_h']['rebuf'].append(step_4_h_traces[trace]['rebuf']*100)
                    plot_data['step4_h']['diff_ssim'].append(step_4_h_traces[trace]['diff_ssim'])

                    group['qoe'].append((
                        step_1_traces[trace]['value'] / step_1_traces[trace]['len'],
                        step_2_traces[trace_all]['value'] / step_2_traces[trace_all]['len'],
                        step_3_traces[trace]['value'] / step_3_traces[trace]['len'],
                        step_4_l_traces[trace]['qoe'],
                        step_4_h_traces[trace]['qoe']
                    ))

                    group['ssim'].append((
                        step_1_traces[trace]['total_ssim'] / step_1_traces[trace]['len'],
                        step_2_traces[trace_all]['total_ssim'] / step_2_traces[trace_all]['len'],
                        step_3_traces[trace]['total_ssim'] / step_3_traces[trace]['len'],
                        step_4_l_traces[trace]['ssim'],
                        step_4_h_traces[trace]['ssim']
                    ))

                    group['diff_ssim'].append((
                        step_1_traces[trace]['diff_ssim'] / step_1_traces[trace]['len'],
                        step_2_traces[trace_all]['diff_ssim'] / step_2_traces[trace_all]['len'],
                        step_3_traces[trace]['diff_ssim'] / step_3_traces[trace]['len'],
                        step_4_l_traces[trace]['diff_ssim'],
                        step_4_h_traces[trace]['diff_ssim']
                    ))

                    group['rebuf'].append((
                        step_1_traces[trace]['total_rebuf'] * 100 / step_1_traces[trace]['total_play'],
                        step_2_traces[trace_all]['total_rebuf'] * 100 / step_2_traces[trace_all]['total_play'],
                        step_3_traces[trace]['total_rebuf'] * 100 / step_3_traces[trace]['total_play'],
                        step_4_l_traces[trace]['rebuf'] * 100,
                        step_4_h_traces[trace]['rebuf'] * 100
                    ))

    x = []
    for i in range(len(plot_data['step1']['qoe'])):
        x.append(i)

    # plt.scatter(x, plot_data['step1']['qoe'], label='Deployed', color='b')
    plt.scatter(x, plot_data['step2']['qoe'], label='Baseline', color=colors['baseline'])
    plt.scatter(x, plot_data['step3']['qoe'], label='Groundtruth (GTBW)', color=colors['groundtruth'])
    plt.scatter(x, plot_data['step4_l']['qoe'], label='Veritas (Low)', color=colors['veritas'], marker='o')
    plt.scatter(x, plot_data['step4_h']['qoe'], label='Veritas (High)', color=colors['veritas'], marker='*')


    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("QoE")
    plt.savefig(output_dir + '/' + 'qoe.png')
    plt.close()

    # plt.scatter(x, plot_data['step1']['ssim'], label='Deployed', color='b')
    plt.scatter(x, plot_data['step2']['ssim'], label='Baseline', color=colors['baseline'])
    plt.scatter(x, plot_data['step3']['ssim'], label='Groundtruth (GTBW)', color='g')
    plt.scatter(x, plot_data['step4_l']['ssim'], label='Veritas (Low)', color='red', marker='o')
    plt.scatter(x, plot_data['step4_h']['ssim'], label='Veritas (High)', color='red', marker='*')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("SSIM")
    plt.savefig(output_dir + '/' + 'ssim.png')
    plt.close()

    # plt.scatter(x, plot_data['step1']['rebuf'], label='Deployed', color='b')
    plt.scatter(x, plot_data['step2']['rebuf'], label='Baseline', color=colors['baseline'])
    plt.scatter(x, plot_data['step3']['rebuf'], label='Groundtruth (GTBW)', color='g')
    plt.scatter(x, plot_data['step4_l']['rebuf'], label='Veritas (Low)', color='red', marker='o')
    plt.scatter(x, plot_data['step4_h']['rebuf'], label='Veritas (High)', color='red', marker='*')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("Rebuffering")
    plt.savefig(output_dir + '/' + 'rebuf.png')
    plt.close()

    # plt.scatter(x, plot_data['step1']['diff_ssim'], label='Deployed', color='b')
    plt.scatter(x, plot_data['step2']['diff_ssim'], label='Baseline', color=colors['baseline'])
    plt.scatter(x, plot_data['step3']['diff_ssim'], label='Groundtruth (GTBW)', color=colors['groundtruth'])
    plt.scatter(x, plot_data['step4_l']['diff_ssim'], label='Veritas (Low)', color=colors['veritas'], marker='o')
    plt.scatter(x, plot_data['step4_h']['diff_ssim'], label='Veritas (High)', color=colors['veritas'], marker='*')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("Diff SSIM")
    plt.savefig(output_dir + '/' + 'diff_ssim.png')
    plt.close()

    # sns.ecdfplot(plot_data['step1']['ssim'], label='Deployed', color='b')
    sns.ecdfplot(plot_data['step2']['ssim'], label='Baseline', color=colors['baseline'])
    sns.ecdfplot(plot_data['step3']['ssim'], label='Groundtruth (GTBW)', color=colors['groundtruth'])
    d = sns.ecdfplot(plot_data['step4_l']['ssim'], label='Verita (Low)', color=colors['veritas'], linestyle='dashed')
    e = sns.ecdfplot(plot_data['step4_h']['ssim'], label='Veritas (High)', color=colors['veritas'])

    plt.legend()
    plt.xlabel("SSIM")
    plt.ylabel("CDF (Fraction of sessions)")
    plt.savefig(output_dir + '/' + 'cdf_ssim.png')
    plt.close()

    # sns.ecdfplot(plot_data['step1']['diff_ssim'], label='Deployed', color='b')
    sns.ecdfplot(plot_data['step2']['diff_ssim'], label='Baseline', color=colors['baseline'])
    sns.ecdfplot(plot_data['step3']['diff_ssim'], label='Groundtruth (GTBW)', color='g')
    l = sns.ecdfplot(plot_data['step4_l']['diff_ssim'], label='Veritas (Low)', color='r', linestyle='dashed')
    h = sns.ecdfplot(plot_data['step4_h']['diff_ssim'], label='Veritas (High)', color='r')

    plt.legend()
    plt.xlabel("Diff SSIM")
    plt.ylabel("CDF (Fraction of sessions)")
    plt.savefig(output_dir + '/' + 'cdf_diff_ssim.png')
    plt.close()

    # sns.ecdfplot(plot_data['step1']['rebuf'], label='Deployed', color='b')
    sns.ecdfplot(plot_data['step2']['rebuf'], label='Baseline', color=colors['baseline'])
    sns.ecdfplot(plot_data['step3']['rebuf'], label='Groundtruth (GTBW)', color=colors['groundtruth'])
    l = sns.ecdfplot(plot_data['step4_l']['rebuf'], label='Veritas (Low)', color=colors['veritas'], linestyle='dashed')
    h = sns.ecdfplot(plot_data['step4_h']['rebuf'], label='Veritas (High)', color=colors['veritas'])

    plt.legend()
    plt.xlabel("Rebuffering ratio (% of session)")
    plt.ylabel("CDF (Fraction of sessions)")
    plt.savefig(output_dir + '/' + 'cdf_rebuf.png')
    plt.close()

    # sns.ecdfplot(plot_data['step1']['qoe'], label='Deployed', color='b')
    sns.ecdfplot(plot_data['step2']['qoe'], label='Baseline', color=colors['baseline'])
    sns.ecdfplot(plot_data['step3']['qoe'], label='Groundtruth (GTBW)', color=colors['groundtruth'])
    l = sns.ecdfplot(plot_data['step4_l']['qoe'], label='Veritas (Low)', color=colors['veritas'], linestyle='dashed')
    h = sns.ecdfplot(plot_data['step4_h']['qoe'], label='Veritas (High)', color=colors['veritas'])


    plt.legend()
    plt.xlabel("QoE")
    plt.ylabel("CDF (Fraction of sessions)")
    plt.savefig(output_dir + '/' + 'cdf_qoe.png')
    plt.close()

    print(1)

    import numpy as np
    gap_qoe_4_h = (np.array(plot_data['step4_h']['qoe']) - np.array(plot_data['step1']['qoe']))*100/(np.array(plot_data['step1']['qoe']))
    gap_ssim_4_h = (np.array(plot_data['step4_h']['ssim']) - np.array(plot_data['step1']['ssim']))*100/(np.array(plot_data['step1']['ssim']))
    gap_diff_ssim_4_h = (np.array(plot_data['step4_h']['diff_ssim']) - np.array(plot_data['step1']['diff_ssim']))*100/(np.array(plot_data['step1']['diff_ssim']))
    gap_rebuf_4_h = (np.array(plot_data['step4_h']['rebuf']) - np.array(plot_data['step1']['rebuf']))*100/(np.array(plot_data['step1']['rebuf']))

    gap_qoe_4_l = (np.array(plot_data['step4_l']['qoe']) - np.array(plot_data['step1']['qoe']))*100/(np.array(plot_data['step1']['qoe']))
    gap_ssim_4_l = (np.array(plot_data['step4_l']['ssim']) - np.array(plot_data['step1']['ssim']))*100/(np.array(plot_data['step1']['ssim']))
    gap_diff_ssim_4_l = (np.array(plot_data['step4_l']['diff_ssim']) - np.array(plot_data['step1']['diff_ssim']))*100/(np.array(plot_data['step1']['diff_ssim']))
    gap_rebuf_4_l = (np.array(plot_data['step4_l']['rebuf']) - np.array(plot_data['step1']['rebuf']))*100/(np.array(plot_data['step1']['rebuf']))

    gap_qoe_2 = (np.array(plot_data['step2']['qoe']) - np.array(plot_data['step1']['qoe']))*100/(np.array(plot_data['step1']['qoe']))
    gap_ssim_2 = (np.array(plot_data['step2']['ssim']) - np.array(plot_data['step1']['ssim']))*100/(np.array(plot_data['step1']['ssim']))
    gap_diff_ssim_2 = (np.array(plot_data['step2']['diff_ssim']) - np.array(plot_data['step1']['diff_ssim']))*100/(np.array(plot_data['step1']['diff_ssim']))
    gap_rebuf_2 = (np.array(plot_data['step2']['rebuf']) - np.array(plot_data['step1']['rebuf']))*100/(np.array(plot_data['step1']['rebuf']))

    gap_qoe_3 = (np.array(plot_data['step3']['qoe']) - np.array(plot_data['step1']['qoe']))*100/(np.array(plot_data['step1']['qoe']))
    gap_ssim_3 = (np.array(plot_data['step3']['ssim']) - np.array(plot_data['step1']['ssim']))*100/(np.array(plot_data['step1']['ssim']))
    gap_diff_ssim_3 = (np.array(plot_data['step3']['diff_ssim']) - np.array(plot_data['step1']['diff_ssim']))*100/(np.array(plot_data['step1']['diff_ssim']))
    gap_rebuf_3 = (np.array(plot_data['step3']['rebuf']) - np.array(plot_data['step1']['rebuf']))*100/(np.array(plot_data['step1']['rebuf']))


    sns.ecdfplot(gap_qoe_4_l, label='HMM Min sample', color='r')
    sns.ecdfplot(gap_qoe_4_h, label='HMM Max sample', color='r')
    sns.ecdfplot(gap_qoe_2, label='Baseline', color='orange')
    sns.ecdfplot(gap_qoe_3, label='Ground truth', color='green')

    plt.legend()
    plt.xlabel("% change from deployment")
    plt.ylabel("Perc. of sessions")
    plt.savefig(output_dir + '/' + 'cdf_qoe_change.png')
    plt.close()

    sns.ecdfplot(gap_ssim_4_l, label='HMM Min sample', color='r')
    sns.ecdfplot(gap_ssim_4_h, label='HMM Max sample', color='r')
    sns.ecdfplot(gap_ssim_2, label='Baseline', color=colors['baseline'])
    sns.ecdfplot(gap_ssim_3, label='Ground truth', color='green')

    plt.legend()
    plt.xlabel("% change from deployment")
    plt.ylabel("Perc. of sessions")
    plt.savefig(output_dir + '/' + 'cdf_ssim_change.png')
    plt.close()

    sns.ecdfplot(gap_diff_ssim_4_l, label='HMM Min sample', color='r')
    sns.ecdfplot(gap_diff_ssim_4_h, label='HMM Max sample', color='r')
    sns.ecdfplot(gap_diff_ssim_2, label='Baseline', color='orange')
    sns.ecdfplot(gap_diff_ssim_3, label='Ground truth', color='green')

    plt.legend()
    plt.xlabel("% change from deployment")
    plt.ylabel("Perc. of sessions")
    plt.savefig(output_dir + '/' + 'cdf_diff_ssim_change.png')
    plt.close()

    sns.ecdfplot(gap_rebuf_4_l, label='HMM Min sample', color='r')
    sns.ecdfplot(gap_rebuf_4_h, label='HMM Max sample', color='r')
    sns.ecdfplot(gap_rebuf_2, label='Baseline', color='orange')
    sns.ecdfplot(gap_rebuf_3, label='Ground truth', color='green')

    plt.legend()
    plt.xlabel("% change from deployment")
    plt.ylabel("Perc. of sessions")
    plt.savefig(output_dir + '/' + 'cdf_rebuf_change.png')
    plt.close()

    sorted_rebuf = sorted(group['rebuf'], key=lambda tup: tup[2])
    sorted_ssim =  sorted(group['ssim'], key=lambda tup: tup[2])
    sorted_diff_ssim =  sorted(group['diff_ssim'], key=lambda tup: tup[2])
    sorted_qoe =  sorted(group['qoe'], key=lambda tup: tup[2])

    print(1)

    x = []
    step_1_rebuf = []
    step_1_ssim = []
    step_1_diff_ssim = []
    step_1_qoe = []
    step_2_rebuf = []
    step_2_ssim = []
    step_2_diff_ssim = []
    step_2_qoe = []
    step_3_rebuf = []
    step_3_ssim = []
    step_3_diff_ssim = []
    step_3_qoe = []
    step_4l_rebuf = []
    step_4l_ssim = []
    step_4l_diff_ssim = []
    step_4l_qoe = []
    step_4h_rebuf = []
    step_4h_ssim = []
    step_4h_diff_ssim = []
    step_4h_qoe = []

    for i in range(len(sorted_ssim)):
        x.append(i)
        step_1_rebuf.append(sorted_rebuf[i][0])
        step_1_ssim.append(sorted_ssim[i][0])
        step_1_diff_ssim.append(sorted_diff_ssim[i][0])
        step_1_qoe.append(sorted_qoe[i][0])

        step_2_rebuf.append(sorted_rebuf[i][1])
        step_2_ssim.append(sorted_ssim[i][1])
        step_2_diff_ssim.append(sorted_diff_ssim[i][1])
        step_2_qoe.append(sorted_qoe[i][1])

        step_3_rebuf.append(sorted_rebuf[i][2])
        step_3_ssim.append(sorted_ssim[i][2])
        step_3_diff_ssim.append(sorted_diff_ssim[i][2])
        step_3_qoe.append(sorted_qoe[i][2])

        step_4l_rebuf.append(sorted_rebuf[i][3])
        step_4l_ssim.append(sorted_ssim[i][3])
        step_4l_diff_ssim.append(sorted_diff_ssim[i][3])
        step_4l_qoe.append(sorted_qoe[i][3])

        step_4h_rebuf.append(sorted_rebuf[i][4])
        step_4h_ssim.append(sorted_ssim[i][4])
        step_4h_diff_ssim.append(sorted_diff_ssim[i][4])
        step_4h_qoe.append(sorted_qoe[i][4])

    plt.scatter(x, step_2_qoe, label='Baseline', color=colors['baseline'], marker='*')
    plt.scatter(x, step_3_qoe, label='Groundtruth (GTBW)', color='green', marker='^')
    plt.scatter(x, step_4l_qoe, label='Veritas (Low)', color='red', marker='1')
    plt.scatter(x, step_4h_qoe, label='Veritas (High)', color='red', marker='2')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("QoE")
    plt.savefig(output_dir + '/' + 'sorted_qoe.png')
    plt.close()


    plt.scatter(x, step_2_rebuf, label='Baseline', color=colors['baseline'], marker='*')
    plt.scatter(x, step_3_rebuf, label='Groundtruth (GTBW)', color='green', marker='^')
    plt.scatter(x, step_4l_rebuf, label='Veritas (Low)', color='red', marker='1')
    plt.scatter(x, step_4h_rebuf, label='Veritas (High)', color='red', marker='2')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("Rebuffering ratio (% of session)")
    plt.savefig(output_dir + '/' + 'sorted_rebuf.png')
    plt.close()

    plt.scatter(x, step_2_ssim, label='Baseline', color=colors['baseline'], marker='*')
    plt.scatter(x, step_3_ssim, label='Groundtruth (GTBW)', color='green', marker='^')
    plt.scatter(x, step_4l_ssim, label='Veritas (Low)', color='red', marker='1')
    plt.scatter(x, step_4h_ssim, label='Veritas (High)', color='red', marker='2')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("SSIM")
    plt.savefig(output_dir + '/' + 'sorted_ssim.png')
    plt.close()

    plt.scatter(x, step_2_diff_ssim, label='Baseline', color=colors['baseline'], marker='*')
    plt.scatter(x, step_3_diff_ssim, label='Groundtruth (GTBW)', color='green', marker='^')
    plt.scatter(x, step_4l_diff_ssim, label='Veritas (Low)', color='red', marker='1')
    plt.scatter(x, step_4h_diff_ssim, label='Veritas (High)', color='red', marker='2')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("Diff SSIM")
    plt.savefig(output_dir + '/' + 'sorted_diff_ssim.png')
    plt.close()
"""    
    step_1_traces = get_traces_from_steps(step_1)
    step_2_traces = get_traces_from_steps(step_2)
    step_3_traces = get_traces_from_steps(step_3)
    step_4_l_traces, step_4_h_traces = step_4_processing(step_4)

    plot_data = {}
    plot_data['step1'] = {}
    plot_data['step2'] = {}
    plot_data['step3'] = {}
    plot_data['step4_l'] = {}
    plot_data['step4_h'] = {}


    plot_data['step1']['qoe'] = []
    plot_data['step1']['ssim'] = []
    plot_data['step1']['rebuf'] = []
    plot_data['step1']['diff_ssim'] = []
    plot_data['step2']['qoe'] = []
    plot_data['step2']['ssim'] = []
    plot_data['step2']['rebuf'] = []
    plot_data['step2']['diff_ssim'] = []
    plot_data['step3']['qoe'] = []
    plot_data['step3']['ssim'] = []
    plot_data['step3']['rebuf'] = []
    plot_data['step3']['diff_ssim'] = []
    plot_data['step4_l']['qoe'] = []
    plot_data['step4_l']['ssim'] = []
    plot_data['step4_l']['rebuf'] = []
    plot_data['step4_l']['diff_ssim'] = []
    plot_data['step4_h']['qoe'] = []
    plot_data['step4_h']['ssim'] = []
    plot_data['step4_h']['rebuf'] = []
    plot_data['step4_h']['diff_ssim'] = []

    group = {}
    group['qoe'] = []
    group['ssim'] = []
    group['diff_ssim'] = []
    group['rebuf'] = []

    for trace_all in step_2_traces:
        trace = trace_all[:-2]
        trace = "_".join(trace_all[9:].split('_')[0:4])
        if trace in step_1_traces:
            if trace in step_3_traces:
                if trace in step_4_l_traces:
                    plot_data['step1']['qoe'].append(step_1_traces[trace]['value']/step_1_traces[trace]['len'])
                    plot_data['step1']['ssim'].append(step_1_traces[trace]['total_ssim']/step_1_traces[trace]['len'])
                    plot_data['step1']['rebuf'].append(step_1_traces[trace]['total_rebuf'] *100/ step_1_traces[trace]['total_play'] )
                    plot_data['step1']['diff_ssim'].append(step_1_traces[trace]['diff_ssim']/step_1_traces[trace]['len'])
                    plot_data['step2']['qoe'].append(step_2_traces[trace_all]['value']/step_2_traces[trace_all]['len'])
                    plot_data['step2']['ssim'].append(step_2_traces[trace_all]['total_ssim']/step_2_traces[trace_all]['len'])
                    plot_data['step2']['rebuf'].append(step_2_traces[trace_all]['total_rebuf']*100 / step_2_traces[trace_all]['total_play'])
                    plot_data['step2']['diff_ssim'].append(step_2_traces[trace_all]['diff_ssim']/step_2_traces[trace_all]['len'])
                    plot_data['step3']['qoe'].append(step_3_traces[trace]['value']/step_3_traces[trace]['len'])
                    plot_data['step3']['ssim'].append(step_3_traces[trace]['total_ssim']/step_3_traces[trace]['len'])
                    plot_data['step3']['rebuf'].append(step_3_traces[trace]['total_rebuf']*100 / step_3_traces[trace]['total_play'])
                    plot_data['step3']['diff_ssim'].append(step_3_traces[trace]['diff_ssim']/step_3_traces[trace]['len'])
                    plot_data['step4_l']['qoe'].append(step_4_l_traces[trace]['qoe'])
                    plot_data['step4_l']['ssim'].append(step_4_l_traces[trace]['ssim'])
                    plot_data['step4_l']['rebuf'].append(step_4_l_traces[trace]['rebuf']*100)
                    plot_data['step4_l']['diff_ssim'].append(step_4_l_traces[trace]['diff_ssim'])
                    plot_data['step4_h']['qoe'].append(step_4_h_traces[trace]['qoe'])
                    plot_data['step4_h']['ssim'].append(step_4_h_traces[trace]['ssim'])
                    plot_data['step4_h']['rebuf'].append(step_4_h_traces[trace]['rebuf']*100)
                    plot_data['step4_h']['diff_ssim'].append(step_4_h_traces[trace]['diff_ssim'])

                    group['qoe'].append((
                        step_1_traces[trace]['value'] / step_1_traces[trace]['len'],
                        step_2_traces[trace_all]['value'] / step_1_traces[trace]['len'],
                        step_3_traces[trace]['value'] / step_3_traces[trace]['len'],
                        step_4_l_traces[trace]['qoe'],
                        step_4_h_traces[trace]['qoe']
                    ))

                    group['ssim'].append((
                        step_1_traces[trace]['total_ssim'] / step_1_traces[trace]['len'],
                        step_2_traces[trace_all]['total_ssim'] / step_2_traces[trace_all]['len'],
                        step_3_traces[trace]['total_ssim'] / step_3_traces[trace]['len'],
                        step_4_l_traces[trace]['ssim'],
                        step_4_h_traces[trace]['ssim']
                    ))

                    group['diff_ssim'].append((
                        step_1_traces[trace]['diff_ssim'] / step_1_traces[trace]['len'],
                        step_2_traces[trace_all]['diff_ssim'] / step_2_traces[trace_all]['len'],
                        step_3_traces[trace]['diff_ssim'] / step_3_traces[trace]['len'],
                        step_4_l_traces[trace]['diff_ssim'],
                        step_4_h_traces[trace]['diff_ssim']
                    ))

                    group['rebuf'].append((
                        step_1_traces[trace]['total_rebuf'] * 100 / step_1_traces[trace]['total_play'],
                        step_2_traces[trace_all]['total_rebuf'] * 100 / step_2_traces[trace_all]['total_play'],
                        step_3_traces[trace]['total_rebuf'] * 100 / step_3_traces[trace]['total_play'],
                        step_4_l_traces[trace]['rebuf'] * 100,
                        step_4_h_traces[trace]['rebuf'] * 100
                    ))

    sorted_rebuf = sorted(group['rebuf'], key=lambda tup: tup[2])
    sorted_ssim =  sorted(group['ssim'], key=lambda tup: tup[2])
    sorted_diff_ssim =  sorted(group['diff_ssim'], key=lambda tup: tup[2])
    sorted_qoe =  sorted(group['qoe'], key=lambda tup: tup[2])

    x = []
    step_1_rebuf = []
    step_1_ssim = []
    step_1_diff_ssim = []
    step_1_qoe = []
    step_2_rebuf = []
    step_2_ssim = []
    step_2_diff_ssim = []
    step_2_qoe = []
    step_3_rebuf = []
    step_3_ssim = []
    step_3_diff_ssim = []
    step_3_qoe = []
    step_4l_rebuf = []
    step_4l_ssim = []
    step_4l_diff_ssim = []
    step_4l_qoe = []
    step_4h_rebuf = []
    step_4h_ssim = []
    step_4h_diff_ssim = []
    step_4h_qoe = []

    for i in range(len(sorted_ssim)):
        x.append(i)
        step_1_rebuf.append(sorted_rebuf[i][0])
        step_1_ssim.append(sorted_ssim[i][0])
        step_1_diff_ssim.append(sorted_diff_ssim[i][0])
        step_1_qoe.append(sorted_qoe[i][0])

        step_2_rebuf.append(sorted_rebuf[i][1])
        step_2_ssim.append(sorted_ssim[i][1])
        step_2_diff_ssim.append(sorted_diff_ssim[i][1])
        step_2_qoe.append(sorted_qoe[i][1])

        step_3_rebuf.append(sorted_rebuf[i][2])
        step_3_ssim.append(sorted_ssim[i][2])
        step_3_diff_ssim.append(sorted_diff_ssim[i][2])
        step_3_qoe.append(sorted_qoe[i][2])

        step_4l_rebuf.append(sorted_rebuf[i][3])
        step_4l_ssim.append(sorted_ssim[i][3])
        step_4l_diff_ssim.append(sorted_diff_ssim[i][3])
        step_4l_qoe.append(sorted_qoe[i][3])

        step_4h_rebuf.append(sorted_rebuf[i][4])
        step_4h_ssim.append(sorted_ssim[i][4])
        step_4h_diff_ssim.append(sorted_diff_ssim[i][4])
        step_4h_qoe.append(sorted_qoe[i][4])

    plt.scatter(x, step_2_qoe, label=step_2_type, color='orange', marker='*')
    plt.scatter(x, step_3_qoe, label='Groundtruth (GTBW)', color='green', marker='^')
    plt.scatter(x, step_4l_qoe, label='Veritas (Low)', color='red', marker='1')
    plt.scatter(x, step_4h_qoe, label='Veritas (High)', color='red', marker='2')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("QoE")
    plt.savefig(output_dir + '/' + 'sorted_qoe.png')
    plt.close()


    plt.scatter(x, step_2_rebuf, label=step_2_type, color='orange', marker='*')
    plt.scatter(x, step_3_rebuf, label='Groundtruth (GTBW)', color='green', marker='^')
    plt.scatter(x, step_4l_rebuf, label='Veritas (Low)', color='red', marker='1')
    plt.scatter(x, step_4h_rebuf, label='Veritas (High)', color='red', marker='2')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("Rebuffering ratio (% of session)")
    plt.savefig(output_dir + '/' + 'sorted_rebuf.png')
    plt.close()

    plt.scatter(x, step_2_ssim, label=step_2_type, color='orange', marker='*')
    plt.scatter(x, step_3_ssim, label='Groundtruth (GTBW)', color='green', marker='^')
    plt.scatter(x, step_4l_ssim, label='Veritas (Low)', color='red', marker='1')
    plt.scatter(x, step_4h_ssim, label='Veritas (High)', color='red', marker='2')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("SSIM")
    plt.savefig(output_dir + '/' + 'sorted_ssim.png')
    plt.close()

    plt.scatter(x, step_2_diff_ssim, label=step_2_type, color='orange', marker='*')
    plt.scatter(x, step_3_diff_ssim, label='Groundtruth (GTBW)', color='green', marker='^')
    plt.scatter(x, step_4l_diff_ssim, label='Veritas (Low)', color='red', marker='1')
    plt.scatter(x, step_4h_diff_ssim, label='Veritas (High)', color='red', marker='2')

    plt.legend()
    plt.xlabel("Traces")
    plt.ylabel("Diff SSIM")
    plt.savefig(output_dir + '/' + 'sorted_diff_ssim.png')
    plt.close()
    
"""