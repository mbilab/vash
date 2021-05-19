import django
import os
import sys
sys.path.append('../')

username = sys.argv[1]
password = sys.argv[2]
paths = ['annovar_files', 'bams', 'tmp']

if '__main__' == __name__:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
    django.setup()
    from django.contrib.auth.models import User

    user = User.objects.create_user(username, '', password)
    try:
        os.makedirs(f'../home/{username}')
    except:
        print(f'username folder {username} exist')
    for path in paths:
        try:
            os.mkdir(f'../home/{username}/{path}')
        except:
            print(f'path folder {path} exist')
    try:
        user.save()
    except:
        print(f'{username} exist')
