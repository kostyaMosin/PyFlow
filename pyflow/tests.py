from django.contrib.auth.models import User
from django.test import TestCase
from django.db.models import QuerySet
import pytz
from datetime import datetime as dt, timedelta

from pyflow.forms import CommentForm
from pyflow.models import Post, Tag, PostLike, PostShow, Comment, CommentLike


class ViewTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(username='user1')
        self.user_2 = User.objects.create_user(username='user2')
        self.tag_1 = Tag.objects.create(title='tag 1')
        self.tag_2 = Tag.objects.create(title='tag 2')
        self.post_1 = Post.objects.create(
            title='title 1', content='content 1', content_code='content code 1', user=self.user_1
        )
        self.post_2 = Post.objects.create(
            title='title 2', content='content 2', content_code='content code 2', user=self.user_1
        )
        self.post_1.tags.set(Tag.objects.filter())
        self.post_2.tags.add(self.tag_1)
        self.post_1.save()
        self.post_2.save()
        self.post_1_like_1 = PostLike.objects.create(value=1, post=self.post_1, user=self.user_1)
        self.post_1_like_2 = PostLike.objects.create(value=1, post=self.post_1, user=self.user_2)
        self.post_2_like_1 = PostLike.objects.create(value=-1, post=self.post_2, user=self.user_1)
        self.post_2_like_2 = PostLike.objects.create(value=-1, post=self.post_2, user=self.user_2)
        self.post_1_show_1 = PostShow.objects.create(post=self.post_1, user=self.user_1)
        self.post_1_show_2 = PostShow.objects.create(post=self.post_1, user=self.user_2)
        self.post_2_show_1 = PostShow.objects.create(post=self.post_2, user=self.user_1)
        self.comment_1 = Comment.objects.create(comment='comment 1', post=self.post_1, user=self.user_1)
        self.comment_2 = Comment.objects.create(comment='comment 2', post=self.post_1, user=self.user_2)
        self.comment_1_like_1 = CommentLike.objects.create(value=1, comment=self.comment_1, user=self.user_2)

    def test_view_main(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertIn('posts', response.context)
        posts = response.context['posts']
        self.assertIsInstance(posts, QuerySet)
        self.assertIn(self.post_1, posts)
        self.assertIn(self.post_2, posts)
        post_1 = posts.get(id=self.post_1.pk)
        post_2 = posts.get(id=self.post_2.pk)
        self.assertIsInstance(post_1, Post)
        self.assertIsInstance(post_2, Post)
        self.assertEqual(post_1, self.post_1)
        self.assertEqual(post_2, self.post_2)
        self.assertEqual(post_1.rating, 2)
        self.assertEqual(post_2.rating, -2)
        self.assertEqual(list(posts), [self.post_2, self.post_1])
        self.assertIn('posts_popular', response.context)
        posts_popular = response.context['posts_popular']
        self.assertIsInstance(posts_popular, QuerySet)
        self.assertIn(self.post_1, posts_popular)
        self.assertIn(self.post_2, posts_popular)
        self.assertEqual(post_1.shows.count(), 2)
        self.assertEqual(post_2.shows.count(), 1)
        self.assertEqual(posts_popular[0], post_1)
        self.assertEqual(posts_popular[1], post_2)
        self.assertEqual(list(posts_popular), [self.post_1, self.post_2])
        self.assertIn('tags', response.context)
        tags = response.context['tags']
        self.assertIsInstance(tags, QuerySet)
        self.assertIn(self.tag_1, tags)
        self.assertIn(self.tag_2, tags)
        tag_1 = tags.get(id=self.tag_1.pk)
        tag_2 = tags.get(id=self.tag_2.pk)
        self.assertIsInstance(tag_1, Tag)
        self.assertIsInstance(tag_2, Tag)
        self.assertEqual(tag_1, self.tag_1)
        self.assertEqual(tag_2, self.tag_2)
        self.assertEqual(tag_1.posts.count(), 2)
        self.assertEqual(tag_2.posts.count(), 1)
        self.assertEqual(list(tags), [self.tag_1, self.tag_2])

    def test_view_sort_by_tag(self):
        post_3 = Post.objects.create(
            title='title 3', content='content 3', content_code='content code 3', user=self.user_1
        )
        post_3.tags.add(self.tag_2)
        post_3.save()
        response = self.client.get(f'/post/tag/{self.tag_1.pk}', {'pk': self.tag_1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts_content.html')
        self.assertIn('posts', response.context)
        posts = response.context['posts']
        self.assertIsInstance(posts, QuerySet)
        self.assertIn(self.post_1, posts)
        self.assertIn(self.post_2, posts)
        self.assertNotIn(post_3, posts)
        post_1 = posts.get(id=self.post_1.pk)
        post_2 = posts.get(id=self.post_2.pk)
        self.assertIsInstance(post_1, Post)
        self.assertIsInstance(post_2, Post)
        self.assertEqual(post_1, self.post_1)
        self.assertEqual(post_2, self.post_2)
        self.assertEqual(post_1.rating, 2)
        self.assertEqual(post_2.rating, -2)
        self.assertEqual(list(posts), [self.post_2, self.post_1])
        self.assertIn('tags', response.context)
        tags = response.context['tags']
        self.assertIsInstance(tags, QuerySet)
        self.assertIn(self.tag_1, tags)
        self.assertIn(self.tag_2, tags)
        tag_1 = tags.get(id=self.tag_1.pk)
        tag_2 = tags.get(id=self.tag_2.pk)
        self.assertIsInstance(tag_1, Tag)
        self.assertIsInstance(tag_2, Tag)
        self.assertEqual(tag_1, self.tag_1)
        self.assertEqual(tag_2, self.tag_2)
        self.assertEqual(tag_1.posts.count(), 2)
        self.assertEqual(tag_2.posts.count(), 2)

    def test_view_sort_by_date_week(self):
        self.post_1.create_at = dt.now(tz=pytz.UTC) - timedelta(29)
        self.post_2.create_at = dt.now(tz=pytz.UTC) - timedelta(6)
        self.post_1.save()
        self.post_2.save()
        response = self.client.get('/post/date/', {'button': 'week'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)
        posts = response.context['posts']
        self.assertIsInstance(posts, QuerySet)
        self.assertNotIn(self.post_1, posts)
        self.assertIn(self.post_2, posts)
        post_2 = posts.get(id=self.post_2.pk)
        self.assertIsInstance(post_2, Post)
        self.assertEqual(post_2, self.post_2)
        self.assertEqual(post_2.rating, -2)
        self.assertEqual(list(posts), [self.post_2])
        tags = response.context['tags']
        self.assertIsInstance(tags, QuerySet)
        self.assertIn(self.tag_1, tags)
        self.assertIn(self.tag_2, tags)
        tag_1 = tags.get(id=self.tag_1.pk)
        tag_2 = tags.get(id=self.tag_2.pk)
        self.assertIsInstance(tag_1, Tag)
        self.assertIsInstance(tag_2, Tag)
        self.assertEqual(tag_1, self.tag_1)
        self.assertEqual(tag_2, self.tag_2)
        self.assertEqual(tag_1.posts.count(), 2)
        self.assertEqual(tag_2.posts.count(), 1)
        self.assertEqual(list(tags), [self.tag_1, self.tag_2])

    def test_view_sort_by_date_month(self):
        self.post_1.create_at = dt.now(tz=pytz.UTC) - timedelta(29)
        self.post_2.create_at = dt.now(tz=pytz.UTC) - timedelta(6)
        self.post_1.save()
        self.post_2.save()
        response = self.client.get('/post/date/', {'button': 'month'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)
        posts = response.context['posts']
        self.assertIsInstance(posts, QuerySet)
        self.assertIn(self.post_1, posts)
        self.assertIn(self.post_2, posts)
        post_1 = posts.get(id=self.post_1.pk)
        post_2 = posts.get(id=self.post_2.pk)
        self.assertIsInstance(post_1, Post)
        self.assertIsInstance(post_2, Post)
        self.assertEqual(post_1, self.post_1)
        self.assertEqual(post_2, self.post_2)
        self.assertEqual(post_1.rating, 2)
        self.assertEqual(post_2.rating, -2)
        self.assertEqual(list(posts), [self.post_2, self.post_1])

    def test_view_sort_by_date_top(self):
        response = self.client.get('/post/date/', {'button': 'top'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)
        posts = response.context['posts']
        self.assertIsInstance(posts, QuerySet)
        self.assertIn(self.post_1, posts)
        self.assertIn(self.post_2, posts)
        post_1 = posts.get(id=self.post_1.pk)
        post_2 = posts.get(id=self.post_2.pk)
        self.assertIsInstance(post_1, Post)
        self.assertIsInstance(post_2, Post)
        self.assertEqual(post_1, self.post_1)
        self.assertEqual(post_2, self.post_2)
        self.assertEqual(post_1.rating, 2)
        self.assertEqual(post_2.rating, -2)
        self.assertEqual(list(posts), [self.post_1, self.post_2])

    def test_view_detail_get(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')
        self.assertIn('post', response.context)
        post_1 = response.context['post']
        self.assertIsInstance(post_1, Post)
        self.assertEqual(post_1, self.post_1)
        self.assertEqual(post_1.title, self.post_1.title)
        self.assertEqual(post_1.content, self.post_1.content)
        self.assertEqual(post_1.content_code, self.post_1.content_code)
        self.assertEqual(post_1.tags, self.post_1.tags)
        self.assertEqual(post_1.create_at, self.post_1.create_at)
        self.assertEqual(post_1.user, self.post_1.user)
        self.assertEqual(post_1.likes, self.post_1.likes)
        self.assertEqual(post_1.comments, self.post_1.comments)
        self.assertEqual(post_1.shows, self.post_1.shows)
        self.assertEqual(post_1.shows.count(), 2)
        self.assertIn('post_rating', response.context)
        post_rating = response.context['post_rating']
        self.assertEqual(post_rating, 2)
        self.assertIn('comments', response.context)
        comments = response.context['comments']
        self.assertIsInstance(comments, QuerySet)
        comment_1 = comments.get(id=self.comment_1.pk)
        comment_2 = comments.get(id=self.comment_2.pk)
        self.assertEqual(comment_1.comment, self.comment_1.comment)
        self.assertEqual(comment_1.user, self.comment_1.user)
        self.assertEqual(comment_1.create_at, self.comment_1.create_at)
        self.assertEqual(comment_2.comment, self.comment_2.comment)
        self.assertEqual(comment_2.user, self.comment_2.user)
        self.assertEqual(comment_2.create_at, self.comment_2.create_at)
        self.assertEqual(comment_1.rating, 1)
        self.assertEqual(comment_2.rating, None)
        self.assertEqual(list(comments), [self.comment_2, self.comment_1])
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CommentForm)
        self.assertIn('posts_by_tags', response.context)
        posts_by_tags = response.context['posts_by_tags']
        self.assertIsInstance(posts_by_tags, QuerySet)
        self.assertIn(self.post_2, posts_by_tags)
        self.assertNotIn(self.post_1, posts_by_tags)
        post_2 = posts_by_tags.get(id=self.post_2.pk)
        self.assertEqual(post_2.title, self.post_2.title)
        self.assertIn('liked_post_by_user', response.context)
        self.assertTrue(response.context['liked_post_by_user'])
        self.assertIn('comment_add_or_comment_like_by_user', response.context)
        comment_add_or_comment_like_by_user = response.context['comment_add_or_comment_like_by_user']
        self.assertIn(self.comment_1, comment_add_or_comment_like_by_user)
        comment_1 = comment_add_or_comment_like_by_user[0]
        self.assertEqual(comment_1.comment, self.comment_1.comment)
        self.assertEqual(comment_1.user, self.comment_1.user)
        self.assertEqual(comment_1.post, self.comment_1.post)
        self.assertEqual(self.post_1.shows.count(), post_1.shows.count())
        self.assertEqual(post_1.shows.count(), 2)

    def test_detail_view_get_without_tags(self):
        self.post_3 = Post.objects.create(
            title='title 3', content='content 3', content_code='content code 3', user=self.user_1
        )
        response = self.client.get(f'/post/{self.post_3.pk}', {'pk': self.post_3.pk})
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts_by_tags', response.context)
        self.assertFalse(response.context['posts_by_tags'])

    def test_detail_view_get_with_unique_tag(self):
        self.post_3 = Post.objects.create(
            title='title 3', content='content 3', content_code='content code 3', user=self.user_1
        )
        self.tag_3 = Tag.objects.create(title='tag 3')
        self.post_3.tags.add(self.tag_3)
        self.post_3.save()
        response = self.client.get(f'/post/{self.post_3.pk}', {'pk': self.post_3.pk})
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts_by_tags', response.context)
        self.assertFalse(response.context['posts_by_tags'])

    def test_detail_view_get_with_user_is_anonymous(self):
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertIn('liked_post_by_user', response.context)
        self.assertFalse(response.context['liked_post_by_user'])
        self.assertNotIn('comment_add_or_comment_like_by_user', response.context)
        post_1 = response.context['post']
        self.assertEqual(self.post_1, post_1)
        self.assertEqual(post_1.shows.count(), self.post_1.shows.count())
        self.assertEqual(post_1.shows.count(), 2)

    def test_detail_view_get_add_post_show_with_unique_auth_user(self):
        self.client.force_login(self.user_2)
        self.assertEqual(self.post_2.shows.count(), 1)
        response = self.client.get(f'/post/{self.post_2.pk}', {'pk': self.post_2.pk})
        self.assertEqual(response.status_code, 200)
        post_2 = response.context['post']
        self.assertEqual(self.post_2, post_2)
        self.assertEqual(post_2.shows.count(), self.post_2.shows.count())
        self.assertEqual(self.post_2.shows.count(), 2)
        self.assertEqual(self.post_2.shows.all()[1].user, self.user_2)
