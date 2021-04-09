from django.urls import path

from pyflow.views import view_main, \
    view_detail, view_add_like_or_dislike_value, view_create_post, \
    view_edit_post, view_delete_post, view_delete_comment

urlpatterns = [
    path('', view_main, name='index'),
    path('post/<int:pk>', view_detail, name='detail'),
    path('post/create/', view_create_post, name='create-post'),
    path('post/edit/<int:pk>', view_edit_post, name='edit-post'),
    path('post/delete/<int:pk>', view_delete_post, name='delete-post'),
    path('comment/delete/<int:pk>', view_delete_comment, name='delete-comment'),
    path('rating/<obj_type>/<int:pk>', view_add_like_or_dislike_value, name='rating'),
]
