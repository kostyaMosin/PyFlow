from django.urls import path

from pyflow.views import view_main, \
    view_detail, view_add_like_or_dislike_value, view_create_post, \
    view_edit_delete_post, view_delete_comment, view_sort_by_tag, \
    view_sort_by_date, view_send_post

urlpatterns = [
    path('', view_main, name='index'),
    path('post/<int:pk>', view_detail, name='detail'),
    path('post/create/', view_create_post, name='create-post'),
    path('post/edit/<int:pk>', view_edit_delete_post, name='edit-delete-post'),
    path('post/tag/<int:pk>', view_sort_by_tag, name='post-by-tag'),
    path('post/date/', view_sort_by_date, name='post-by-date'),
    path('comment/delete/<int:pk>', view_delete_comment, name='delete-comment'),
    path('rating/<obj_type>/<int:pk>', view_add_like_or_dislike_value, name='rating'),
    path('send_post/<int:pk>', view_send_post, name='send-post'),
]
