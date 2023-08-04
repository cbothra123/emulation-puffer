import sys
import numpy as np
import json
import os

from influxdb import InfluxDBClient

port = 8086
user = 'puffer'
password = os.environ['INFLUXDB_PASSWORD']
dbname = 'puffer'

VIDEO_DURATION = 180180
PKT_BYTES = 1500
MILLION = 1000000
THOUSAND = 1000

expt_id_cache = {}

def get_expt_id(pt):
    if pt['expt_id'] is not None:
        return int(pt['expt_id'])
    elif pt['expt_id_1'] is not None:
        return int(pt['expt_id_1'])

    return None

def get_user(pt):
    if pt['user'] is not None:
        return pt['user']
    elif pt['user_1'] is not None:
        return pt['user_1']

    return None

def connect_to_influxdb(host, port, user, password, dbname):
    influx_client = InfluxDBClient(
        host, port, user,
        password, dbname)
    sys.stderr.write('Connected to the InfluxDB at {}:{}\n'
                     .format(host, port))
    return influx_client

def create_time_clause(time_start, time_end):
    time_clause = None

    if time_start is not None:
        time_clause = "time >= '{}'".format(time_start)
    if time_end is not None:
        if time_clause is None:
            time_clause = "time <= '{}'".format(time_end)
        else:
            time_clause += " AND time <= '{}'".format(time_end)

    return time_clause

def calculate_trans_times(video_sent_results, video_acked_results):
    d = {}
    last_video_ts = {}

    for pt in video_sent_results['video_sent']:
        expt_id = get_expt_id(pt)

        session = get_user(pt) + '_' + str(pt['init_id']) + '_' + pt['channel'] + '_' + str(expt_id)

        if session not in d:
            d[session] = {}
            last_video_ts[session] = None

        video_ts = int(pt['video_ts'])

        if last_video_ts[session] is not None:
            if video_ts != last_video_ts[session] + VIDEO_DURATION:
                continue

        last_video_ts[session] = video_ts

        d[session][video_ts] = {}
        dsv = d[session][video_ts]  # short name

        dsv['sent_ts'] = pt['time']
        dsv['size'] = float(pt['size']) / PKT_BYTES  # bytes -> packets
        # byte/second -> packet/second
        dsv['delivery_rate'] = float(pt['delivery_rate']) / PKT_BYTES
        dsv['cwnd'] = float(pt['cwnd'])
        dsv['in_flight'] = float(pt['in_flight'])
        dsv['min_rtt'] = float(pt['min_rtt']) / MILLION  # us -> s
        dsv['rtt'] = float(pt['rtt']) / MILLION  # us -> s
        if 'rto' in pt:
            dsv['rto'] = float(pt['rto']) / MILLION  # us -> s
        else:
            dsv['rto'] = 0.0
        if 'last_snd' in pt:
            dsv['last_snd'] = float(pt['last_snd']) / THOUSAND #ms -> s
        else:
            dsv['last_snd'] = 0.0
        if 'ssthresh' in pt:
            dsv['ssthresh'] = float(pt['ssthresh'])
        else:
            dsv['ssthresh'] = 0.0
        dsv['quality'] = pt['format']
        if 'bytes_sent' in pt:
            dsv['bytes_sent'] = pt['bytes_sent']
        else:
            dsv['bytes_sent'] = 'NA'
        if 'bytes_retrans' in pt:
            dsv['bytes_retrans'] = pt['bytes_retrans']
        else:
            dsv['bytes_retrans'] = 'NA'
        if 'ssim_index' in pt:
            dsv['ssim_index'] = pt['ssim_index']
        else:
            dsv['ssim_index'] = 'NA'
        if 'cum_rebuffer' in pt:
            dsv['cum_rebuffer'] = pt['cum_rebuffer']
        else:
            dsv['cum_rebuffer'] = 'NA'
        if 'buffer' in pt:
            dsv['buffer'] = pt['buffer']
        else:
            dsv['buffer'] = 'NA'
        if 'format' in pt:
            dsv['quality'] = pt['format']
        else:
            dsv['quality'] = 'NA'
            
    for pt in video_acked_results['video_acked']:
        expt_id = get_expt_id(pt)

        session = get_user(pt) + '_' + str(pt['init_id']) + '_' + pt['channel'] + '_' + str(expt_id)

        if session not in d:
            continue

        video_ts = int(pt['video_ts'])
        if video_ts not in d[session]:
            continue

        dsv = d[session][video_ts]  # short name

        # calculate transmission time
        sent_ts = np.datetime64(dsv['sent_ts'])
        acked_ts = np.datetime64(pt['time'])
        
        first_frame = int(pt['first_frame']) if 'first_frame' in pt else 0
        last_frame = int(pt['last_frame']) if 'last_frame' in pt else 0
        
        dsv['client_trans'] = (first_frame - last_frame)
        
        if 'client_trans_time' in pt:
            client_trans_time = float(pt['client_trans_time'])
        else:
            client_trans_time = 0

        dsv['acked_ts'] = str(np.datetime64(pt['time'])) + 'Z'
        dsv['trans_time'] = (acked_ts - sent_ts) / np.timedelta64(1, 's')
        dsv['client_trans_time'] = client_trans_time

    return d

def endpoint(host, start, end):
    time_clause = create_time_clause(start, end)
    influx_client = connect_to_influxdb(host, port, user, password, dbname)

    # perform queries in InfluxDB
    video_sent_query = 'SELECT * FROM video_sent'
    if time_clause is not None:
        video_sent_query += ' WHERE ' + time_clause
    video_sent_results = influx_client.query(video_sent_query)
    if not video_sent_results:
        sys.exit('Error: no results returned from query: ' + video_sent_query)

    video_acked_query = 'SELECT * FROM video_acked'
    if time_clause is not None:
        video_acked_query += ' WHERE ' + time_clause
    video_acked_results = influx_client.query(video_acked_query)
    if not video_acked_results:
        sys.exit('Error: no results returned from query: ' + video_acked_query)

    # calculate chunk transmission times
    ret = calculate_trans_times(video_sent_results, video_acked_results)
    print(len(ret))
    return ret

def parser_influx(host, start_time, end_time, video_streaming_dir):
    res = endpoint(host, start_time, end_time)

    for session in res:

        session_name = session
        log_file = open(video_streaming_dir + '/' + session_name, 'w')
        log_file.write('index,start_time,end_time,size,trans_time,cwnd,rtt,rto,ssthresh,last_snd,min_rtt,'
                       'delivery_rate,bytes_sent,bytes_retrans,client_trans_time,ssim_index,cum_rebuffer,buffer,quality\n')

        index = 0
        for element in res[session]:
            if 'size' in  res[session][element]:
                if 'delivery_rate' in res[session][element]:
                    if 'trans_time' in res[session][element]:
                        if 'cwnd' in res[session][element]:
                            if 'rtt' in res[session][element]:
                                trans_time_adjust = str((res[session][element]['trans_time']*1000))
                                log_file.write(str(index) + ',' + str(res[session][element]['sent_ts']) + ',' +
                                                str(res[session][element]['acked_ts']) + ',' +
                                                str((res[session][element]['size']*1500)/1000) + ',' +
                                                trans_time_adjust + ',' +
                                                str(res[session][element]['cwnd']) + ',' +
                                                str(res[session][element]['rtt']*1000) + ',' +
                                                str(res[session][element]['rto']*1000) + ',' +
                                                str(res[session][element]['ssthresh']) + ',' +
                                                str(res[session][element]['last_snd']) + ',' +
                                                str(res[session][element]['min_rtt']*1000) + ',' +
                                                str((res[session][element]['delivery_rate']*1500*8)/1000000) + ',' +
                                                str(res[session][element]['bytes_sent']) + ',' +
                                                str(res[session][element]['bytes_retrans']) + ',' +
                                                str(res[session][element]['client_trans']) + ',' +
                                                str(res[session][element]['ssim_index']) + ',' +
                                                str(res[session][element]['cum_rebuffer']) + ',' +
                                                str(res[session][element]['buffer']) + ',' + 
                                                str(res[session][element]['quality']) + '\n' 
                                                )
                                index+=1
    return 1