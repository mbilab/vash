import asyncio
import datetime
import json
import logging
import os
import time
from base64 import b64encode
from hashlib import md5, sha256
from subprocess import PIPE, Popen
from sys import stderr

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib import auth
from django.contrib.auth.models import Group, User
from django.db import connection
from django.db.models import Q
from django.db.utils import InternalError
from django.forms.models import model_to_dict
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render

from bin.config import unicode_table
from bin.model_utils import (_Qs, check_keyword_is_contained_in_term_model,
                             create_admin_group, create_cohort_with_SQL,
                             create_sub_variants, has_only_terms)

from .models import CohortModel, HashCodeModel, VariantModel

_MAX_VARIANTS_PER_REQUEST = 500
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HOME = os.path.join(_BASE_DIR, 'home')

variants_sorted = []

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s\t%(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
logger = logging.getLogger(__name__)


def _base64(content, length=11):  # 11 x 6 = 66 bits
    code = content.encode('utf-8')
    code = sha256(code).digest()
    code = b64encode(code)
    return str(code)[:length]


def use_get(func):
    def wrapper(request, *args, **kwargs):
        if 'GET' != request.method:
            return JsonResponse({'error': f'Method `{request.method}` not allowed.'})
        return func(request, *args, **kwargs)

    return wrapper


def use_post(func):
    def wrapper(request, *args, **kwargs):
        if 'POST' != request.method:
            return JsonResponse({'error': f'Method `{request.method}` not allowed.'})
        return func(request, *args, **kwargs)

    return wrapper


def is_authenticated(f):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'error': f'User not logged in.'})

        try:
            return f(request, *args, **kwargs)
        except CohortModel.DoesNotExist as e:
            return JsonResponse({'error': f'Cohort id not found.'})

    return wrapper


@use_post
@is_authenticated
def cohort(request, cohort_id):
    if not request.user.has_perm(f'app.can_use_cohort_{cohort_id}'):
        return JsonResponse({'error': 'User has no permission of use this cohort'})
    # parameters
    get = json.loads(request.body.decode('utf-8')).get
    query_str = get('queries', '[]')
    queries = json.loads(query_str)

    if 0 == len(queries):  # non-filtered cohort request
        cohort = CohortModel.objects.get(pk=cohort_id)
    else:  # filtered cohort request
        token = _base64(str(cohort_id) + query_str)
        try:
            # seen queries
            cohort = CohortModel.objects.get(token=token)
        except CohortModel.DoesNotExist:
            # unseen queries
            cohort = CohortModel.objects.get(pk=cohort_id)
            qs = _Qs(cohort, queries)
            cohort.save_filter(token, query_str)

            valid = check_keyword_is_contained_in_term_model(
                cohort_id, queries)
            if valid:
                cohort.n_variants = CohortModel.objects.get(
                    id=cohort_id).variantmodel_set.filter(qs).count()
            else:
                cohort.n_variants = 0
            cohort.save()

    cohort = model_to_dict(cohort)
    cohort['id'] = cohort_id

    #! fix these
    del cohort['owner']
    del cohort['token']

    return JsonResponse(cohort)


@use_post
@is_authenticated
def update_cohort(request, cohort_id):
    cohort = CohortModel.objects.get(id=cohort_id)
    if not cohort.is_owned_by(request.user):
        return JsonResponse({'error': 'User does not own editing this cohort'})

    get = json.loads(request.body.decode('utf-8')).get
    update_obj = get('update_obj')

    cohort = CohortModel.objects.filter(id=cohort_id)
    cohort.update(**update_obj)

    return JsonResponse({})


@use_post
@is_authenticated
@async_to_sync
async def create_cohort(request):
    # def create_cohort(request):
    samples = []
    cases = []
    controls = []
    files = []
    # bam_prefix = ''

    get = json.loads(request.body.decode('utf-8')).get
    cohort = get('cohort', [])
    cohort_name = get('name', '')
    description = get('description', '')
    bam = get('bam', '').replace(', ', ',')
    all_samples = get('allSamples', bool)

    for sample, infos in cohort.items():
        if infos['selected']:
            samples.append(sample)
            files.append(infos['path'])
            cases.append(sample) if infos['case'] else None
            controls.append(sample) if infos['control'] else None
    vcfs_string = ' '.join(files)

    descriptions = {
        'title': cohort_name,
        'detail': description,
    }

    infos = {
        'bam': bam,
        'description': descriptions,
        'filtered': [],
    }

    cohort = {
        'name': cohort_name,
        'info': json.dumps(infos),
        'queries': json.dumps([]),
        'owner': request.user,
        'pid': 1,
        'token': '',
        'ctime': datetime.datetime.now(),
        'created_percentage': 0,
        'samples': ''
    }
    cohort = await sync_to_async(CohortModel.objects.create)(**cohort)
    await sync_to_async(cohort.save)()
    # cohort = CohortModel.objects.create(**cohort)
    # cohort.save()
    cohort_id = cohort.id
    asyncio.ensure_future(sync_to_async(create_cohort_with_SQL)(
        f'{_HOME}/{request.user.username}/annovar_files/{vcfs_string}',
        cohort_id,
        all_samples
    ))
    # create_cohort_with_SQL(
    #     f'{_HOME}/{request.user.username}/annovar_files/{vcfs_string}',
    #     cohort_id,
    #     all_samples
    # )

    admin_group = await sync_to_async(create_admin_group)(request.user, cohort_id)
    # admin_group = create_admin_group(request.user, cohort_id)

    cohort.admin_group = admin_group
    await sync_to_async(cohort.save)()
    # cohort.save()

    return JsonResponse({})


@use_post
@is_authenticated
@async_to_sync
async def create_sub_cohort(request):
    get = json.loads(request.body.decode('utf-8')).get
    cohort_ori_id = get('cohort_id', '')
    if not await sync_to_async(request.user.has_perm)(f'app.can_use_cohort_{cohort_ori_id}'):
        return JsonResponse({'error': 'User has no permission of editing this cohort'})

    cohort_name = get('name', '')
    description = get('description', '')
    bam = get('bam', '').replace(', ', ',')
    filtered = get('filtered', '')
    n_variants = get('n_variants', '')
    queries = json.loads(get('queries', []))

    cohort_ori = await sync_to_async(CohortModel.objects.get)(pk=cohort_ori_id)
    parent_cohort_id = cohort_ori.parent_cohort_id if cohort_ori.parent_cohort_id else cohort_ori_id

    descriptions = {
        'title': cohort_name,
        'detail': description,
    }

    infos = {
        'bam': bam,
        'description': descriptions,
        'filtered': filtered,
    }

    cohort = {
        'available': cohort_ori.available,
        'ctime': datetime.datetime.now(),
        'info': json.dumps(infos),
        'n_variants': int(n_variants),
        'name': cohort_name,
        'others': cohort_ori.others,
        'owner': request.user,
        'pid': 1,
        'queries': json.dumps([]),
        'samples': cohort_ori.samples,
        'token': '',
        'parent_cohort_id': parent_cohort_id,
        'created_percentage': 0,
    }
    cohort = await sync_to_async(CohortModel.objects.create)(**cohort)

    admin_group = await sync_to_async(create_admin_group)(request.user, cohort.id)
    asyncio.ensure_future(sync_to_async(create_sub_variants)(
        cohort.id, cohort_ori_id, queries, admin_group))

    cohort.admin_group = admin_group
    await sync_to_async(cohort.save)()

    return JsonResponse({})


@use_post
@is_authenticated
@async_to_sync
async def delete_cohort(request, cohort_id):
    cohort = await sync_to_async(CohortModel.objects.get)(id=cohort_id)
    if not await sync_to_async(cohort.is_owned_by)(request.user):
        return JsonResponse({'error': 'User does not own editing this cohort'})

    cohort.pid = 2
    await sync_to_async(cohort.save)()
    asyncio.ensure_future(sync_to_async(cohort.delete)())
    return JsonResponse({})


@use_get
@is_authenticated
@async_to_sync
async def add_sharing_cohort(request, cohort_id, user_id):
    cohort = await sync_to_async(CohortModel.objects.get)(id=cohort_id)
    if not await sync_to_async(cohort.is_owned_by)(request.user):
        return JsonResponse({'error': 'User does not own this cohort'})

    if not await sync_to_async(cohort.parent_is_owned_by)(request.user):
        return JsonResponse({'error': 'User can not sahre  this cohort'})

    user = await sync_to_async(User.objects.get)(id=user_id)
    admin_group = await sync_to_async(Group.objects.get)(name=f'Cohort_{cohort_id} Users')

    if await sync_to_async(user.has_perm)(f'app.can_use_cohort_{cohort_id}'):
        return JsonResponse({'error': 'User has permission already'})
    else:
        await sync_to_async(user.groups.add)(admin_group)

    return JsonResponse({})


@use_get
@is_authenticated
@async_to_sync
async def remove_sharing_cohort(request, cohort_id, user_id):
    cohort = await sync_to_async(CohortModel.objects.get)(id=cohort_id)
    if not await sync_to_async(cohort.is_owned_by)(request.user):
        return JsonResponse({'error': 'User does not own editing this cohort'})

    user = await sync_to_async(User.objects.get)(id=user_id)
    admin_group = await sync_to_async(Group.objects.get)(name=f'Cohort_{cohort_id} Users')

    if await sync_to_async(user.has_perm)(f'app.can_use_cohort_{cohort_id}'):
        await sync_to_async(user.groups.remove)(admin_group)
    else:
        return JsonResponse({'error': 'User has no permission yet'})

    return JsonResponse({})


@use_get
@is_authenticated
def get_friends(request):
    users = User.objects.all().exclude(id=request.user.id)

    friends = [{
        'name': user.username,
        'id': user.id,
        'groups': list(user.groups.all().values())
    } for user in users]

    return JsonResponse({'friends': friends})


@use_get
def index(request):
    return render(request, 'index.html')


@use_post
def login(request):
    params = json.loads(request.body.decode('utf-8'))
    user = auth.authenticate(request, **params)
    if not user:
        return JsonResponse({'error': f'Incorrect username or password.'})
    auth.login(request, user)
    return me(request, user=user)


@use_post
def logout(request):
    auth.logout(request)
    return JsonResponse({})


@use_post
@is_authenticated
def me(request, user=None):
    if not user:
        user = request.user
    vcfs = []
    try:
        fdir = os.listdir(f'./home/{user}/annovar_files/')
        for vcf in fdir:
            sample = vcf.split('.')[0]
            # sample = vcf
            vcfs.append({
                'mtime': datetime.datetime.fromtimestamp(os.path.getmtime(f'./home/{user}/annovar_files/{vcf}')).strftime('%Y-%m-%d %H:%M:%S'),
                'path': vcf,
                'sample': sample
            })
    except:
        pass
    bams = []
    try:
        fdir = sorted(os.listdir(f'./home/{user}/bams/'))
        fdir_bam = [f for f in fdir if f.split('.')[-1] == 'bam']
        for bam in fdir_bam:
            bams.append({
                'path': bam,
                'sample': bam
            })
    except:
        pass
    user_groups = request.user.groups.all()
    cohorts = CohortModel.objects.none()
    for group in user_groups:
        if not group.cohortmodel_set.filter(token='').exists():
            continue
        cohorts |= group.cohortmodel_set.filter(token='')
    user = model_to_dict(user, fields=['id', 'username'])
    user['cohorts'] = list(cohorts.values(
        'ctime',
        'id',
        'info',
        'name',
        'n_variants',
        'pid',
        'queries',
        'samples',
        'available',
        'others',
        'owner',
        'parent_cohort_id',
        'created_percentage'
    ))
    user['vcfs'] = vcfs
    user['bams'] = bams
    return JsonResponse(user)


@ use_post
@ is_authenticated
def terms(request, cohort_id):
    if not request.user.has_perm(f'app.can_use_cohort_{cohort_id}'):
        return JsonResponse({'error': 'User has no permission of use this cohort'})
    get = json.loads(request.body.decode('utf-8')).get
    field = get('dbName')
    keyword = get('keyword', '')

    for ori, after in unicode_table.items():
        keyword = keyword.replace(ori, after)

    try:
        # TODO check if field exists for safer sql
        cursor = connection.cursor()
        cursor.execute(f"SELECT /*+ MAX_EXECUTION_TIME(500) */ `app_{field.lower()}terms`.`term`\
        FROM `app_{field.lower()}terms`\
        WHERE `app_{field.lower()}terms`.`cohort_id` = %(cohort_id)s\
        AND `app_{field.lower()}terms`.`term` LIKE %(keyword)s\
        LIMIT 10", {
            'cohort_id': cohort_id,
            'keyword': f'%{keyword}%'
        })
        terms = cursor.fetchall()
    except InternalError:
        terms = []

    terms = [term[0].replace("''", "'") for term in terms]

    return JsonResponse(terms, safe=False)


@ use_post
@ is_authenticated
def variants(request, cohort_id, start, size):
    if not request.user.has_perm(f'app.can_use_cohort_{cohort_id}'):
        return JsonResponse({'error': 'User has no permission of use this cohort'})

    # parameters
    get = json.loads(request.body.decode('utf-8')).get
    queries = json.loads(get('queries', '[]'))
    reverse = get('reverse', 'false')
    size = max(min(size, _MAX_VARIANTS_PER_REQUEST), 0)

    startTime = time.time()
    cohort = CohortModel.objects.get(id=cohort_id)
    valid = check_keyword_is_contained_in_term_model(cohort.id, queries)
    if not valid:
        return JsonResponse({'rows': [], 'start': start})

    qs = _Qs(cohort, queries)
    logger.debug(qs)
    try:
        if not reverse:
            variants = cohort.variantmodel_set.filter(qs)[start:start+size]
        else:
            variants = cohort.variantmodel_set.filter(qs).reverse()[
                start: start+size]
    except VariantModel.DoesNotExist:
        return JsonResponse({'error': f'Cohort id `{cohort_id}` not found'})
    variants = list(variants.values())
    if reverse:
        variants.reverse()
    if len(variants) == 0:
        return JsonResponse({'rows': [], 'start': start})
    db_start_id = variants[0]["id"]
    db_end_id = variants[-1]["id"]
    logger.info(
        f'index: {start}\ttime: {time.time() - startTime}s\tdb_start_id: {db_start_id}\tdb_end_id: {db_end_id}\treverse: {reverse}'
    )
    samples = json.loads(variants[0]['Samples']).keys()

    others = json.loads(variants[0]['Others']).keys()
    for variant in variants:
        for sample in samples:
            variant[sample] = json.loads(variant['Samples'])[sample]
        for other in others:
            variant[other] = json.loads(variant['Others'])[other]

    return JsonResponse({'rows': variants, 'start': start, 'db_start_id': db_start_id, 'db_end_id': db_end_id})
