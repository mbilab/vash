# VASH2.0

Vash2.0 is an efficient web-application for filtering and browsing whole genome variants.
After parsing VCF file and creating table in database, users are able to browse whole genome variants smoothly.
Vash provises not only the fluent browsing experience, but also the powerful tools to filter variants.

Built on [Vash](http://merry.ee.ncku.edu.tw:8083/mbilab/vash) source code. 

## Before Get Started

You must have package installed before installation

    - docker
    - python >= 3.6
    - python3-pip
    - yarn v1.16.0

## Get Started

1. Setting virtual environment for backend Django

   ```
   $ virtualenv -p python3.6 [virtualenv/directory]
   $ . [virtualenv/directory/bin/activate]
   $ pip install -r requirement.txt
   # follow following stackoverflow
   # https://stackoverflow.com/questions/55657752/django-installing-mysqlclient-error-mysqlclient-1-3-13-or-newer-is-required
   ```

2. Setting frontend for parcel and vue

   ```
   $ yarn
   $ yarn build:pug
   ```

3. Setting user directory and database

   ```
   $ ./manage.py migrate
   # add user and folders
   $ cd bin && python3 user.py [username] [password]
   # cp [vcf-files] into home/username/annovar_files/

   # start db
   $ mkdir mysql && docker run --name=mysql_vash -d -p [port]:3306 -v $PWD/mysql:/var/lib/mysql -e MYSQL_DATABASE=vash -e MYSQL_ROOT_PASSWORD=vashpassword mysql

   # setting db config, especially db port
   $ cd proj
   $ cp proj.default.py proj.py
   $ vi proj.py
   ```

4. Run

   ```
   # caution: virtualenv need to be activated

   # run with all default
   (venv) $ yarn start
   # then open localhost:10102 on browser

   # change default port
   $ echo [port] > port
   (venv) $ yarn start

   # run frontend and backend seperately
   (venv) $ yarn start:django
   $ yarn watch:vue
   ```

## Dependencies

- [bcftools](http://www.htslib.org/download/)
  Download bcfools-1.x from http://www.htslib.org/download/

```
$ cd bcfools-1.x
$ ./configure --prefix=/where/to/install
$ make
$ make install # you may need sudo permission for install
```

- [annovar](http://annovar.openbioinformatics.org/en/latest/)

```
$ cd bin/tools/annovar
$ sh update_db.sh
```

## Experiment

1. Buffer size
   The query size is not unlimited, so there is a buffer size need to determine. After doing some test, the query needed to executed every 1000000 of query values,
   the size of byte string is between 886425578 to 951147664 bytes, so the information that said the max size of query is 1GB is confirmed.

## Postgresql Tutorial

1. Connect Database

   ```
   $ psql dbname username
   ```

2. Show Tables

   ```
   [dbname]=# /dt
   ```

## Project Structure

```
vcf-viewer/
|- app/                     # Django backend app main folder.
|   |- migrations/          # Migration scripts for database.
|   |- models.py            # DB Schema and Django models.
|   |- views.py             # Main api methods.
|- bin                      # Execution files and tools for cohort.
|   |- tools/               # Kggseq, Annovar program and scripts from Don-Chi.
|   |- config.py            # Configuration file for every type of score in VCF files.
|   |- annovar_parser.py    # Parser for combined cohort files via do.sh, should be rename.
|   |- do_tmp.sh            # Test commands for kggseq, can be deleted.
|   |- do.sh                # Scripts to run kggseq, bcftools, sed/cut (cut vcf file), and parser for cohort.
|   |- save_pid.py          # When do.sh begin, save pid to database.
|   |- sub_variants.py      # Save filtered cohort as new cohort script.
|   |- user.py          	# Add user script
|- components               # Components for Vue frontend.
|- dist                     # (Auto created) Compiled file via parcel.
|- home                     # (Auto created) Users folder to save vcf files, combined files, and pedigree files.
|- proj                     # Settings for Django backend.
|   |- settings.py          # Main setting file for Django backend.
|   |- urls.py              # Router for api endpoints.
|- store                    # Stores for Vuex.
|- config.js                # Main config file for Vue frontend.
|- db.sqlite3               # Sqlite database file, should be deleted after change db engine to postgresql.
|- index.pug                # Template file for index.
|- manage.py                # Main execution file for Django server.
|- mock.js                  # Some mock data for develop.
|- package.json             # Yarn(NPM) config file.
|- proj.js                  # Entry point for Vue.
|- proj.jsx                 # Entry point for React.
|- README.md                # Readme.
|- requirement.txt          # Dependencies for python.
|- yarn.lock                # Yarn lock file.
```

## FAQ

1. python version

Q:

```
(venv) $ yarn start:django
yarn run v1.3.2
(node:72162) [DEP0005] DeprecationWarning: Buffer() is deprecated due to security and usability issues. Please use the Buffer.alloc(), Buffer.allocUnsafe(), o
r Buffer.from() methods instead.

......(Error Messages).....

SyntaxError: invalid syntax
error Command failed with exit code 1.
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.
```

A: python version < v3.6, make sure python version of virtual environment is above v3.6

```
# check python version of virtual environment
(venv) $ python --version
```
