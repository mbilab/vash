#!/bin/bash
# example: sh do.annovar.sh ../home/cychen/ [filename w/o .vcf] 1 .

Files=""
Work_folder=$1
VCF_folder="${Work_folder}vcf_files"
Out_folder="${Work_folder}annovar_files"
Merged_folder="${Work_folder}merged"
Temp_folder="${Work_folder}tmp"
Ped_folder="${Work_folder}pedigrees"
Log_foler="log"
Output_name=$2
Cohort_Id=$3
Pedigree_file=$4
PID=$$
shift; shift; shift; shift

mkdir -p ${Out_folder} ${Log_folder} ${Temp_folder}

sed -n '/##/ p' ${Out_folder}/${Output_name}.vcf > ${Temp_folder}/${Output_name}.header
sed '/#CHROM/,$!d' ${Out_folder}/${Output_name}.vcf > ${Temp_folder}/${Output_name}.body.vcf

python3.6 parser.annovar.py ${Temp_folder}/${Output_name} ${Cohort_Id}
