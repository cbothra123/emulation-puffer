[Puffer](https://puffer.stanford.edu) is an open-source "YouTube TV" built from scratch, streaming live television channels for free over the Internet. We are also operating it as an open research platform for the community to design and validate adaptive bitrate (ABR) algorithms, congestion control, and network prediction algorithms. Please refer to our [research paper](https://www.usenix.org/conference/nsdi20/presentation/yan) (*Community Award* winner at NSDI 2020) for more details.

As a production-grade system with a large codebase and more than 200,000 real users today, building Puffer locally is certainly a non-trivial task. You may want to focus only on the components that are of interest to you, and feel free to let us know in the [Google group](https://groups.google.com/forum/#!forum/puffer-stanford) if anything is not clear or what we can do to simplify the process.

This documentation has been tested on Ubuntu 18.04, 20.04 and 22.04.

## Prerequisite compilation

1. Clone and fetch submodules:
    ```
    git clone https://github.com/StanfordSNR/puffer  
    cd puffer/
    git submodule update --recursive --init
    ```
    
    Unless otherwise specified, all the relative paths in this documentation refer to locations relative to `puffer/`, which we assume resides in your home directory `~`.

2. Update package lists and install dependencies:

    ```
    automake
    autoconf
    gcc >= 7.0
    g++ >= 7.0
    python3
    wget
    zip
    libmpeg2-4-dev
    opus-tools
    libopus-dev
    libsndfile-dev
    libavformat-dev
    libavutil-dev
    libpq-dev
    libyaml-cpp-dev
    libssl-dev
    libcrypto++-dev
    liba52-dev
    ffmpeg
    cmake
    ```

    Two additional dependencies are required: 1) `libpqxx >= 7.0.0`, which needs to be built from https://github.com/jtv/libpqxx.git; 2) `libtorch`: download [libtorch-v1.8.1.cpu.zip](https://github.com/StanfordSNR/pytorch/releases/download/v1.8.1-puffer/libtorch-v1.8.1-cpu.zip) and unzip it into a folder `third_party/libtorch`. You may also download libtorch from the [official website](https://pytorch.org/get-started/locally/), where you select "LTS", "Linux", "LibTorch", "C++/Java", "CPU", "cxx11 ABI".

3. Puffer's media server normally uses a secure WebSocket to transmit video to clients, which would require an SSL certificate to establish the connection. For simplicity, let's compile a non-secure WebSocket server without the need of an SSL certificate.

    ```
    ./autogen.sh
    ./configure
    make -j CXXFLAGS='-DNONSECURE'
    ```

    Without the flag `-DNONSECURE`, a secure WebSocket server would be built, and you would have to run `make clean` and rebuild the non-secure WebSocket server before proceeding.

## Web server and media server
Puffer's web server hosts the [website](https://puffer.stanford.edu) (including a JavaScript video client) and authenticates users. When an authenticated user starts playing a TV channel, the video client will establish a WebSocket connection to receive video from one of Puffer's media server, which runs one of a set of ABR or congestion control algorithms. Playing video locally through Puffer requires setting up both the web server and the media server.

1. Install pip3 (`python3-pip`) and use pip3 to install the below Python modules:

    ```
    pip3 install django psycopg2-binary influxdb pyyaml matplotlib torch flask
    ```
    and then after `django` is installed, run
    ```
    pip3 install django[argon2]
    ```

    Make sure Django's version is >= 2.1, and generate a random string to be used as the web 
    server key.

2. Install PostgreSQL (`postgresql`), which stores user information and experimental configuration (e.g., which ABR algorithms and what algorithm parameters are being tested). As an example throughout the documentation, let's configure it to run on `127.0.0.1:5432`, and create a database called `puffer` and a user `puffer` with all privileges. You may run

    ```
    # install Postgres
    $ sudo apt install postgresql

    # switch to user "postgres" and access the Postgres command line interface
    $ sudo -u postgres psql

    # create a database "puffer"
    postgres=# CREATE DATABASE puffer;

    # create a user "puffer"
    postgres=# CREATE USER puffer WITH PASSWORD '<postgres password>';

    # grant all privileges of the database "puffer" to the user "puffer"
    postgres=# GRANT ALL PRIVILEGES ON DATABASE puffer TO puffer;

    # exit the Postgres prompt
    postgres=# \q
    ```
    
    Make sure you are able to connect to the local Postgres database, e.g., by running

    ```
    psql "host=127.0.0.1 port=5432 dbname=puffer user=puffer password=<postgres password>"
    ```

3. Create environment variables to securely store your web server key and Postgres password. For instance, you may append two lines to `~/.bashrc`

    ```
    export PUFFER_PORTAL_SECRET_KEY='<web server key>'
    export PUFFER_PORTAL_DB_KEY='<postgres password>'
    ```

    and execute `source ~/.bashrc`.

4. Create a YAML file `settings.yml` under `src/`; it manages almost every configuration of Puffer in one place. For now, just put in

    ```
    portal_settings:
      allowed_hosts:
        - '*'
      debug: true
      secret_key: PUFFER_PORTAL_SECRET_KEY
    postgres_connection:
      host: 127.0.0.1
      port: 5432
      dbname: puffer
      user: puffer
      password: PUFFER_PORTAL_DB_KEY
    ws_base_port: 50000
    experiments:
      - num_servers: 1
        fingerprint:
          abr: linear_bba
          abr_config:
            upper_reservoir: 0.9
          cc: cubic
    enable_logging: false
    ```

    The current settings let us run a single media server at port 50000, using the simplest ABR algorithm [BBA](http://yuba.stanford.edu/~nickm/papers/sigcomm2014-video.pdf) and Cubic for congestion control. Data logging is disabled for now (`enable_logging: false`). Do **not** replace `PUFFER_PORTAL_SECRET_KEY` or `PUFFER_PORTAL_DB_KEY` with your actual password; they are string literals pointing Puffer to the correct environment variables.

5. Apply Puffer's database schema to the Postgres database

    ```
    ./src/portal/manage.py migrate
    ```

6. Serve static files (e.g., JavaScript and CSS) by creating a symbolic link to `third_party/dist-for-puffer`

    ```
    ln -s ../../../../../third_party/dist-for-puffer/ src/portal/puffer/static/puffer/dist
    ```

    Make sure you have fetched git submodules to access the latest `third_party/dist-for-puffer`.

7. Start a development web server with

    ```
    ./src/portal/manage.py runserver 0:8080
    ```

    Visit `127.0.0.1:8080` to verify that the home page of Puffer displays correctly, and you can sign up and log in.

8. Download pre-recorded [TV clips](https://storage.googleapis.com/puffer-stanford-public/media-181230.tar.gz) (~7GB) for testing purpose. Among all the pre-recorded channels, the NBC channel has the longest video of more than 10 minutes. After uncompressing the tar file into, say,  `/home/ubuntu/media-181230`, you need to append the lines below to `src/settings.yml`:

    ```
    media_dir: /home/ubuntu/media-181230
    enforce_moving_live_edge: false
    channels:
      - abc
      - nbc
      - fox
      - pbs
      - cbs
      - univision
    channel_configs:
      abc:
        live: true
        video:
          1280x720: [20, 22, 24, 26]
          854x480: [22, 24, 26]
          640x360: [24, 26]
          426x240: [26]
        audio:
          - 128k
          - 64k
          - 32k
        present_delay_chunk: 300
      nbc:
        live: true
        video:
          1920x1080: [22, 24]
          1280x720: [20, 22, 24, 26]
          854x480: [24, 26]
          640x360: [24]
          426x240: [26]
        audio:
          - 128k
          - 64k
          - 32k
        present_delay_chunk: 300
      fox:
        live: true
        video:
          1280x720: [20, 22, 24, 26]
          854x480: [22, 24, 26]
          640x360: [24, 26]
          426x240: [26]
        audio:
          - 128k
          - 64k
          - 32k
        present_delay_chunk: 300
      pbs:
        live: true
        video:
          1920x1080: [22, 24]
          1280x720: [20, 22, 24, 26]
          854x480: [24, 26]
          640x360: [24]
          426x240: [26]
        audio:
          - 128k
          - 64k
          - 32k
        present_delay_chunk: 300
      cbs:
        live: true
        video:
          1920x1080: [22, 24]
          1280x720: [20, 22, 24, 26]
          854x480: [24, 26]
          640x360: [24]
          426x240: [26]
        audio:
          - 128k
          - 64k
          - 32k
        present_delay_chunk: 300
      univision:
        live: true
        video:
          1280x720: [20, 22, 24, 26]
          854x480: [22, 24, 26]
          640x360: [24, 26]
          426x240: [26]
        audio:
          - 128k
          - 64k
          - 32k
        present_delay_chunk: 300
    ```

    where `enforce_moving_live_edge` allows for testing pre-recorded video instead of live streaming; alternatively, set `live: false` to play a pre-recorded video from the beginning. The bitrate ladder of each channel must match what is pre-encoded in the media archive.

9. Finally, run Puffer's media server with

    ```
    cd src/
    ./media-server/run_servers settings.yml
    ```

    and click on "Watch TV" to play the pre-recorded TV clips. Note that the pre-recorded channels may not match exactly the currently available channels in the player, so some channels (e.g., the CW) may not be playable.

## Logging data
Puffer uses InfluxDB to record time-series data for analysis and monitoring purposes. In particular, the data contains each client's playback buffer level over time, timestamps when a video chunk is sent and acknowledged, and the size and SSIM of each chunk. 

1. [Install InfluxDB](https://docs.influxdata.com/influxdb/v1.7/introduction/installation/)

    ```
    # add the InfluxData repository
    wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
    source /etc/lsb-release
    echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

    # install and start the InfluxDB service
    sudo apt-get update && sudo apt-get install influxdb
    sudo systemctl unmask influxdb.service
    sudo systemctl start influxdb

    # [optional] start InfluxDB automatically after reboots
    sudo systemctl enable influxdb
    ```

    By default, InfluxDB runs on `127.0.0.1:8086`.

2. InfluxDB has disabled authentication by default, but we recommend to create an admin user and enable authentication.

    First, create an admin user `puffer`

    ```
    # access InfluxDB shell
    $ influx

    # create an admin user "puffer"
    > CREATE USER puffer WITH PASSWORD '<influxdb password>' WITH ALL PRIVILEGES
    ```
    
    Next, modify `/etc/influxdb/influxdb.conf` to enable authentication by setting the `auth-enabled` option to `true` in the `[http]` section
    ```
    [http]
      ...
      auth-enabled = true
    ```

    Finally, restart InfluxDB for these changes to take effect. 
    ```
    sudo systemctl restart influxdb
    ```

3. Verify the authentication and create a database `puffer`

    ```
    # access InfluxDB shell
    $ influx

    # authenticate as the "puffer" user
    > auth
    username: puffer
    password: <influxdb password>

    # create a database "puffer" to store Puffer data
    > CREATE DATABASE puffer

    # check if "puffer" database has been created 
    > SHOW DATABASES
    ```

   If everything looks good, save the InfluxDB password in an environment variable `INFLUXDB_PASSWORD`.

4. Configure Puffer in `src/settings.yml` to start logging data into InfluxDB

    ```
    enable_logging: true
    log_dir: /home/ubuntu/puffer/src/monitoring
    influxdb_connection:  
      host: 127.0.0.1
      port: 8086
      dbname: puffer
      user: puffer
      password: INFLUXDB_PASSWORD 
    ```

    Note that `enable_logging` is set to `true` now, and do **not** replace `INFLUXDB_PASSWORD` with your actual InfluxDB password (it is a string literal pointing Puffer to the environment variable). The `log_dir` must be the absolute path to `src/monitoring`, where you should see `*.conf` files such as `client_buffer.conf`. `src/monitoring/log_reporter.cc` uses these `*.conf` files to interpret the log data output by media servers (e.g., `client_buffer.1.log`), and asynchronously posts the data to InfluxDB.

## Encode recorded video for streaming
Besides the provided [TV clips](https://storage.googleapis.com/puffer-stanford-public/media-181230.tar.gz), you may encode any other videos into the format and folder hierarchy accepted by Puffer. Nonetheless, Puffer only provides code for encoding `.ts` ([MPEG transport stream](https://en.wikipedia.org/wiki/MPEG_transport_stream)) files.

Below we encode a small `.ts` file [leno.ts](https://storage.googleapis.com/puffer-stanford-public/leno.ts) as an example. Longer videos can be download [here](https://storage.googleapis.com/puffer-stanford-public/ts-10m-210516.tar.gz), where each `.ts` file is 10 minutes long.

1. Create two empty folders, e.g., `~/leno-raw-video` and `~/leno-raw-audio`. Decode `leno.ts` using the command below and wait for its completion:
   ```
   ~/puffer/src/atsc/decoder 0x21 0x24 1080i30 60 900 10248 ~/leno-raw-video ~/leno-raw-audio < leno.ts
   ```
   The 6 arguments following `decoder` are different for each channel, and can be found [here](https://github.com/StanfordSNR/puffer/wiki/Notes-for-Puffer-staff) (search for `decoder_args`).

2. Create a YAML file `leno.yml` to indicate encoding settings, e.g., output directory `/home/ubuntu/leno-show`, two video and audio qualities, not live streaming, no logging, no cleaning of encoded ("ready") media, no decoder (since step #1 has run the decoder):
    ```
    media_dir: /home/ubuntu/leno-show
    channels:
      - leno
    channel_configs:
      leno:
        video:
          1920x1080: [23]
          1280x720: [23]
        audio:
          - 128k
          - 64k
        live: false
    enable_logging: false
    clean_ready_media: false
    decoder: false
    ```

3. Run `~/puffer/src/wrappers/run_pipeline leno.yml` in a terminal, but note that it does not start encoding yet. The encoding will be triggered by each video or audio file *moved* into the folder `leno-show/working/video-raw` or `leno-show/working/audio-raw`, respectively. File copy or other events do not trigger encoding.

   Since video encoding may easily overload the system (especially if all files are moved at once), it is recommended to pace the moving, e.g., run the following commands in a terminal to sleep for `N` seconds between two file movements to avoid system overload (`N` depends on how many video qualities to encode, how many CPU cores are available, etc.):
   ```
   cd ~/leno-raw-video
   for f in *.y4m; do echo $f; mv $f /home/ubuntu/leno-show/working/video-raw; sleep <N>; done
   ``` 

   Wait for the encoding to complete. Audio files might be okay to move at once. There should be better ways to move a new file only when the system is not overloaded. 

4. To stream `leno-show` from Puffer's player page, modify `~/puffer/src/portal/puffer/templates/puffer/player.html` and add a new channel named `leno`. The encoding specs in `leno.yml` will also need to be copied into the primary `settings.yml`.

# Use live feeds for streaming
Streaming live feeds is more complex. You will need to have your live feeds output transport stream in real time to our `decoder` program. Instead of piping a `.ts` file into the `decoder` as described above, the `decoder` also takes an optional parameter `--tcp <IP>:<port>`, where the IP and port are the address from which it is able to read the transport stream in real time over a TCP connection.

Puffer receives the channels with a VHF/UHF TV antenna connected to a Blonder Tongue AQT8-IP receiver, which demodulates the MPEG-2 transport stream and encapsulates it into UDP datagrams. We then forward the UDP datagrams over a TCP connection using `src/forwarder/udp_to_tcp`, which allows the `decoder` to read from with the `--tcp` option.

## How to add your own ABR algorithm

To add a new ABR algorithm to Puffer, please check out the existing ABR implementations in `src/abr`. Taking BBA as an example: We created new files `linear_bba.hh` and `linear_bba.cc` in `src/abr`, and made the new class `LinearBBA` inherit from class `ABRAlgo` and fill in two callback functions:

```
virtual void video_chunk_acked(Chunk &&) {}
virtual VideoFormat select_video_format() = 0;
```

`video_chunk_acked` will be called by the `WebSocketServer` (in `src/media-server/ws_media_server.cc`) every time when a video chunk (`Chunk`) is acknowledged by a client, represented as a member variable `client_` of class `WebSocketClient`. It gives the new ABR algorithm an opportunity to maintain internal states; `LinearBBA` skips this callback as it is stateless.

`select_video_format` will be called when the `WebSocketServer` needs to determine a version (`VideoFormat`) of the next video chunk to serve the client. `LinearBBA` selects the version only based on client's current playback buffer level (`client_.video_playback_buf()`).

## About `settings.yml`

* Both web and media servers will need to be restarted after a change is made to `settings.yml`.

* The `experiments` section is used to specify a list of experiments to run; each will be automatically assigned a unique ID (`expt_id`) and saved in PostgreSQL. In each experiment, you may specify as `num_servers` the number of media server processes running that experiment, and its parameters in `fingerprint`. You can set an ABR algorithm in `abr`, which will instantiate the corresponding ABR object (`WebSocketClient::init_abr_algo()` in `src/media-server/ws_client.cc`); you can also specify a congestion control algorithm in `cc`, which will be passed as a string to `setsockopt(IPPROTO_TCP, TCP_CONGESTION, <cc>)`.

    Example: To start four media server processes, with two running `linear_bba/bbr` (must enable TCP BBR on the OS first), and the other two running `puffer_ttp/bbr` (must download the TTP model trained on 2/2/2019 from our website):

    ```
    experiments:
      - num_servers: 2
        fingerprint:
          abr: linear_bba
          abr_config:
            upper_reservoir: 0.9
          cc: bbr
      - num_servers: 2
        fingerprint:
          abr: puffer_ttp
          abr_config:
            model_dir: /path/to/puffer/ttp/models/bbr-20190202-1
            rebuffer_length_coeff: 100
          cc: bbr
    ```

## Troubleshooting

* Since Puffer's `notifier` leverages `inotify` to monitor file system events, the below error may occur if the file watch limit of `inotify` is too low:
    ```
    terminate called after throwing an instance of 'unix_error'
      what():  inotify_init: Too many open files
    ```
    To solve the issue, increase the limit (temporarily) with
    ```
    sudo sysctl -w fs.inotify.max_user_instances=<LARGE VALUE>
    sudo sysctl -w fs.inotify.max_user_watches=<LARGE VALUE>
    ```
