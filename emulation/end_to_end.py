import os
from os import path
import time
import signal
from subprocess import check_call, Popen
import sys
from shutil import copyfile, rmtree
import subprocess
import shlex
import datetime
import argparse
import yaml


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mahimahi_dir", type=str, required=True)
    parser.add_argument("--settings_yml", type=str, required=True)
    parser.add_argument("--type", type=str, required=True, choices=['deployment',
                                                                    'groundtruth', 'veritas', 'baseline'])

    args = parser.parse_args()
    return args

def start_mahimahi_clients(p1, p2, mm_filepath):

    # create a temporary directory to store Chrome sessions
    chrome_sessions = "chrome-sessions"
    if not path.exists(chrome_sessions):
        os.makedirs(chrome_sessions)

    # declare variable to store a list of processes
    plist = []

    try:
        port = 9361
        remote_debugging_port = 10000
        plist = []

        # downlink: trace_dir/TRACE (to transmit video)
        # uplink: 12 Mbps (fast enough for ack messages)
        if 'delay' in mm_filepath:
            delay = int(mm_filepath.split('_')[1])
        else:
            delay = 40
        if 'duration' in mm_filepath:
            play_duration = int(float(mm_filepath.split('duration_')[1].split('_')[0]))
            if play_duration == 720:
                play_duration = 600
        else:
            play_duration = 320

        mahimahi_chrome_cmd = "mm-delay {} mm-link 12Mbps {} -- sh -c " \
                              "'google-chrome --headless --disable-gpu --remote-debugging-port={} " \
                              "http://$MAHIMAHI_BASE:8080/player/?wsport={} " \
                              "--user-data-dir={}/{}.profile'".format(
                                delay, mm_filepath, remote_debugging_port,
                                port, chrome_sessions, port)

        print(mahimahi_chrome_cmd)

        p = Popen(mahimahi_chrome_cmd.encode('utf-8'),
                  shell=True, preexec_fn=os.setsid)
        plist.append(p)
        time.sleep(4)  # don't know why but seems necessary

        time.sleep(play_duration + 10)

        p1.terminate()
        p2.terminate()

        for p in plist:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            time.sleep(4)

        rmtree(chrome_sessions, ignore_errors=True)
    except Exception as e:
        print("exception: " + str(e))
        pass
    finally:
        for p in plist:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            rmtree(chrome_sessions, ignore_errors=True)


def main():

    args = parse_arguments()

    mahi_mahi_files = os.listdir(args.mahimahi_dir)

    readme = open("readme", "a+")
    readme.write("#### {} #### \n".format(args.type))
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    readme.write("Start: " + str(current_time) + "\n")
    readme.close()

    for i in range(0, len(mahi_mahi_files)):


        with open(args.settings_yml, 'r') as f:
            data = yaml.safe_load(f)
        f.close()

        data["trace"] = "_" + mahi_mahi_files[i].replace(".txt", "")
        with open(args.settings_yml, 'w') as f:
            yaml.dump(data, f)

        server_cmd = "sudo sysctl -w net.ipv4.tcp_slow_start_after_idle=0; " \
                     "sysctl net.ipv4.tcp_slow_start_after_idle;" \
                     "sudo sysctl -w  net.ipv4.tcp_no_metrics_save=1; " \
                     "/opt/puffer/src/portal/manage.py runserver 0:8080"

        p1 = Popen(server_cmd.encode('utf-8'), shell=True, preexec_fn=os.setsid)
        time.sleep(5)
        media_server_cmd = "sudo sysctl -w net.ipv4.tcp_slow_start_after_idle=0; " \
                           "sysctl net.ipv4.tcp_slow_start_after_idle;" \
                           "sudo sysctl -w net.ipv4.tcp_no_metrics_save=1; " \
                           "/opt/puffer/src/media-server/run_servers /opt/puffer/src/" \
                           + args.settings_yml

        p2 = Popen(media_server_cmd.encode('utf-8'), shell=True, preexec_fn=os.setsid)
        time.sleep(5)

        # assume web server and media server are both running
        start_mahimahi_clients(p1, p2, os.path.join(args.mahimahi_dir, mahi_mahi_files[i]))
        os.system('kill -9 $(pgrep -f /opt/puffer/)')

    readme = open("readme", "a+")
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    readme.write("End: " + str(current_time) + "\n")
    readme.write("######## \n")
    readme.close()


if __name__ == '__main__':
    main()


