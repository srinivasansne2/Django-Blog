from django.contrib import admin
from .models import Category, Post, AboutUs


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    search_fields=('title', 'content')
    list_filter=('category',)


# Register your models here.
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(AboutUs)




