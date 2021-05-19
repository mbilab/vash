#!/bin/bash
set -euxo pipefail

# vcftools
# /home/t1000g/2018_Proposal/bin/vcftools/src/perl/vcf-merge vcf/*.gz > tbb.342.merge_vcftools.vcf

# bcftools
#/home/t1000g/2018_Proposal/bin/bcftools-1.6/bcftools merge --file-list firstnas_vcflist.txt --threads 16 --merge all > nas1.192.merge.vcf
#/home/t1000g/2018_Proposal/bin/bcftools-1.6/bcftools merge --file-list files.txt --threads 16 --merge all > tbb.342.merge_bcftools.vcf
#python merge_by_bcftools.py

#python merge_Vcf.py -p ./first_batch/out_merge -b 18 -t 24 -v file_list.all.txt #vcf.list.all.txt
#python merge_Vcf.py -p ./second_batch/out_merge -b 10 -t 24 -v file_list.batch1.txt
#python merge_Vcf.py -p ./third_batch/out_merge -b 10 -t 24 -v file_list.batch2.txt

python merge_Vcf.py -p ./merge_NFH -b 10 -t 24 -v file_list.NFH.txt
python merge_Vcf.py -p ./merge_PKD -b 10 -t 24 -v file_list.PKD.txt
python merge_Vcf.py -p ./merge_TSC -b 10 -t 24 -v file_list.TSC.txt
