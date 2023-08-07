#Create a directory for the experiment: <dummy-exp>
#Assuming the FCC cooked (per second throughput) traces are copied to <test-sample> directory in the <dummy-exp> directory.

#Get the mahimahi trace for the sample traces.
python3 cooked_to_mm.py dummy-exp/test-sample dummy-exp/mm-sample

#Assuming our Q is what-if we move from low qualities to high qualities: Deployment: low, Groundtruth: high.
#Run video streaming for mahimahi traces for deployment.
python3 end_to_end.py dummy-exp dummy-exp/mm-sample ../src/veritas-lowest.yml deployment

#Run video streaming for mahimahi traces for groundtruth.
python3 end_to_end.py dummy-exp dummy-exp/mm-sample ../src/veritas-highest.yml groundtruth

#Get the video session streams from deployment [use smart to get the start and end time from readme.].
python3 get_video_sessions.py dummy-exp deployment localhost --smart 1

#Get baseline traces from the video sessions.
python3 get_baseline_traces.py dummy-exp dummy-exp/deployment

#Get the mahimahi traces from the baseline.
python3 baseline_to_mm.py dummy-exp dummy-exp/baseline

#Run video streaming for mahimahi traces using baseline.
python3 end_to_end.py dummy-exp dummy-exp/mm-baseline ../src/veritas-highest.yml baseline

#Map the video sessions into Veritas format.
python3 convert_to_veritas.py dummy-exp fcc_cooked dummy-exp/deployment

#Create/copy the Veritas training and inference configuration
cp Veritas/src/data/datasets/Controlled-GT-Cubic-BBA-Low/train_config.yaml dummy-exp/veritas
cp Veritas/src/data/datasets/Controlled-GT-Cubic-BBA-Low/inference_config.yaml dummy-exp/veritas

#Run Veritas
cd Veritas
python3 scripts/get_fhash.py --input_directory ../dummy-exp/veritas
python3 scripts/get_full.py --input_directory ../dummy-exp/veritas
python3 scripts/train.py --input_directory ../dummy-exp/veritas

#Be careful to pass the trained model path.
python3 scripts/inference.py --input_directory ../dummy-exp/veritas --trained_model <model_path>

#Get the Veritas samples
cd ..
python3 get_veritas_samples.py dummy-exp  --veritas_transform_dir <Veritas transform directory path> --transition_time_step 5 --emulation_session_len 320

#Get Veritas mahimahi traces
python3 get_veritas_mahimahi.py dummy-exp dummy-exp/veritas-samples 5

#Run video streaming for mahimahi traces using Veritas.
python3 end_to_end.py dummy-exp dummy-exp/mm-veritas ../src/veritas-highest.yml veritas

#Plot results
python3 plot_results.py dummy-exp
