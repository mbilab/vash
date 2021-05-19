#!/bin/bash

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

mkdir -p ${Out_folder} ${Log_folder}

python3.6 parser.py ${Out_folder}/${Output_name} 1 ${Cohort_Id}

Files=""
Work_folder=$1
: '

for file in $@; do
	Files="${Files} ${VCF_folder}/${file}.norm"
	bcftools norm -m-both ${VCF_folder}/${file} -Oz -o ${VCF_folder}/${file}.norm &&\
	bcftools index -f ${VCF_folder}/${file}.norm &
done
wait
bcftools merge --merge all ${Files} -Oz -o ${Temp_folder}/merged.${Output_name}.vcf.gz

VCF_Filter="--vcf-filter-in PASS,VQSRTrancheSNP90.00to91.00,VQSRTrancheSNP91.00to92.00,VQSRTrancheSNP92.00to93.00,VQSRTrancheSNP93.00to94.00,VQSRTrancheSNP94.00to95.00,VQSRTrancheSNP95.00to96.00,VQSRTrancheSNP96.00to97.00,VQSRTrancheSNP97.00to98.00,VQSRTrancheSNP98.00to99.00,VQSRTrancheSNP99.00to99.90,VQSRTrancheINDEL90.00to99.90"
AF_Filter="--db-filter exac.eas.sas,1kgeas201305,1kgsas201305,gadexome.eas.sas,gadgenome.eas.sas --rare-allele-freq 1"
Const="--mouse-pheno --zebrafish-pheno --ddd-annot --omim-annot --cosmic-annot --scsnv-annot --rsid --dgv-cnv-annot --nt 4 --buildver hg19"
DB_Gene="--db-gene refgene,gencode,knowngene"
DB_Score="--db-score dbnsfp --mendel-causing-predict best"

if [ $Pedigree_file = "." ]; then
	java -Xmx16g -jar tools/kggseq10/kggseq.jar --no-lib-check --vcf-file ${Temp_folder}/merged.${Output_name}.vcf.gz --o-vcf --o-annovar ${Const} ${DB_Gene} ${VCF_Filter} ${AF_Filter} ${DB_Score} --genotype-filter 3 --out ${Out_folder}/${Output_name} &&\
	gunzip -c ${Out_folder}/${Output_name}.flt.vcf.gz > ${Out_folder}/${Output_name}.vcf &&\
	gunzip -c ${Out_folder}/${Output_name}.flt.txt.gz > ${Out_folder}/${Output_name}.txt &
else
	java -Xmx16g -jar tools/kggseq10/kggseq.jar --no-lib-check --ped-file ${Ped_folder}/${Pedigree_file} --vcf-file ${Temp_folder}/merged.${Output_name}.vcf.gz --o-vcf --o-annovar ${Const} ${DB_Gene} ${VCF_Filter} ${AF_Filter} ${DB_Score} --out ${Out_folder}/${Output_name} &&\
	gunzip -c ${Out_folder}/${Output_name}.flt.vcf.gz > ${Out_folder}/${Output_name}.vcf &&\
	gunzip -c ${Out_folder}/${Output_name}.flt.txt.gz > ${Out_folder}/${Output_name}.txt &
	java -Xmx16g -jar tools/kggseq10/kggseq.jar --no-lib-check --ped-file ${Ped_folder}/${Pedigree_file} --vcf-file ${Temp_folder}/merged.${Output_name}.vcf.gz --o-vcf ${Const} ${DB_Gene} ${VCF_Filter} ${AF_Filter} ${DB_Score} --genotype-filter 1,2,6 --out ${Out_folder}/${Output_name}_Recessive &&\
	gunzip -c ${Out_folder}/${Output_name}_Recessive.flt.vcf.gz > ${Out_folder}/${Output_name}_recessive.vcf &
	java -Xmx16g -jar tools/kggseq10/kggseq.jar --no-lib-check --ped-file ${Ped_folder}/${Pedigree_file} --vcf-file ${Temp_folder}/merged.${Output_name}.vcf.gz --o-vcf ${Const} ${DB_Gene} ${VCF_Filter} ${AF_Filter} ${DB_Score} --genotype-filter 3,4,5,6 --out ${Out_folder}/${Output_name}_Dominant &&\
	gunzip -c ${Out_folder}/${Output_name}_Dominant.flt.vcf.gz > ${Out_folder}/${Output_name}_dominant.vcf &
	java -Xmx16g -jar tools/kggseq10/kggseq.jar --no-lib-check --ped-file ${Ped_folder}/${Pedigree_file} --vcf-file ${Temp_folder}/merged.${Output_name}.vcf.gz --o-vcf ${Const} ${DB_Gene} ${VCF_Filter} ${AF_Filter} ${DB_Score} --double-hit-gene-trio-filter --out ${Out_folder}/${Output_name}_Compound &&\
	gunzip -c ${Out_folder}/${Output_name}_Compound.flt.vcf.gz > ${Out_folder}/${Output_name}_compound.vcf &
	java -Xmx16g -jar tools/kggseq10/kggseq.jar --no-lib-check --ped-file ${Ped_folder}/${Pedigree_file} --vcf-file ${Temp_folder}/merged.${Output_name}.vcf.gz --o-vcf ${Const} ${DB_Gene} ${VCF_Filter} ${AF_Filter} ${DB_Score} --genotype-filter 4,7 --out ${Out_folder}/${Output_name}_Denovo &&\
	gunzip -c ${Out_folder}/${Output_name}_Denovo.flt.vcf.gz > ${Out_folder}/${Output_name}_denovo.vcf &
fi
wait
'

#case `uname` in
	#Linux)
		#sed -i '/#CHROM/,$!d' ${Out_folder}/${Output_name}.vcf
		#for i in ${Out_folder}/${Output_name}_*.vcf; do
			#sed -i '/#CHROM/,$!d' $i
			#cut -f 1,2 < $i > $i.cut
			#mv $i.cut $i
		#done
	#;;
	#Darwin)
		#sed -i '' '/#CHROM/,$!d' ${Out_folder}/${Output_name}.vcf
		#for i in ${Out_folder}/${Output_name}_*.vcf; do
			#sed -i '' '/#CHROM/,$!d' $i
			#cut -f 1,2 < $i > $i.cut
			#mv $i.cut $i
		#done
	#;;
#esac
#paste -d '\t' ${Out_folder}/${Output_name}.vcf ${Out_folder}/${Output_name}.txt > ${Out_folder}/${Output_name}.combined.txt
#mv ${Out_folder}/${Output_name}.combined.txt ${Out_folder}/${Output_name}.vcf


