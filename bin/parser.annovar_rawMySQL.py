#!/usr/bin/env python
# standard import
import csv
import gzip
import json
import os
import sys
import time
from base64 import b64encode
from hashlib import md5

# django import
import django
import pymysql.cursors
from django.forms.models import model_to_dict

from conf import DATABASES
# local import
from config import (fields_to_rename, fields_with_terms, infos_to_rename,
                    numeric_fields, unicode_table)

sys.path.append('../')


BUFFER_SIZE = 1000


def cohort_update(n_variants, terms, samples, others, available):
    terms = json.dumps(terms).replace("'", "''")
    samples = ','.join(sample for sample in samples)
    others = ','.join(other for other in others)
    for k, v in infos_to_rename.items():
        if v in available:
            available[available.index(v)] = k
    available = ','.join(v for v in available)
    CohortModel.objects.filter(id=cohort_id).update(
        queries='[]', fullyMatches='[]', n_variants=n_variants)
    print("Update: queries, n_variants")
    CohortModel.objects.filter(id=cohort_id).update(samples=samples)
    print("Update: samples")
    CohortModel.objects.filter(id=cohort_id).update(others=others)
    print("Update: others")
    CohortModel.objects.filter(id=cohort_id).update(available=available)
    print("Update: available")
    CohortModel.objects.filter(id=cohort_id).update(terms=terms)
    print("Update: terms")
    print(terms)
    CohortModel.objects.filter(id=cohort_id).update(pid='0')
    print("Update: pid")


def infos_split(infos):
    info = {}
    infos = infos.split(';')
    for row in infos:
        if '=' in row:
            _row = row.split('=')
            info[_row[0]] = _row[1]

    return info


def parse_header(f_header, f_body):
    info = {}
    for row in f_header.readlines():
        if row.startswith('##'):
            next(f_body)
        else:
            return info
        if row.startswith('##INFO'):
            # exclude <>, if text of description include \"
            row = row[8:-1].split('"')
            r = row[0].split(',')   # split with ,
            _info = {}
            for i in range(1, len(r)-1):
                _row = r[i].split('=')  # get k and v exclude description
                _info[_row[0]] = _row[1]    # k: v
            # if description include "
            _info[r[-1].split('=')[0]
                  ] = row[1] if len(row) > 1 else r[-1].split('=')[1]
            info[r[0].split('=')[1]] = _info

    return {}


def parse_row(cohort_id, infos, reader, samples, cursor):
    counter = 0
    full_terms = {k: set() for k in fields_with_terms}
    full_terms['ID'] = set()
    insert_counter = 0
    others = set()
    terms = {}
    terms_oversize = []
    variants = []

    sql = ''
    fields = []

    process_total_time = 0.0
    insert_total_time = 0.0

    for row in reader:
        process_time = time.time()
        row['POS'] = f"{row['CHROM']}:{row['Start']}-{int(row['Start'])+len(row['REF'])-1}"
        row['End'] = int(row['Start']) + len(row['REF']) - 1
        row['cohort_id'] = cohort_id

        # samples
        row['Samples'] = {}
        if args.all_samples:
            for sample in samples:
                row['Samples'][sample] = row[sample]
                del row[sample]
        else:
            for sample in samples:
                del row[sample]
        row['Samples'] = json.dumps(row['Samples']).replace('"', '\\"')

        # INFO
        row['INFO'] = infos_split(row['INFO'])
        row['Others'] = {}

        # add missing infos
        if infos - row['INFO'].keys():
            for k in list(infos - row['INFO'].keys()):
                row['INFO'][k] = '.'

        # process every key in INFO
        info_keys = list(row['INFO'].keys())
        infos_to_rename_k = list(infos_to_rename.keys())
        for k in info_keys:
            # rename col and value
            for ori, after in unicode_table.items():
                row['INFO'][k] = row['INFO'][k].replace(ori, after)
            # transfer from INFO to row
            # numeric field change dot to 1e^-12
            if k in numeric_fields:
                _k = k
                if k in infos_to_rename_k:
                    _k = infos_to_rename[k]
                if row['INFO'][k] == '.':
                    row[_k] = '0.000000000001'
                elif row['INFO'][k] == 'nan':
                    row[_k] = '0.000000000002'
                else:
                    row[_k] = row['INFO'][k]
            elif k in fields_with_terms:
                if k in infos_to_rename_k:
                    row[infos_to_rename[k]] = row['INFO'][k]
                else:
                    row[k] = row['INFO'][k]
            else:
                row['Others'][k] = row['INFO'][k]
                others.add(k)

        # terms
        terms_available = [term for term in fields_with_terms
                           if term not in terms_oversize]
        for field in terms_available:
            if field in info_keys:
                if len(full_terms[field]) > BUFFER_SIZE:
                    full_terms[field] = ['TooMuch']
                    terms_oversize.append(field)
                else:
                    for _term in row['INFO'][field].split(','):
                        full_terms[field].add(_term)
                    # full_terms[field].add(_term for _term in row['INFO'][field].split(','))
        if not len(full_terms['ID']) > BUFFER_SIZE and full_terms['ID'] != ['TooMuch']:
            full_terms['ID'].add(row['variantID'])
        else:
            full_terms['ID'] = ['TooMuch']

        # ready to dump
        row['Others'] = json.dumps(row['Others']).replace('"', '\\"')
        del row['INFO']
        if counter == 0:
            fields = list(sorted(row.keys()))
            sql = 'INSERT INTO app_variantmodel(' + \
                ','.join(k for k in fields) + ') VALUES '
            values = '(' + ','.join(f"'{row[v]}'" if type(row[v])
                                    == str else f'{row[v]}' for v in fields) + ')'
            sql += values
        else:
            values = ',(' + ','.join(f"'{row[v]}'" if type(row[v])
                                     == str else f'{row[v]}' for v in fields) + ')'
            sql += values
        counter += 1
        process_total_time += time.time() - process_time
        if counter >= BUFFER_SIZE:
            insert_time = time.time()
            cursor.execute(sql)
            insert_counter += 1
            variants = []
            counter = 0
            print(f'insert: {insert_counter}')
            insert_total_time += time.time() - insert_time

    variants_length = (insert_counter*BUFFER_SIZE) + counter
    if counter > 0:
        insert_time = time.time()
        cursor.execute(sql)
        insert_counter += 1
        print(f'insert(left): {insert_counter}')
        insert_total_time += time.time() - insert_time

    insert_time = time.time()
    connection.commit()
    insert_total_time += time.time() - insert_time

    process_time = time.time()
    for k in full_terms.keys():
        if len(full_terms[k]) > 0:
            terms[k] = full_terms[k]
    process_total_time += time.time() - process_time

    print(f'len(variants): {variants_length}')
    print(f'** PROCESS TIME = {round(process_total_time, 6)}')
    print(f'** INSERT TIME = {round(insert_total_time, 6)}')

    return terms, others, variants_length


def add_IDhash(cohort_id):
    variants = VariantModel.objects.filter(cohort_id=cohort_id)
    for variant in variants:
        for id in variant.variantID.split(';'):
            h = md5(str.encode(id))
            hashcode = b64encode(h.digest()).decode('utf-8')[:5]

            id_hash_code = IDHashCodeModel(
                id=None, hashcode=hashcode, variant=variant)
            id_hash_code.save()


if '__main__' == __name__:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
    django.setup()
    from app.models import *
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("filename", help="absolute path of file and filename")
    parser.add_argument("cohort_id", help="cohort id in Cohorts DB")
    parser.add_argument('--all-samples', dest='all_samples',
                        action='store_true')
    parser.add_argument('--no-all-samples', dest='all_samples',
                        action='store_false')
    parser.set_defaults(detail=True)
    args = parser.parse_args()

    file = f'{args.filename}'
    if file.endswith('.vcf'):
        f_header = open(file)
        f_body = open(file)
    elif file.endswith('.vcf.gz'):
        f_header = gzip.open(file, 'rt', encoding='utf-8')
        f_body = gzip.open(file, 'rt', encoding='utf-8')
    else:
        print('error filetype')
        exit()
    cohort_id = args.cohort_id

    whole_time = time.time()
    start_time = time.time()
    info_dict = parse_header(f_header, f_body)
    f_header.close()
    infos = set()
    for k in info_dict.keys():
        if info_dict[k]['Type'] != 'Flag':
            infos.add(k)
    print(
        f"*** parse header *** --- {round(time.time()-start_time, 6)} seconds ---")

    # variants
    print(f'parsing {file}...')
    reader = csv.DictReader(f_body, delimiter='\t')

    # get samples, infos set and others set
    start_time = time.time()
    fields = reader.fieldnames
    for field in fields_to_rename.keys():
        fields[fields.index(field)] = fields_to_rename[field]
    samples = [sample for sample in fields[9:]]

    start_time = time.time()
    # connection
    connection = pymysql.connect(
        host=DATABASES['default']['HOST'],
        port=int(DATABASES['default']['PORT']),
        user=DATABASES['default']['USER'],
        password=DATABASES['default']['PASSWORD'],
        db=DATABASES['default']['NAME'])
    cursor = connection.cursor()

    terms, others, variants_length = parse_row(
        cohort_id, infos, reader, samples, cursor)
    print(
        f"*** parse and insert *** --- {round(time.time()-start_time, 6)} seconds ---")

    start_time = time.time()
    for key in terms.keys():
        terms[key] = ','.join(term for term in terms[key])
    if not args.all_samples:
        samples = []
    add_IDhash(cohort_id)
    cohort_update(variants_length, terms, samples,
                  sorted(others), sorted(infos))
    print(f"*** UPDATE *** --- {round(time.time()-start_time, 6)} seconds ---")
    print(f"WHOLE TIME = {round(time.time()-whole_time, 6)}")
