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

1. Install python depandencies
   ```
   $ pip install -r requirements.txt
   ```
   and then follow [this answer in stackoverflow.com](https://stackoverflow.com/a/55954355)
   ```
   $ vi <env_directory_name>/Lib/site-packages/django/db/backends/mysql/base.py
   ```

2. Build front-end page
   ```
   $ yarn
   $ yarn build
   ```

3. Configurate dajngo setting and database

   ```
   $ cd proj
   $ cp settings.py.sample settings.py
   $ vi settings.py
   ```
   and set your `SECRET_KEY` and `DATABASE` in `proj.py`.
   
4. Configurate and run database
   Create directory for docker volumne at where you want and run database with docker.
   ```
   $ mkdir mysql
   $ docker run --name=mysql_vash -d -p [port]:3306 -v $PWD/mysql:/var/lib/mysql -e MYSQL_DATABASE=vash -e MYSQL_ROOT_PASSWORD=[vashpassword] mysql
    ```
   Note configuaration in `proj/conf.py` , especially port.
   
   Migrate. 
   ```
   $ ./manage.py makemigrations app
   $ ./manage.py migrate
   ```
   
   Create users.
   ```
   $ cd bin
   $ python3 user.py [username] [password]
   ```
 

    Put your vcariant files(vcf) in `home/[username]/annovar_files/`.
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
|- app/                      # Django backend app main folder.
|   |- migrations/           # Migration scripts for database.
|   |- models.py             # DB Schema and Django models.
|   |- views.py              # Main api methods.
|- bin                       # Execution files and tools for cohort.
|   |- config.py             # Configuration file for every type of score in VCF files.
|   |- model_utils.py.       # Util functions
|   |- user.py               # The script creates user.
|- proj                      # Settings for Django backend.
|   |- settings.py           # Main setting file for Django backend.
|   |- urls.py               # Router for api endpoints.
|- public                    # Front-end public assets 
|- src                       # Front-end source code.
|   |- components            # Vue components.
|   |- store                 # Stores for Vuex.
|   |- config.js             # Main config file for Vue frontend.
|- manage.py                 # Main execution file for Django server.
|- home/[user]/annovarfiles/ # Directory for variant files(vcf). Created after user created.
```
