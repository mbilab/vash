DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'DB_NAME',
        'USER': 'DB_USER_NAME',
        'PASSWORD': 'DB_USER_PASSWORD',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
    # 'default': {
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'vash',
        # 'USER': 'root',
        # 'PASSWORD': 'vashpassword',
        # 'HOST': '127.0.0.1',
        # 'PORT': '10110',
    # }
}
