from django import forms

from .models import Category, Comment, Location, Post


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('title', 'description', 'slug',)


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ('name',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date',
                  'location', 'category', 'image',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
