# standard import
import json
import os
import sys
from base64 import b64encode
from hashlib import md5

# django import
import django
from django.db.models import Q

# local import
from config import fields_with_terms, infos_to_rename

sys.path.append('../')


BUFFER_SIZE = 1000


def _Qs(cohortId, queries):
    qs = Q(cohort_id=cohortId)
    for query in queries:
        key = list(query.keys())[0]
        if "__icontains" in key:
            sqs = Q()
            for value in list(query.values())[0]:
                sqs |= Q(**{key: value})
            qs &= sqs
        else:
            qs &= Q(**query)
    return qs


def QfullyMatches(fullyMatches):
    qs = Q()
    # fullyMatches = [{'variantID': ['rs123', 'rs234']}, {'???':[???, ???]} ]
    for fullyMatch in fullyMatches:
        sub_qs = Q()

        key = 'variantID'
        if not key in fullyMatch:
            continue
        values = fullyMatch[key]
        if '.' in values:
            values.remove('.')
            sub_qs |= Q(variantID__icontains='.')

        hs = [md5(str.encode(value)) for value in values]
        hashcodes = [b64encode(h.digest()) for h in hs]
        hashcodes = [hashcode.decode('utf-8')[:5] for hashcode in hashcodes]
        hashcodes = IDHashCodeModel.objects.filter(hashcode__in=hashcodes)
        hashcodes = hashcodes.values('variant_id')
        id_list = [hashcode['variant_id'] for hashcode in hashcodes]

        sub_qs |= Q(id__in=id_list)
        qs &= sub_qs

    return qs


def add_IDhash(cohort_id):
    variants = VariantModel.objects.filter(cohort_id=cohort_id)
    for variant in variants:
        for id in variant.variantID.split(';'):
            h = md5(str.encode(id))
            hashcode = b64encode(h.digest()).decode('utf-8')[:5]

            id_hash_code = IDHashCodeModel(
                id=None, hashcode=hashcode, variant=variant)
            id_hash_code.save()


def create_sub_variants(id, id_ori, queries, fullyMatches):
    print(id, id_ori, queries, fullyMatches)
    qs = _Qs(id_ori, json.loads(queries))
    qfullyMatches = QfullyMatches(fullyMatches)
    qs &= qfullyMatches
    print(qs)
    cohort = CohortModel.objects.get(pk=id)
    cohort_ori = CohortModel.objects.get(pk=id_ori)
    variants = VariantModel.objects.filter(qs)

    counter = 0
    sub_variants = []
    terms_keys = list(json.loads(cohort_ori.terms).keys())
    terms = {k: set() for k in terms_keys}
    terms['ID'] = set()

    print('start filtering')
    for variant in variants:
        variant.pk = None
        variant.cohort_id = id
        sub_variants.append(variant)
        counter += 1

        # terms
        for field in terms_keys:
            if field in infos_to_rename.keys():
                terms[field].add(variant.__dict__[infos_to_rename[field]])
            elif field == 'ID':
                terms['ID'].add(variant.__dict__['variantID'])
            else:
                terms[field].add(variant.__dict__[field])

        if counter == 1000:
            VariantModel.objects.bulk_create(sub_variants)
            sub_variants = []
            counter = 0

    if sub_variants:
        VariantModel.objects.bulk_create(sub_variants)

    print('sub variant insert complete')

    add_IDhash(cohort.id)
    print('add ID hashcode complete')

    for key in terms.keys():
        terms[key] = ','.join(term for term in terms[key])
    cohort.terms = json.dumps(terms).replace("'", "''")
    cohort.pid = 0
    cohort.save()
    print('cohort update complete')


if '__main__' == __name__:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
    django.setup()
    from app.models import *

    print(len(sys.argv))
    if len(sys.argv) == 5:
        id = sys.argv[1]
        id_ori = sys.argv[2]
        queries = sys.argv[3]
        fullyMatches = sys.argv[4]
        create_sub_variants(id=id, id_ori=id_ori,
                            queries=queries, fullyMatches=fullyMatches)
