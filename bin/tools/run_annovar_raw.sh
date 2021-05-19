#!/bin/bash

set -euo pipefail

ANNOVAR="/home/t1000g/2018_Proposal/bin/annovar_v201707"
DB="/home/t1000g/2018_Proposal/bin/annovar_v201707/humandb/"


VCF_folder="/home/t1000g/for_NCKU_vcfviewer"
Out_folder="/home/t1000g/for_NCKU_vcfviewer/annovar"

mkdir -p avinputs avoutputs

# Prepare ANNOVAR input 1000g
for i in ${VCF_folder}/*.vqsr_SNP_INDEL.hc.recaled.vcf.gz; do
    prefix=`basename $i .vqsr_SNP_INDEL.hc.recaled.vcf.gz`

    ${ANNOVAR}/convert2annovar.pl -format vcf4 $i -outfile ${Out_folder}/avinputs/${prefix}.avinput # --includeinfo -withzyg
    ${ANNOVAR}/table_annovar.pl ${Out_folder}/avinputs/${prefix}.avinput ${DB} --outfile ${Out_folder}/avoutputs/${prefix} -buildver hg19 -remove -protocol refGene,knownGene,clinvar_20170130,esp6500siv2_all,1000g2015aug_all,EAS.sites.2015_08,exac03,cg69,kaviar_20150923,avsnp147,avsnp150,tbbaf,dbnsfp33a,dbscsnv11,gwava,tfbsConsSites,wgRna,targetScanS -operation g,g,f,f,f,f,f,f,f,f,f,f,f,f,f,r,r,r -otherinfo -nastring . --thread 36
done

# Convert annovar input
# real    113m32.847s
# user    116m20.771s
# sys     1m32.851s

# Run annovar
# real    1276m55.015s
# user    13669m38.764s
# sys     288m2.381s
