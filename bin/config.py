fields_to_delete = ['INFO']

fields_to_insert = {
    'INFO': 'Samples',
    'INFO': 'Others',
    'Start': 'End',
    'Start': 'POS'
}

fields_to_rename = {
    '#CHROM': 'CHROM',
    'ID': 'variantID',
    'POS': 'Start'
}

fields_with_terms = ['AAChange.knownGene', 'AAChange.refGene', 'ANNOVAR_DATE', 'CLNDISDB', 'CLNDN', 'CLNREVSTAT', 'CLNSIG',
                     'DDDPhenotype', 'ExonicFunc.knownGene', 'ExonicFunc.refGene', 'FATHMM_pred', 'FILTER', 'Func.knownGene',
                     'Func.refGene', 'GeneDetail.knownGene', 'GeneDetail.refGene', 'Gene.knownGene', 'Gene.refGene',
                     'Geno2MP', 'LRT_pred', 'M-CAP_pred', 'MetaLR_pred', 'MetaSVM_pred', 'MostImportantFeatureGene',
                     'MostImportantGeneFeature', 'MousePhenotypeIMPC', 'MousePhenotypeMGI', 'MutationTaster_pred', 'PROVEAN_pred',
                     'Polyphen2_HDIV_pred', 'Polyphen2_HVAR_pred', 'SIFT_pred', 'ZebrafishPhenotype', 'avsnp150', 'culprit',
                     'fathmm-MKL_coding_pred']

infos_to_rename = {
    '1000g2015aug_all': 'N_1000g2015aug_all',
    'AAChange.knownGene': 'AAChange_dot_knownGene',
    'AAChange.refGene': 'AAChange_dot_refGene',
    'EAS.sites.2015_08': 'EAS_dot_sites_dot_2015_08',
    'AFR.sites.2015_08': 'AFR_dot_sites_dot_2015_08',
    'AMR.sites.2015_08': 'AMR_dot_sites_dot_2015_08',
    'EUR.sites.2015_08': 'EUR_dot_sites_dot_2015_08',
    'SAS.sites.2015_08': 'SAS_dot_sites_dot_2015_08',
    'END': 'END_flag',
    'Eigen-PC-raw': 'Eigen_dash_PC_dash_raw',
    'Eigen-raw': 'Eigen_dash_raw',
    'ExonicFunc.knownGene': 'ExonicFunc_dot_knownGene',
    'ExonicFunc.refGene': 'ExonicFunc_dot_refGene',
    'Func.knownGene': 'Func_dot_knownGene',
    'Func.refGene': 'Func_dot_refGene',
    'GERP++_RS': 'GERPpp_RS',
    'GERP++_RS_rankscore': 'GERPpp_RS_rankscore',
    'Gene.knownGene': 'Gene_dot_knownGene',
    'Gene.refGene': 'Gene_dot_refGene',
    'GeneDetail.knownGene': 'GeneDetail_dot_knownGene',
    'GeneDetail.refGene': 'GeneDetail_dot_refGene',
    'M-CAP_pred': 'M_dash_CAP_pred',
    'M-CAP_rankscore': 'M_dash_CAP_rankscore',
    'M-CAP_score': 'M_dash_CAP_score',
    'fathmm-MKL_coding_pred': 'fathmm_dash_MKL_coding_pred',
    'fathmm-MKL_coding_rankscore': 'fathmm_dash_MKL_coding_rankscore',
    'fathmm-MKL_coding_score': 'fathmm_dash_MKL_coding_score'
}

numeric_fields = ['AC', 'AF', 'AF_afr', 'AF_amr', 'AF_asj', 'AF_eas', 'AF_female', 'AF_fin', 'AF_male', 'AF_nfe', 'AF_oth',
                  'AF_popmax', 'AF_raw', 'AF_sas', 'AN', 'AllAltHomGtyNum', 'AllHetGtyNum', 'AllRefHomGtyNum', 'BaseQRankSum',
                  'CADD_phred', 'CADD_raw', 'CADD_raw_rankscore', 'CLNALLELEID', 'ClippingRankSum', 'DANN_rankscore', 'DANN_score',
                  'DANN_score', 'DP', 'EAS.sites.2015_08', 'AFR.sites.2015_08', 'AMR.sites.2015_08', 'EUR.sites.2015_08',
                  'SAS.sites.2015_08', 'END', 'Eigen_coding_or_noncoding', 'Eigen-PC-raw',
                  'Eigen-raw', 'ExAC_AFR', 'ExAC_ALL', 'ExAC_AMR', 'ExAC_EAS', 'ExAC_FIN', 'ExAC_NFE', 'ExAC_OTH', 'ExAC_SAS',
                  'ExcessHet', 'FATHMM_converted_rankscore', 'FATHMM_score', 'FATHMM_score', 'FS', 'GERP++_RS', 'GERP++_RS_rankscore',
                  'GTEx_V6_gene', 'GTEx_V6_tissue', 'GWAVA_region_score', 'GWAVA_tss_score', 'GWAVA_unmatched_score', 'GenoCanyon_score',
                  'GenoCanyon_score', 'GenoCanyon_score_rankscore', 'InbreedingCoeff', 'Interpro_domain', 'Kaviar_AC', 'Kaviar_AF',
                  'Kaviar_AN', 'LRT_converted_rankscore', 'LRT_score', 'LRT_score', 'MLEAC', 'MLEAF', 'MQ', 'MQRankSum', 'M_CAP_score',
                  'M-CAP_rankscore', 'M-CAP_score', 'MaxDBAltAF', 'MetaLR_rankscore', 'MetaLR_score', 'MetaSVM_rankscore',
                  'MetaSVM_score', 'MetaSVM_score', 'MutPred_score', 'MutationAssessor_pred', 'MutationAssessor_score',
                  'MutationAssessor_score', 'MutationAssessor_score_rankscore', 'MutationTaster_converted_rankscore',
                  'MutationTaster_score', 'MutationTaster_score', '1000g2015aug_all', 'PROVEAN_converted_rankscore', 'PROVEAN_score',
                  'PROVEAN_score', 'Polyphen2_HDIV_rankscore', 'Polyphen2_HDIV_score', 'Polyphen2_HDIV_score', 'Polyphen2_HVAR_rankscore',
                  'Polyphen2_HVAR_score', 'Polyphen2_HVAR_score', 'QD', 'QUAL', 'ReadPosRankSum', 'SIFT_converted_rankscore', 'SIFT_score',
                  'SIFT_score', 'SOR', 'SiPhy_29way_logOdds', 'SiPhy_29way_logOdds_rankscore', 'VEST3_rankscore', 'VEST3_score',
                  'VEST3_score', 'VQSLOD', 'altFreq_at_1kgeas201305', 'altFreq_at_1kgsas201305', 'altFreq_at_exacEAS',
                  'altFreq_at_exacSAS', 'altFreq_at_gnomad.exomeEAS', 'altFreq_at_gnomad.exomeSAS',
                  'altFreq_at_gnomad.genomeEAS', 'cg69', 'controls_AF_popmax', 'dbscSNV_ADA_SCORE', 'dbscSNV_RF_SCORE',
                  'esp6500siv2_all', 'fathmm_MKL_coding_score', 'fathmm-MKL_coding_rankscore', 'fathmm-MKL_coding_score',
                  'gnomAD_exome_AFR', 'gnomAD_exome_ALL', 'gnomAD_exome_AMR', 'gnomAD_exome_ASJ', 'gnomAD_exome_EAS', 'gnomAD_exome_FIN',
                  'gnomAD_exome_NFE', 'gnomAD_exome_OTH', 'gnomAD_exome_SAS', 'gnomAD_genome_AFR', 'gnomAD_genome_ALL', 'gnomAD_genome_AMR',
                  'gnomAD_genome_ASJ', 'gnomAD_genome_EAS', 'gnomAD_genome_FIN', 'gnomAD_genome_NFE', 'gnomAD_genome_OTH',
                  'gnomAD_2_exome_AF', 'gnomAD_2_exome_AF_afr', 'gnomAD_2_exome_AF_amr', 'gnomAD_2_exome_AF_asj', 'gnomAD_2_exome_AF_eas',
                  'gnomAD_2_exome_AF_female', 'gnomAD_2_exome_AF_fin', 'gnomAD_2_exome_AF_male', 'gnomAD_2_exome_AF_nfe', 'gnomAD_2_exome_AF_oth',
                  'gnomAD_2_exome_AF_popmax', 'gnomAD_2_exome_AF_raw', 'gnomAD_2_exome_AF_sas', 'gnomAD_2_exome_controls_AF_popmax', 'gnomAD_2_exome_non_cancer_AF_popmax',
                  'gnomAD_2_exome_non_neuro_AF_popmax', 'gnomAD_2_exome_non_topmed_AF_popmax', 'gnomAD_2_genome_AF', 'gnomAD_2_genome_AF_afr', 'gnomAD_2_genome_AF_amr',
                  'gnomAD_2_genome_AF_asj', 'gnomAD_2_genome_AF_eas', 'gnomAD_2_genome_AF_female', 'gnomAD_2_genome_AF_fin', 'gnomAD_2_genome_AF_male',
                  'gnomAD_2_genome_AF_nfe', 'gnomAD_2_genome_AF_oth', 'gnomAD_2_genome_AF_popmax', 'gnomAD_2_genome_AF_raw', 'gnomAD_2_genome_AF_sas',
                  'gnomAD_2_genome_controls_AF_popmax', 'gnomAD_2_genome_non_cancer_AF_popmax', 'gnomAD_2_genome_non_neuro_AF_popmax', 'gnomAD_2_genome_non_topmed_AF_popmax',
                  'integrated_confidence_value', 'integrated_fitCons_score', 'integrated_fitCons_score_rankscore', 'n_variants',
                  'non_cancer_AF_popmax', 'non_neuro_AF_popmax', 'non_topmed_AF_popmax', 'phastCons100way_vertebrate',
                  'phastCons100way_vertebrate_rankscore', 'phastCons20way_mammalian', 'phastCons20way_mammalian_rankscore',
                  'phyloP100way_vertebrate', 'phyloP100way_vertebrate_rankscore', 'phyloP20way_mammalian', 'phyloP20way_mammalian_rankscore',
                  'targetScanS', 'tbbaf', 'tbbaf_all', 'tbbaf_illumina', 'tbbaf_proton', 'tfbsConsSites', 'wgRna']

unicode_table = {
    '\\x3b': ';',
    '\\x3d': '=',
    '\\': '',
    '\'': '\\\'',
    '\u0000': '\\\\0',
    '\"': '\\\"',
    '\b': '\\\b',
    '\n': '\\\n',
    '\r': '\\\r',
    '\t': '\\\t',
    '\u001A': '\\\z',
}
