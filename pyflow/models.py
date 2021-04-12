from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    content_code = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', related_name='posts')
    create_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    def __str__(self):
        return f'{self.pk} {self.title}'


class PostLike(models.Model):
    value = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        null=True,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='post_likes',
    )

    def __str__(self):
        return f'{self.pk} value: {self.value} | {self.post}'


class PostShow(models.Model):
    post = models.ForeignKey(
        Post,
        null=True,
        on_delete=models.CASCADE,
        related_name='shows'
    )
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.post} show: {self.create_at}'


class Comment(models.Model):
    comment = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    def __str__(self):
        return f'{self.pk} comment for post: {self.post}'


class CommentLike(models.Model):
    value = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(
        Comment,
        null=True,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    def __str__(self):
        return f'{self.pk} value: {self.value} | {self.comment}'


class Tag(models.Model):
    title = models.CharField(max_length=30)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title}'
