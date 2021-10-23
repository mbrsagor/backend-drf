# DRF Backend API
> Django Rest framework backend API server which has to implement Celery and Docker.

### Setup

The following steps will walk you thru installation on a Mac. Linux should be similar.
It's also possible to develop on a Windows machine, but I have not documented the steps.
If you've developed Django apps on Windows, you should have little problem getting
up and running.

#### Dependencies
###### Prerequisites

- Python 3.8.9 
- PostgreSQL 13.2
- Django 3.2
- Docker

Create virtualenv in your system then follow the commends:
```` virtualenv venv --python=python3.8 ````

If you successfully create the virtualenv then activate:
```source venv/bin/activate```

> Then crete `.env` file and paste code from `.env-sample` file and update valid information.

After that you may run `requirements.txt` file following the command:
```bash
pip install -r requirements.txt
./manage.py migrate
./manage.py runserver
```

##### If you run the the project Docker, please follow the instructions in this self-learning guide.
```base
docker-compose run drfbackend
docker-compose build
docker-compose up
```

## Table of contents:
- Well organized `CRUD` operations
- Custom user model
   - User Account
   - User Login
   - User Registration
   - User Account by email
   - User Reset Password
   - User Reset Password
 - JET authentication system
 - Token based authentication system
 - SMTP email sending

There are two branch here.
```
git branch
```
* Master
* ModelsRelationShip-API
