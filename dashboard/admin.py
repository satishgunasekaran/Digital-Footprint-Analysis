from django.contrib import admin
from . import models
# Register your models here.

class PostsAdmin(admin.ModelAdmin):
    list_display = ('dateposted',) 

admin.site.register(models.Posts,PostsAdmin)