from django.db import models


class DomainEntity(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Book(DomainEntity):
    title = models.CharField(max_length=100)
    description = models.TextField()
    publisher = models.CharField(max_length=400)
    release_date = models.DateField()

    def __str__(self):
        return self.title


class Author(DomainEntityl):
    name = models.CharField(max_length=225)
    biography = models.TextField()
    date_of_birth = models.DateField()
    books = models.ManyToManyField('Book', related_name='authors', blank=True)

    def __str__(self):
        return self.name

