exp_num=3
max_components=50
min_size=100
duration=1200
input='../output/180s/app_traffic_180s.csv'
output_dir='../results/1200s'
time_interval=5
size_interval=100

mkdir $output_dir/$exp_num

python main.py -m=clustering --input=$input --output=$output_dir/$exp_num/original.csv --gmm-max-components=$max_components --gmm-min-cluster-size=$min_size
python main.py -m=stats --input=$output_dir/$exp_num/original.csv --output=$output_dir/$exp_num/original_stats.json 
python main.py -m=distributions --input=$output_dir/$exp_num/original.csv --output=$output_dir/$exp_num/original_dist.json --size-interval=$size_interval --time-interval=$time_interval

python main.py -m=generate --input=$output_dir/$exp_num/original_stats.json --output=$output_dir/$exp_num/gen_normal.csv --duration=$duration
python main.py -m=generate --input=$output_dir/$exp_num/original_dist.json  --output=$output_dir/$exp_num/gen_dist.csv --duration=$duration

python main.py -m=stats --input=$output_dir/$exp_num/gen_normal.csv --output=$output_dir/$exp_num/gen_normal_stats.json 
python main.py -m=stats --input=$output_dir/$exp_num/gen_dist.csv --output=$output_dir/$exp_num/gen_dist_stats.json 

python main.py -m=stats-comparison --original-stats=$output_dir/$exp_num/original_stats.json --generated-stats=$output_dir/$exp_num/gen_normal_stats.json --output=$output_dir/$exp_num/normal_comparison.xlsx
python main.py -m=stats-comparison --original-stats=$output_dir/$exp_num/original_stats.json --generated-stats=$output_dir/$exp_num/gen_dist_stats.json --output=$output_dir/$exp_num/dist_comparison.xlsx

python main.py -m=ks-comparison --ks-original-traffic=$output_dir/$exp_num/original.csv --ks-generated-traffic=$output_dir/$exp_num/gen_normal.csv > ./$output_dir/$exp_num/normal-ks-comparison
python main.py -m=ks-comparison --ks-original-traffic=$output_dir/$exp_num/original.csv --ks-generated-traffic=$output_dir/$exp_num/gen_dist.csv > ./$output_dir/$exp_num/dist-ks-comparison


echo "exp_num=$exp_num" > ./$output_dir/$exp_num/context
echo "max_components=$max_components" > ./$output_dir/$exp_num/context
echo "min_size=$min_size" > ./$output_dir/$exp_num/context
echo "duration=$duration" > ./$output_dir/$exp_num/context
echo "time_interval=$time_interval" > ./$output_dir/$exp_num/context
echo "size_interval=$size_interval" > ./$output_dir/$exp_num/context