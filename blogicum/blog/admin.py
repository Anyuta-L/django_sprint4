from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_published',)


admin.site.register(Category, CategoryAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_published',)


admin.site.register(Location, LocationAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at', 'author')
    search_fields = ('title', 'text')
    list_filter = ('is_published', 'author', 'category')
    date_hierarchy = 'pub_date'


admin.site.register(Post, PostAdmin)
