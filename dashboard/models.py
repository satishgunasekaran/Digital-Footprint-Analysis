from django.db import models

class Posts(models.Model):
    dateposted = models.CharField(max_length = 200)
    text = models.TextField()
    likes = models.PositiveIntegerField()  
    created = models.DateTimeField(auto_now_add = True)
