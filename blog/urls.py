from django.contrib import admin
from django.urls import path,include
from . import views

from .views import(PostListView,
                   PostDetailView,
                   PostCreateView,
                   PostUpdateView,
                   PostDeleteView,
                   UserPostListView) 
from . import views

urlpatterns = [
    path("", views.PostListView.as_view(), name="blog-home"),  # homepage
    path("user/<str:username>/", views.UserPostListView.as_view(), name="user-posts"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),  # ✅ use .as_view()
    path("post/new/", views.PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name="post-update"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
    path("like/<int:pk>/", views.like_post, name="like-post"),  # function-based
    path("comment/<int:pk>/", views.add_comment, name="add-comment"),  # function-based
    path("about/", views.about, name="blog-about"),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit-comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete-comment'),
]