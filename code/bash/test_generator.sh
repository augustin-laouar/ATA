max_components=50
min_size=100
duration=605
input='../output/600s.csv'
output_dir='../results/method2'

mkdir $output_dir

echo "max_components=$max_components" > ./$output_dir/context
echo "min_size=$min_size" >> ./$output_dir/context
echo "duration=$duration" >> ./$output_dir/context


python main.py -m=clustering --input=$input --output=$output_dir/original.csv --gmm-max-components=$max_components --gmm-min-cluster-size=$min_size
python main.py -m=stats --input=$output_dir/original.csv --output=$output_dir/original_stats.json 

generators=("uni" "exp" "norm" "gamma")

for ps_generator in "${generators[@]}"
do 
    for ipt_generator in "${generators[@]}"
    do
        exp_dir=$output_dir/$ipt_generator-$ps_generator
        mkdir $exp_dir
        python main.py -m=generate --input=$output_dir/original_stats.json --output=$exp_dir/gen.csv --ipt-generator=$ipt_generator --ps-generator=$ps_generator --duration=$duration
        python main.py -m=stats --input=$exp_dir/gen.csv --output=$exp_dir/gen_stats.json 
        python main.py -m=stats-comparison --original-stats=$output_dir/original_stats.json --generated-stats=$exp_dir/gen_stats.json --output=$exp_dir/stats_comparison.xlsx
        python main.py -m=ks-comparison --ks-original-traffic=$output_dir/original.csv --ks-generated-traffic=$exp_dir/gen.csv > ./$exp_dir/ks-comparison
        python throughput.py --original=$output_dir/original.csv --generated=$exp_dir/gen.csv --interval=3 --output=$exp_dir > ./$exp_dir/throughput
        python packet_second.py --original=$output_dir/original.csv --generated=$exp_dir/gen.csv --interval=3 --output=$exp_dir > ./$exp_dir/packet_second
    done
done