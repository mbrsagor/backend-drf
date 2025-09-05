# DRF Backend API
> Django Rest framework backend API server, which has to implement Celery and Docker.

### Setup

The following steps will walk you through installation on a Mac. Linux should be similar.
It's also possible to develop on a Windows machine, but I have not documented the steps.
If you've developed Django apps on Windows, you should have little problem getting
up and running.

#### Dependencies
###### Prerequisites

- Python 3.8.9 
- PostgreSQL 13.2
- Django 3.2
- Docker

Create a virtualenv in your system, then follow the comments:
```` virtualenv venv --python=python3.8 ````

If you successfully create the virtualenv, then activate:
```source venv/bin/activate```

> Then create `.env` file and paste code from the `.env-sample` file and update valid information.

After that, you may run the `requirements.txt` file following the command:
```bash
pip install -r requirements.txt
./manage.py migrate
./manage.py runserver
```

##### If you run the project Docker, please follow the instructions in this self-learning guide.
```base
docker-compose run drfbackend
docker-compose build
docker-compose up
```

## Table of contents:
- Well-organized `CRUD` operations
- Custom user model
   - User Account
   - User Login
   - User Registration
   - User Account by email
   - User Reset Password
   - User Reset Password
 - JET authentication system
 - Token-based authentication system
 - SMTP email sending

There are two branches here.
```
git branch
```
* Master


> if you want to fix any kind of database migrations, you should follow these instructions. 

>> Open your terminal:
```bash
psql -U postgres
```
Then,
```psql
\c my-db;
ALTER TABLE blog_post ADD COLUMN created_at with time zone DEFAULT now();
```

> Docker:
```bash
docker exec -it postgres_db psql -U postgres
\c db_name;
ALTER TABLE catalogue_submission ADD COLUMN status INTEGER DEFAULT 1;
ALTER TABLE catalogue_submission RENAME COLUMN old_field_name TO new_field_name;
```
