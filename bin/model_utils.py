# standard import
import csv
import gzip
import itertools
import json
import logging
import math
import os
import re
import sys
import time
from base64 import b64encode
from hashlib import md5
from itertools import islice

# django import
import django
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.models import Q
from django.db.utils import InternalError, OperationalError
from django.forms.models import model_to_dict

# local import
from app.models import (AAChange_dot_knownGeneTerms, AAChange_dot_refGeneTerms,
                        ANNOVAR_DATETerms, CLNDISDBTerms, CLNDNTerms,
                        CLNREVSTATTerms, CLNSIGTerms, CohortModel,
                        ExonicFunc_dot_knownGeneTerms,
                        ExonicFunc_dot_refGeneTerms, FATHMM_predTerms,
                        Func_dot_knownGeneTerms, Func_dot_refGeneTerms,
                        Gene_dot_knownGeneTerms, Gene_dot_refGeneTerms,
                        GeneDetail_dot_knownGeneTerms,
                        GeneDetail_dot_refGeneTerms, Geno2MPTerms,
                        HashCodeModel, LRT_predTerms, M_dash_CAP_predTerms,
                        MetaLR_predTerms, MetaSVM_predTerms,
                        MutationTaster_predTerms, Polyphen2_HDIV_predTerms,
                        Polyphen2_HVAR_predTerms, PROVEAN_predTerms,
                        SIFT_predTerms, VariantModel, avsnp150Terms,
                        culpritTerms, fathmm_dash_MKL_coding_predTerms,
                        variantIDTerms)

# local import
from .config import (fields_to_rename, fields_with_terms, infos_to_rename,
                     numeric_fields, unicode_table)

BUFFER_SIZE = 2000
HASHCODE_BUFFER_SIZE = 5000
logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s\t%(message)s',
    datefmt='%Y-%m-%d %H:%M',
)
logger = logging.getLogger(__name__)


def _Qs(cohort, queries, match_counts={}):
    qs = Q()

    id_cached = False
    for query in queries:
        key = list(query.keys())[0]
        if key == 'id__gte':
            id_cached = True

    for query in queries:
        key = list(query.keys())[0]
        if "variantID" in key:
            value = query[key]
            key = key.replace('__match', '')
            match = {}
            match[key] = value
            qs &= Q_hashcodes(match)
        elif "__match" in key:
            value = query[key]
            key = key.replace('__match', '')
            if is_indexes(key, value):
                logger.info('is_indexes')
                match = {}
                match[key] = value
                q_match, match_counts = Q_match(
                    cohort, match, id_cached, match_counts)
                qs &= q_match
            else:
                for v in value:
                    qs &= Q(**{f'{key}__icontains': v})
        elif "position" in key:
            qs &= Q_position(query)
        else:
            qs &= Q(**query)
    logger.info(qs)
    return qs, match_counts


def Q_hashcodes(match):
    qs = Q()
    # match = {'variantID': ['rs123', 'rs234']}
    keys = match.keys()
    if len(keys) > 1:
        logger.error('WRONG Match format: key_len > 1')

    key = next(iter(keys))
    values = [v.lower() for v in match[key]]

    hs = [md5(str.encode(value)) for value in values]
    hashcodes = [b64encode(h.digest()) for h in hs]
    hashcodes = [hashcode.decode('utf-8') for hashcode in hashcodes]

    query_key = f'hashcodemodel__{key}'
    for hashcode in hashcodes:
        qs |= Q(**{query_key: hashcode})

    return qs


def Q_match(cohort, match, id_cached, match_counts):
    qs = Q()
    # match = {'CLNSIG': ['rs123', 'rs234']}
    keys = match.keys()
    if len(keys) > 1:
        logger.error('WRONG Match format: key_len > 1')

    key = next(iter(keys))
    values = [v.lower() for v in match[key]]

    hs = [md5(str.encode(value)) for value in values]
    hashcodes = [b64encode(h.digest()) for h in hs]
    hashcodes = [hashcode.decode('utf-8') for hashcode in hashcodes]

    start_time = time.time()
    try:
        if ''.join(hashcodes) in match_counts:
            match_count = match_counts[''.join(hashcodes)]
        else:
            query_key = f'{key}__in'
            match_count = HashCodeModel.objects.filter(
                **{query_key: hashcodes}
            ).count()
            match_counts[''.join(hashcodes)] = match_count
    except (InternalError, OperationalError):
        match_count = None

    logger.info(
        f"*** count matches *** --- {round(time.time()-start_time, 6)} seconds ,  {match_count}---")

    # It will be super  slow, when no string is contained
    if match_count and match_count < HASHCODE_BUFFER_SIZE and match_count != 0:
        query_key = f'hashcodemodel__{key}'
        for hashcode in hashcodes:
            qs |= Q(**{query_key: hashcode})
        if not id_cached:
            try:
                query_key = f'hashcodemodel__{key}__in'
                first_match_ids = [cohort.variantmodel_set.filter(
                    **{query_key: [hashcode]}).first().id for hashcode in hashcodes]
                first_match_id = min(first_match_ids)
                qs &= Q(**{'id__gte': first_match_id})
            except (django.core.exceptions.FieldError, AttributeError):
                first_match_id = None
    else:
        query_key = f'{key}__icontains'
        for value in values:
            qs |= Q(**{query_key: value})

    return qs, match_counts


def Q_position(query):

    qs = Q()

    key = list(query.keys())[0]
    positions = query[key]
    for position in positions:
        chrom, variant_range = position.split(':')
        variant_range = variant_range.split('-')

        sqs = Q()
        qs &= Q(**{})
        if len(variant_range) == 1:
            qs &= Q(**{'CHROM': chrom, 'Start': variant_range[0]})
        if len(variant_range) == 2:
            qs &= Q(**{
                'CHROM': chrom,
                'Start__gte': variant_range[0],
                'Start__lte': variant_range[1]
            })
        qs |= sqs
    return qs


def is_indexes(key, value):
    # key: Gene_dot_refGene
    # value: ['BRCA1', 'BRCA2']
    if not key in [
        'Func_dot_refGene',
        'Gene_dot_refGene',
        'ExonicFunc_dot_refGene',
        'Func_dot_knownGene',
        'Gene_dot_knownGene',
        'ExonicFunc_dot_knownGene',
        'CLNDN',
        'CLNSIG',
        'Polyphen2_HDIV_pred',
        'Polyphen2_HVAR_pred',
        'SIFT_pred'
    ]:
        return False

    term_model = eval(f'{key}Terms')
    if term_model.objects.filter(term__in=value):
        return True
    else:
        False


def has_only_terms(cohort_id, queries):
    # queries = [{'Gene_dot_refGene__match': ['BRCA1']}]
    for query in queries:
        key = list(query.keys())[0]
        if "__match" in key:
            keywords = query[key]
            key = key.replace('__match', '')
            try:
                term_model = eval(f'{key}Terms')
                for keyword in keywords:
                    qs = term_model.objects.filter(
                        cohort_id=cohort_id, term=keyword)
                    if not qs:
                        return False
            # if no correspond term_model
            except NameError:
                return False
        else:
            return False

    return True


def check_keyword_is_contained_in_term_model(cohort_id, queries):
    # queries = [{'Gene_dot_refGene__match': ['BRCA1']}]
    valid = True
    for query in queries:
        key = list(query.keys())[0]
        if "__match" in key:
            keywords = query[key]
            key = key.replace('__match', '')
            if key in ['variantID', 'AAChange_dot_refGene', 'AAChange_dot_knownGene', 'GeneDetail_dot_refGene', 'Gene_dot_knownGene']:
                continue
            try:
                valid_query = False
                term_model = eval(f'{key}Terms')
                for keyword in keywords:
                    qs = term_model.objects.filter(
                        cohort_id=cohort_id, term__icontains=keyword)
                    if qs:
                        valid_query = True
                valid = valid if valid_query else False
            # if no correspond term_model
            except NameError:
                continue
    logger.info(f'keyword is contained in term model: {valid}')

    return valid


def get_vcf_head_tail(file):
    head = file.tell()
    file.seek(0, 2)
    tail = file.tell()
    return head, tail


def insert_HashCodeModel(cohort_id, cursor, connection):
    field_names = [field.name for field in HashCodeModel._meta.fields]
    field_names.remove('id')
    field_names.remove('variant')

    variants = VariantModel.objects.filter(
        cohort_id=cohort_id)
    batch = []
    for variant in variants:
        variant_hashcode = {}
        # {
        # 'variant_id': ['asdasd']
        # 'variantID': ['asdass', 'asdasd'...]
        # }
        for field_name in field_names:
            values = re.split(';|\||,', str(getattr(variant, field_name)))
            hs = [md5(str.encode(value)) for value in values]
            variant_hashcode[field_name] = [
                b64encode(h.digest()).decode('utf-8')
                for h in hs
            ]

        max_len = max(*[len(v) for v in variant_hashcode.values()])
        variant_hashcode['variant_id'] = [str(variant.id)]*max_len
        for key in variant_hashcode.keys():
            hashcodes_len = len(variant_hashcode[key])
            for i in range(max_len-hashcodes_len):
                variant_hashcode[key].append('')

        for i in range(max_len):
            row = tuple([variant_hashcode[key][i]
                         for key in variant_hashcode.keys()])
            batch.append(str(row))

        if len(batch) < BUFFER_SIZE:
            continue

        cursor.execute(
            f"INSERT INTO `app_hashcodemodel` ({','.join(variant_hashcode.keys())})\
            VALUES {','.join(batch)};"
        )
        connection.commit()
        batch = []

    if batch:
        cursor.execute(
            f"INSERT INTO `app_hashcodemodel` ({','.join(variant_hashcode.keys())})\
            VALUES {','.join(batch)};"
        )
        connection.commit()


def create_sub_variants(id, id_ori, queries, admin_group):
    cohort = CohortModel.objects.get(pk=id)
    cohort_ori = CohortModel.objects.get(pk=id_ori)

    qs = _Qs(cohort_ori, queries)

    variants = cohort_ori.variantmodel_set.filter(qs)

    last_insert_id = VariantModel.objects.latest('id').id

    counter = 0
    sub_hashcodes = []
    sub_variants = []
    terms = {k: set() for k in fields_with_terms}
    terms['variantID'] = set()

    for variant in variants:
        hashcodes = variant.hashcodemodel_set.all()
        variant.pk = None
        variant.cohort_id = id
        sub_variants.append(variant)
        counter += 1

        # terms
        empty_fields = []
        for field in terms.keys():
            term = None
            if field in infos_to_rename.keys():
                term = variant.__dict__[infos_to_rename[field]]
            else:
                term = variant.__dict__[field]
            if not term:
                empty_fields.append(field)
            else:
                terms[field].add(term)

        for field in empty_fields:
            del terms[field]

        for hashcode in hashcodes:
            hashcode.id = None
            hashcode.variant_id = last_insert_id + counter
            sub_hashcodes.append(hashcode)

        if counter % 1000 == 0:
            VariantModel.objects.bulk_create(sub_variants)
            HashCodeModel.objects.bulk_create(sub_hashcodes)
            CohortModel.objects.filter(id=id).update(
                created_percentage=counter/cohort.n_variants*100
            )
            sub_variants = []
            sub_hashcodes = []

    if sub_variants:
        VariantModel.objects.bulk_create(sub_variants)
        HashCodeModel.objects.bulk_create(sub_hashcodes)
        CohortModel.objects.filter(id=id).update(
            created_percentage=counter/cohort.n_variants*100
        )

    logger.debug('sub variant insert complete')

    for field in terms.keys():
        # if field == 'ID':
        #     continue
        # if field == 'avsnp150':
        #     continue
        # if field == 'ID':
        #     objs = [eval(f'variantIDTerms(cohort_id={id}, term="{term}")')
        #             for term in terms[field]]
        if field == 'FILTER':  # FILTER isn't a field in INFO
            continue

        if field in infos_to_rename.keys():
            objs = [eval(f'{infos_to_rename[field]}Terms(cohort_id={id}, term="{term}")')
                    for term in terms[field]]
        else:
            objs = [eval(f'{field}Terms(cohort_id={id}, term="{term}")')
                    for term in terms[field]]

        for i in range(int(math.ceil(len(objs)/BUFFER_SIZE))):
            batch = list(islice(objs, BUFFER_SIZE*i, BUFFER_SIZE*(i+1)))
            if field == 'ID':
                model_objects = variantIDTerms.objects
            elif field in infos_to_rename.keys():
                model_objects = eval(f'{infos_to_rename[field]}Terms.objects')
            else:
                model_objects = eval(f'{field}Terms.objects')
            model_objects.bulk_create(batch, BUFFER_SIZE)
    cohort.pid = 0
    cohort.admin_group = admin_group

    cohort.save()
    logger.info('cohort update complete')


def cohort_update(cohort_id, n_variants, terms, samples, others, available):
    samples = ','.join(sample for sample in samples)
    others = ','.join(other for other in others)
    for k, v in infos_to_rename.items():
        if v in available:
            available[available.index(v)] = k
    available = ','.join(v for v in available)
    CohortModel.objects.filter(id=cohort_id).update(
        queries='[]', n_variants=n_variants)
    CohortModel.objects.filter(id=cohort_id).update(samples=samples)
    logger.debug("Update: samples")
    CohortModel.objects.filter(id=cohort_id).update(others=others)
    logger.debug("Update: others")
    CohortModel.objects.filter(id=cohort_id).update(available=available)
    logger.debug("Update: available")
    cohort = CohortModel.objects.get(id=cohort_id)
    for field in terms.keys():
        # if field == 'ID':
        #     continue
        # if field == 'avsnp150':
        #     continue
        if field == 'ID':
            objs = [eval(f'variantIDTerms(cohort_id={cohort_id}, term="{term}")')
                    for term in terms[field].split(',')]
        elif field in infos_to_rename.keys():
            objs = [eval(f'{infos_to_rename[field]}Terms(cohort_id={cohort_id}, term="{term}")')
                    for term in terms[field].split(',')]
        else:
            objs = [eval(f'{field}Terms(cohort_id={cohort_id}, term="{term}")')
                    for term in terms[field].split(',')]

        for i in range(int(math.ceil(len(objs)/BUFFER_SIZE))):
            batch = list(islice(objs, BUFFER_SIZE*i, BUFFER_SIZE*(i+1)))
            if field == 'ID':
                model_objects = variantIDTerms.objects
            elif field in infos_to_rename.keys():
                model_objects = eval(f'{infos_to_rename[field]}Terms.objects')
            else:
                model_objects = eval(f'{field}Terms.objects')
            model_objects.bulk_create(batch, BUFFER_SIZE)

    logger.debug("Update: terms")
    CohortModel.objects.filter(id=cohort_id).update(pid='0')
    logger.debug("Update: pid")


def parse_header(f_header, f_body):
    info = {}
    row = f_header.readline()
    while row:
        if row.startswith('##'):
            f_body.readline()
        else:
            return info
        if row.startswith('##INFO'):
            # exclude <>, if text of description include \"
            row = row[8: -1].split('"')
            r = row[0].split(',')   # split with ,
            _info = {}
            for i in range(1, len(r)-1):
                _row = r[i].split('=')  # get k and v exclude description
                _info[_row[0]] = _row[1]    # k: v
            # if description include "
            _info[r[-1].split('=')[0]
                  ] = row[1] if len(row) > 1 else r[-1].split('=')[1]
            info[r[0].split('=')[1]] = _info
        row = f_header.readline()

    return {}


def build_hash_info_dict(hash_keys, row):
    hash_info_dict = {}
    for key in hash_keys:
        hash_info_dict[key] = re.split(';|\||,', row.get(key, '').lower())

    max_hash_info_len = max(*[len(v) for v in hash_info_dict.values()])

    for key in hash_info_dict.keys():
        info_len = len(hash_info_dict[key])
        for i in range(max_hash_info_len-info_len):
            hash_info_dict[key].append('')

    return hash_info_dict, max_hash_info_len


def build_full_terms(full_terms, info_keys, terms_oversize, row
                     ):
    terms_available = [term for term in fields_with_terms
                       if term not in terms_oversize]
    for field in terms_available:
        if field in info_keys:
            for _term in re.split(',|\||;', row['INFO'][field]):
                full_terms[field].add(_term)
    full_terms['ID'].add(row['variantID'])

    return full_terms, terms_oversize


def build_info(infos, info_keys, info_keys_to_rename):
    info = {}
    infos = infos.split(';')
    for row in infos:
        if '=' in row:
            _row = row.split('=')
            info[_row[0]] = _row[1]

    missing_info_keys = list(info_keys - info.keys())
    for key in missing_info_keys:
        info[key] = '.'

    info['variantID'] = info['avsnp150']
    try:
        info['AF'] = str(int(info['AC']) / int(info['AN']))
    except ValueError:
        info['AF'] = '.'

    return info


def build_samples(all_samples, samples, row):
    if not all_samples:
        return json.dumps({})

    tmp = {}
    for sample in samples:
        tmp[sample] = row[sample]

    return json.dumps(tmp).replace('"', '\\"')


def insert_hash_batch(last_insert_id, cursor, hash_batch, hash_keys, connection):
    logger.debug(hash_batch[-1])

    for hash_row in hash_batch:
        hash_row[0] += last_insert_id
    hash_batch = [str(tuple(hash_row)) for hash_row in hash_batch]
    sql = f"\
        INSERT INTO `app_hashcodemodel` (variant_id,{','.join(hash_keys)})\
        VALUES {','.join(hash_batch)};"

    logger.debug(sql)
    cursor.execute(sql)
    connection.commit()


def parse_row(cohort_id, vcf_head, vcf_tail, info_keys, reader, samples, cursor, all_samples, connection, f_body):
    info_keys_to_rename = list(infos_to_rename.keys())
    full_terms = {k: set() for k in fields_with_terms}
    full_terms['ID'] = set()
    insert_counter = 0
    row_index = 0
    others = set()
    terms = {}
    terms_oversize = []

    fields = []

    process_total_time = 0.0
    insert_variant_time = 0.0
    insert_hashcode_time = 0.0

    batch = []
    hash_batch = []
    hash_keys = [field.name for field in HashCodeModel._meta.fields]
    hash_keys.remove('id')
    hash_keys.remove('variant')

    for row in reader:
        process_time = time.time()

        row['POS'] = f"{row['CHROM']}:{row['Start']}-{int(row['Start'])+len(row['REF'])-1}"
        row['End'] = int(row['Start']) + len(row['REF']) - 1
        row['cohort_id'] = cohort_id
        row['Samples'] = build_samples(all_samples, samples, row)
        row['INFO'] = build_info(row['INFO'], info_keys, info_keys_to_rename)
        row['Others'] = {}

        # process every key in INFO
        for k in row['INFO'].keys():
            # rename col and value
            for ori, after in unicode_table.items():
                row['INFO'][k] = row['INFO'][k].replace(ori, after)
            # transfer from INFO to row
            # numeric field change dot to 1e^-12
            if k in numeric_fields:
                _k = k
                if k in info_keys_to_rename:
                    _k = infos_to_rename[k]
                if row['INFO'][k] == '.':
                    row[_k] = '0.000000000001'
                elif row['INFO'][k] == 'nan':
                    row[_k] = '0.000000000002'
                else:
                    row[_k] = row['INFO'][k]
            elif k in fields_with_terms:
                if k in info_keys_to_rename:
                    row[infos_to_rename[k]] = row['INFO'][k]
                else:
                    row[k] = row['INFO'][k]
            else:
                row['Others'][k] = row['INFO'][k]
                others.add(k)

        row['Others'] = json.dumps(row['Others']).replace('"', '\\"')

        for sample in samples:
            del row[sample]

        full_terms, terms_oversize = build_full_terms(
            full_terms, row['INFO'].keys(), terms_oversize, row)

        del row['INFO']
        fields = list(sorted(row.keys()))
        batch.append('(' + ','.join(f"'{row[v]}'" for v in fields) + ')')

        hash_info_dict, max_hash_info_len = build_hash_info_dict(
            hash_keys, row)

        for i in range(max_hash_info_len):
            hash_row = [hash_info_dict[key][i] for key in hash_keys]
            hash_row = [md5(str.encode(v)) for v in hash_row]
            hash_row = [b64encode(v.digest()).decode('utf-8')
                        for v in hash_row]
            hash_batch.append([row_index]+[v for v in hash_row])

        row_index += 1

        process_total_time += time.time() - process_time

        if len(batch) >= BUFFER_SIZE:
            insert_variant_start = time.time()
            sql = 'INSERT INTO app_variantmodel(' + \
                ','.join(k for k in fields) + ') VALUES '
            sql += ','.join(batch)
            cursor.execute(sql)
            connection.commit()

            insert_counter += 1
            batch = []
            logger.info(f'insert: {insert_counter}')

            insert_variant_time += time.time() - insert_variant_start

            insert_hashcode_start = time.time()
            cursor.execute("SELECT last_insert_id();")
            last_insert_id = cursor.fetchone()[0]
            logger.debug(f'last_insert_id: {last_insert_id}')
            insert_hash_batch(last_insert_id, cursor,
                              hash_batch, hash_keys, connection)
            hash_batch = []
            row_index = 0
            insert_hashcode_time += time.time() - insert_hashcode_start
            CohortModel.objects.filter(id=cohort_id).update(
                created_percentage=(f_body.tell() - vcf_head) * 100 /
                (vcf_tail - vcf_head)
            )

    variants_length = (insert_counter*BUFFER_SIZE) + len(batch)
    if len(batch) > 0:

        insert_variant_start = time.time()
        sql = 'INSERT INTO app_variantmodel(' + \
            ','.join(k for k in fields) + ') VALUES '
        sql += ','.join(batch)
        cursor.execute(sql)
        connection.commit()

        insert_counter += 1
        logger.info(f'insert(left): {insert_counter}')

        insert_variant_time += time.time() - insert_variant_start

        insert_hashcode_start = time.time()
        cursor.execute("SELECT last_insert_id();")
        last_insert_id = cursor.fetchone()[0]
        logger.debug(f'last_insert_id: {last_insert_id}')
        insert_hash_batch(last_insert_id, cursor,
                          hash_batch, hash_keys, connection)
        insert_hashcode_time += time.time() - insert_hashcode_start
        CohortModel.objects.filter(id=cohort_id).update(
            created_percentage=(f_body.tell() - vcf_head) * 100 /
            (vcf_tail - vcf_head)
        )

    process_time = time.time()
    for k in full_terms.keys():
        if len(full_terms[k]) > 0:
            terms[k] = full_terms[k]
    process_total_time += time.time() - process_time

    logger.info(f'len(variants): {variants_length}')
    logger.info(f'** PROCESS TIME = {round(process_total_time, 6)}')
    logger.info(f'** INSERT VARIANT TIME = {round(insert_variant_time, 6)}')
    logger.info(f'** INSERT HASHCODE TIME = {round(insert_hashcode_time, 6)}')

    return terms, others, variants_length


def create_admin_group(user, cohort_id):
    content_type = ContentType.objects.get_for_model(CohortModel)
    permission = Permission.objects.create(
        name=f'Can use cohort: {cohort_id}',
        codename=f'can_use_cohort_{cohort_id}',
        content_type=content_type
    )
    cohort_admin = Group.objects.create(
        name=f'Cohort_{cohort_id} Users',
    )

    cohort_admin.permissions.add(permission)
    user.groups.add(cohort_admin)

    return cohort_admin


def create_cohort_with_SQL(filename, cohort_id, all_samples):
    file = f'{filename}'
    if file.endswith('.vcf'):
        f_header = open(file)
        f_body = open(file)
    elif file.endswith('.vcf.gz'):
        f_header = gzip.open(file, 'rt', encoding='utf-8')
        f_body = gzip.open(file, 'rt', encoding='utf-8')
    else:
        logger.error('error filetype')
        return

    whole_time = time.time()
    start_time = time.time()
    info_dict = parse_header(f_header, f_body)
    infos = set()
    for k in info_dict.keys():
        if info_dict[k]['Type'] != 'Flag':
            infos.add(k)
    logger.info(
        f"*** parse header *** --- {round(time.time()-start_time, 6)} seconds ---")

    vcf_head, vcf_tail = get_vcf_head_tail(f_header)
    f_header.close()
    # variants
    logger.debug(f'parsing {file}...')

    # Prventing "OSError: telling position disabled by next() call"
    # https://stackoverflow.com/questions/14879428/python-csv-distorts-tell

    def generator(csvfile):
        # readline seems to be the key
        while True:
            line = csvfile.readline()
            if not line:
                break
            yield line

    reader = csv.DictReader(generator(f_body), delimiter='\t')

    # get samples, infos set and others set
    start_time = time.time()
    fields = reader.fieldnames
    for field in fields_to_rename.keys():
        fields[fields.index(field)] = fields_to_rename[field]
    samples = [sample for sample in fields[9:]]

    start_time = time.time()
    cursor = connection.cursor()

    terms, others, variants_length = parse_row(
        cohort_id, vcf_head, vcf_tail, infos, reader, samples, cursor, all_samples, connection, f_body)
    logger.info(
        f"*** parse and insert *** --- {round(time.time()-start_time, 6)} seconds ---")

    start_time = time.time()
    for key in terms.keys():
        terms[key] = ','.join(term for term in terms[key])
    if not all_samples:
        samples = []
    cohort_update(cohort_id, variants_length, terms, samples,
                  sorted(others), sorted(infos))
    logger.info(
        f"*** UPDATE *** --- {round(time.time()-start_time, 6)} seconds ---")
    logger.info(f"WHOLE TIME = {round(time.time()-whole_time, 6)}")
