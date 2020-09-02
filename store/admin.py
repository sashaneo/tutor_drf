from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin

from store.models import Book, UserBookRelation

admin.site.register(Book)


# @admin.register(Book)
# class BookAdmin(ModelAdmin):
#     pass

@admin.register(UserBookRelation)
class UserBookRelation(ModelAdmin):
    pass
