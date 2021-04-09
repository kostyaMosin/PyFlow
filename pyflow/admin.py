from django.contrib import admin

from pyflow.models import Post, PostLike, PostShow, Comment, CommentLike, Tag

admin.site.register(Post)
admin.site.register(PostLike)
admin.site.register(PostShow)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(Tag)
