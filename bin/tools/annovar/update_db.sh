#!/bin/bash

set -euo pipefail

mkdir -p humandb

dataset_fromannovar=(refGene knownGene ensGene esp6500siv2_all 1000g2015aug exac03 cg69 kaviar_20150923 avsnp150 dbnsfp33a dbscsnv11 gwava clinvar_20180603 gnomad_genome)

echo "Annovar DB update from Annovar"
for ((i=0; i<${#dataset_fromannovar[@]}; i++)); do
   timeAndDate=`date`
   echo "[$timeAndDate] No.${i} :${dataset_fromannovar[$i]}"
   ./annotate_variation.pl -downdb -webfrom annovar -buildver hg19 ${dataset_fromannovar[$i]} humandb
done

dataset_ucsc=(wgRna tfbsConsSites targetScanS)
for ((i=0; i<${#dataset_ucsc[@]}; i++)); do
  timeAndDate=`date`
  echo "[$timeAndDate] No.${i} : ${dataset_ucsc[$i]}"
  ./annotate_variation.pl -downdb -buildver hg19 ${dataset_ucsc[$i]} humandb
done