from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task (models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    # null = para la base de datos es necesario, blanck= opcional para el admin
    dateCompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    # cascada porque si se elimina el user, se eliminan sus tasks
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + ' - Usuario: ' + self.user.username