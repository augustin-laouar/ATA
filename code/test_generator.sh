max_components=50
min_size=100
duration=1200
input='../output/180s/app_traffic_180s.csv'
output_dir='../results/method'


python main.py -m=clustering --input=$input --output=$output_dir/original.csv --gmm-max-components=$max_components --gmm-min-cluster-size=$min_size
python main.py -m=stats --input=$output_dir/original.csv --output=$output_dir/original_stats.json 
#Save stats débit : intervalle de mesure = 1s. Débit min/max/moyen/ecarttype/var




#Nom des experiences : IPT gen / PS gen
#EXP 1 : Uni / Uni 
exp_dir=$output_dir/uni-uni
mkdir $exp_dir
python main.py -m=generate --input=$output_dir/original_stats.json --output=$exp_dir/gen.csv --ipt-generator=uni --ps-generator=uni --duration=$duration
python main.py -m=stats --input=$exp_dir/gen_normal.csv --output=$exp_dir/gen_stats.json 
python main.py -m=stats-comparison --original-stats=$output_dir/original_stats.json --generated-stats=$exp_dir/gen_stats.json --output=$exp_dir/stats_comparison.xlsx
python main.py -m=ks-comparison --ks-original-traffic=$output_dir/original.csv --ks-generated-traffic=$exp_dir/gen_normal.csv > ./$exp_dir/ks-comparison
#Save stats débit : intervalle de mesure = 1s. Débit min/max/moyen/ecarttype/var
#Save fig débit superposé avec débit originale
#Save auto corrélation superposé avec autocorrélation originale

#EXP 2 : Uni / Norm
exp_dir=$output_dir/uni-norm
mkdir $exp_dir
python main.py -m=generate --input=$output_dir/original_stats.json --output=$exp_dir/gen.csv --ipt-generator=uni --ps-generator=norm --duration=$duration

#EXP 3 : Uni / Exp
exp_dir=$output_dir/uni-exp
mkdir $exp_dir

#EXP 4 : Norm / Uni
exp_dir=output_dir/norm-uni
mkdir $exp_dir

#EXP 5 : Norm / Norm
exp_dir=$output_dir/norm-norm
mkdir $exp_dir

#EXP 6 : Norm / Exp
exp_dir=$output_dir/norm-exp
mkdir $exp_dir

#EXP 7 : Exp / Uni
exp_dir=$output_dir/exp-uni
mkdir $exp_dir

#EXP 8 : Exp / Norm
exp_dir=$output_dir/exp-norm
mkdir $exp_dir

#EXP 9 : Exp / Exp
exp_dir=$output_dir/exp-exp
mkdir $exp_dir



echo "exp_num=$exp_num" > ./$output_dir/context
echo "max_components=$max_components" > ./$output_dir/context
echo "min_size=$min_size" > ./$output_dir/context
echo "duration=$duration" > ./$output_dir/context