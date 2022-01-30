# Running in local
Setup the mysql database first 
 - import schema.sql

0. install pipenv with command
    pip install pipenv
1. ##check docker / local comments for testing 
2. pipenv shell
3. pipenv install <package_name> (for any packages to be installed)
3.1. try this command if package issues
   pipenv install requests fastapi mysql-connector-python pymysql pytz sqlalchemy uvicorn

4. uvicorn app.main:controller --reload (to start the app locally)
OR 
uvicorn main:controller --reload
5. swagger(<>/docs)
6. Redoc(<>/redoc)

# Docker build 
docker build -t hevolve-db-app:oct25 .

# Docker run
docker run -d --net=host --name hevolve_db_app hevolve-db-app:oct25

# Remove UNIQUE constraint on question_and_answer model
# Keep NOT NULL constraint on question_and_answer model




## Others - start
```
    desc question_and_answer;
    SHOW INDEX FROM question_and_answer;
    alter table question_and_answer drop index question;
    alter table question_and_answer drop index answer;
    alter table question_and_answer modify column question varchar(1000) not null;
```

TRY #0
update bind-address to 0.0.0.0 in the following 
/etc/mysql/mysql.conf.d/mysqld.cnf

#restart
created new user fastApiUser and updated db url.
## Others - end


### references 
rest
fastapi
sqlalchemy
pydantic
docker 