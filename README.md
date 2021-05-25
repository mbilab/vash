# VASH

Vash is an efficient web-application for filtering and browsing whole genome variants.
After parsing VCF file and creating table in database, users are able to browse whole genome variants smoothly.
Vash provises not only the fluent browsing experience, but also the powerful tools to filter variants.

This repo is open sourece version of Vash.
First version of Vash: [Vash](http://merry.ee.ncku.edu.tw:8083/mbilab/vash). 

## Before Get Started

You must have package installed before installation
- docker
- python >= 3.6
- yarn or npm

## Get Started

1. Setting virtual environment for backend Django
   ```
   $ pip install -r requirement.txt
   ```
   and then follow [this answer in stackoverflow.com](https://stackoverflow.com/a/55954355)

2. Build front-end page
   ```
   $ yarn
   $ yarn build
   ```

3. Setting dajngo configuration and database

   ```
   $ cd proj
   $ cp proj.default.py proj.py
   $ cp conf.default.py conf.py
   $ vi proj.py
   ```
   and set your `SECRET_KEY` in `proj.py`.
   
4. Set and Run database
   Create directory for docker volumne at where you want and run database with docker.
   ```
   $ mkdir mysql
   $ docker run --name=mysql_vash -d -p [port]:3306 -v $PWD/mysql:/var/lib/mysql -e MYSQL_DATABASE=vash -e MYSQL_ROOT_PASSWORD=vashpassword mysql
    ```
   set db configuaration in `proj/conf.py` , especially db port.
   
   Migrate. 
   ```
   $ ./manage.py makemigrations app
   $ ./manage.py migrate
   ```
   
   ```
   $ cd bin
   $ python3 user.py [username] [password]
   ```
 

    Put your vcf-files in `home/[username]/annovar_files/`.
    ```
    cp [vcf-files] into home/[username]/annovar_files/
    ```

5. Run Server

   ```
   $ yarn start:server   
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
