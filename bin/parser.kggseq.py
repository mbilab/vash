#!/usr/bin/env python


import collections
from conf import DATABASES
import csv
import json
import psycopg2
import sqlite3
from sys import argv

import time
start_time = time.time()

conn = psycopg2.connect(database=DATABASES['default']['NAME'],
                        host=DATABASES['default']['HOST'],
                        password=DATABASES['default']['PASSWORD'],
                        port=DATABASES['default']['PORT'],
                        user=DATABASES['default']['USER'])
cur = conn.cursor()

fields_to_delete = ['INFO', 'FORMAT', 'Chromosome', 'GENCODEFeatures', 'ReferenceAlternativeAllele', 'RefGeneFeatures', 'StartPositionHg19', 'UCSCKnownGeneFeatures']
# fields_to_delete = ['INFO', 'FORMAT', 'Chromosome', 'GENCODEFeatures', 'ReferenceAlternativeAllele', 'RefGeneFeatures', 'StartPositionHg19', 'UCSCKnownGeneFeatures', '#CHROM']
fields_to_rename = [
    ( 'altFreq@exacEAS', 'altFreq_at_exacEAS' ),
    ( 'altFreq@exacSAS', 'altFreq_at_exacSAS' ),
    ( 'altFreq@1kgeas201305', 'altFreq_at_1kgeas201305' ),
    ( 'altFreq@1kgsas201305', 'altFreq_at_1kgsas201305' ),
    ( 'altFreq@gnomad.exomeEAS', 'altFreq_at_gnomad_dot_exomeEAS' ),
    ( 'altFreq@gnomad.exomeSAS', 'altFreq_at_gnomad_dot_exomeSAS' ),
    ( 'altFreq@gnomad.genomeEAS', 'altFreq_at_gnomad_dot_genomeEAS' ),
    ( 'ada_score@dbscSNV', 'ada_score_at_dbscSNV' ),
    ( '#CHROM', 'CHROM' ),
    ( 'DiseaseName(s)MIMid', 'DiseaseName_s_MIMid' ),
    ( 'M-CAP_score', 'M_CAP_score' ),
    ( 'fathmm-MKL_coding_score', 'fathmm_MKL_coding_score' ),
    ( 'Eigen-raw', 'Eigen_raw' ),
    ( 'GERP++_RS', 'GERPpp_RS' ),
    ( 'M-CAP_pred', 'M_CAP_pred' ),
    ( 'fathmm-MKL_coding_pred', 'fathmm_MKL_coding_pred' ),
    ( 'Eigen-phred', 'Eigen_phred' ),
    ( 'BestCombinedTools:OptimalCutoff:TP:TN', 'BestCombinedTools_OptimalCutoff_TP_TN' ),
    ( 'ID', 'variantID' ),
    ( 'POS', 'Start' )]
fields_with_terms = ['DDDPhenotype', 'FILTER', 'MostImportantGeneFeature', 'MostImportantFeatureGene', 'MousePhenotypeIMPC', 'MousePhenotypeMGI', 'ZebrafishPhenotype']
numeric_fields = ['n_variants', 'AllAltHomGtyNum', 'AllHetGtyNum', 'AllRefHomGtyNum',
                  'altFreq_at_1kgeas201305', 'altFreq_at_1kgsas201305', 'altFreq_at_exacEAS', 'altFreq_at_exacSAS',
                  'altFreq_at_gnomad_dot_exomeEAS', 'altFreq_at_gnomad_dot_exomeSAS', 'altFreq_at_gnomad_dot_genomeEAS',
                  'DANN_score', 'fathmm_MKL_coding_score', 'FATHMM_score', 'GenoCanyon_score', 'LRT_score',
                  'MaxDBAltAF', 'M_CAP_score', 'MetaSVM_score', 'MutationTaster_score', 'MutationAssessor_score', 'MutPred_score',
                  'Polyphen2_HDIV_score', 'Polyphen2_HVAR_score', 'PROVEAN_score', 'QUAL', 'SIFT_score', 'VEST3_score']

prefix = argv[1]
ped = argv[2]
cohort_id = argv[3]

# variants
file = f'{prefix}.vcf'
print(f'parsing {file}...')

reader = csv.DictReader(open(file), delimiter='\t')
fields = reader.fieldnames
samples = fields[fields.index('FORMAT') + 1 : fields.index('Chromosome')]

for field in fields_to_rename:
    fields[fields.index(field[0])] = field[1]
fields = list(fields) # otherwise, reader.fieldnames will be changed, too
fields[fields.index('FORMAT') + 1 : fields.index('Chromosome')] = ()
for field in fields_to_delete:
    fields.remove(field)
fields.insert(fields.index('Start')-1, 'POS')
fields.insert(fields.index('FILTER')+1, 'Samples')
fields.insert(fields.index('MostImportantFeatureGene')+1, 'n_variants')
fields.insert(fields.index('MostImportantGeneFeature')+1, 'Genotype')

genotype = {}
n_variants = {}
terms = { k: set() for k in fields_with_terms }
variants = []
for row in reader:
    # fields to add
    row['POS'] = f"{row['CHROM']}:{row['Start']}-{int(row['Start'])+len(row['REF'])-1}"
    row['End'] = int(row['Start']) + len(row['REF']) - 1
    row['Samples'] = {}
    for sample in samples:
        row['Samples'][sample] = row[sample]
        del row[sample]
    row['Samples'] = json.dumps(row['Samples'])

    # fields to delete
    for field in fields_to_delete:
        del row[field]

    # initialize `genotype`
    genotype[f'{row["CHROM"]}:{row["Start"]}'] = {
        'compound': False,
        'denovo': False,
        'dominant': False,
        'recessive': False
    }

    # n_variants
    if row['MostImportantFeatureGene'] in n_variants:
        n_variants[row['MostImportantFeatureGene']] += 1
    else:
        n_variants[row['MostImportantFeatureGene']] = 1

    # terms
    for field in fields_with_terms:
        terms[field].add(row[field])

    variants.append(row)

# genotype
# def parse_genotype(gtype):
    # file = f'{prefix}_{gtype}.vcf'
    # with open(file) as f:
        # print(f'parsing {file}...')
        # reader = csv.DictReader(f, delimiter='\t')
        # for row in reader:
            # genotype[f'{row["#CHROM"]}:{row["POS"]}'][gtype] = True

if '1' == ped:
    numeric_fields += ['AffectedAltHomGtyNum', 'AffectedHetGtyNum', 'AffectedRefHomGtyNum', 'UnaffectedAltHomGtyNum', 'UnaffectedHetGtyNum', 'UnaffectedRefHomGtyNum']
    for field in ['AllAltHomGtyNum', 'AllHetGtyNum', 'AllRefHomGtyNum']:
        fields.insert(fields.index('Genotype')+1, field)
        numeric_fields.remove(field)
    # for v in ['compound', 'denovo', 'dominant', 'recessive']:
        # parse_genotype(v)

print('writing to database...')

sql_fields = '("cohort_id","' + ('","').join(fields) + '")'
sql_values = '(%s' + ',%s' * len(fields) + ')'
query = f'INSERT INTO app_variantmodel {sql_fields} VALUES '.encode()
# print(genotype)

buffer = []
buffer_size = 100000
for row in variants:
    row['Genotype'] = '.'
    for key in genotype[f'{row["CHROM"]}:{row["Start"]}'].keys():
        if genotype[f'{row["CHROM"]}:{row["Start"]}'][key] == True:
            if row['Genotype'] == '.':
                row['Genotype'] = key
            else:
                row['Genotype'] += f', {key}'
    for genotype_number in ['AltHomGtyNum', 'HetGtyNum', 'RefHomGtyNum']:
        row[f'All{genotype_number}'] = str(int(row[f'Affected{genotype_number}']) + int(row[f'Unaffected{genotype_number}']))
    row['n_variants'] = n_variants[row['MostImportantFeatureGene']]
    for field in numeric_fields:
        if '.' == row[field]:
            row[field] = -1
        elif 'N' == row[field]:
            row[field] = -2
    buffer.append((cohort_id, ) + tuple(row[field] for field in fields))
    if len(buffer) >= buffer_size:
        #! prevent values
        values = b','.join(cur.mogrify(sql_values, v) for v in buffer)
        cur.execute(query + values)
        buffer = []

if len(buffer):
    values = b','.join(cur.mogrify(sql_values, v) for v in buffer)
    cur.execute(query + values)

# terms
for field in fields_with_terms:
    terms[field] = list(terms[field])

terms = json.dumps(terms).replace("'", "''")
samples=','.join(sample for sample in samples)

conn.commit()
print("***INSERT***\n--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
cur.execute(f'CLUSTER VERBOSE app_variantmodel USING app_variantmodel_pkey;')
cur.execute(f'UPDATE app_cohortmodel SET n_variants = {len(variants)}, samples = \'{samples}\', pid = 0, terms = \'{terms}\' WHERE ID = {cohort_id};')
conn.commit()
print("***CLUSTER***\n--- %s seconds ---" % (time.time() - start_time))
conn.close()
