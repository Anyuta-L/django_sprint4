from django.urls import path

from . import views
from .views import (AddCommentView, CommentDeleteView, CreatePostView,
                    EditCommentView, EditPostView, EditProfileView,
                    PostDeleteView, PostDetailView, ProfileView,
                    category_posts_view)

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:category_slug>/', category_posts_view, name='category_posts'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('posts/create/', CreatePostView.as_view(), name='create_post'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/edit/', EditPostView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:pk>/', EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/delete_comment/<int:pk>/', CommentDeleteView.as_view(), name='delete_comment'),
    ]
