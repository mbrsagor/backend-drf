# Docker product docs


[Source](https://learndjango.com/tutorials/django-docker-and-postgresql-tutorial)

```bash
docker-compose up -d --build
docker-compose exec web python manage.py makemigrations user
docker-compose exec web python manage.py migrate
docker-compose up
docker-compose down
```
