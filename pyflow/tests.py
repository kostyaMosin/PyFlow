from django.contrib.auth.models import User
from django.test import TestCase
from django.db.models import QuerySet

from pyflow.models import Post, Tag, PostLike, PostShow


class ViewTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(username='user1')
        self.user_2 = User.objects.create_user(username='user2')
        self.tag_1 = Tag.objects.create(title='tag 1')
        self.tag_2 = Tag.objects.create(title='tag 2')
        self.post_1 = Post.objects.create(
            title='title 1',
            content='content 1',
            content_code='content code 1',
            user=self.user_1
        )
        self.post_2 = Post.objects.create(
            title='title 2',
            content='content 2',
            content_code='content code 2',
            user=self.user_1
        )
        self.post_1.tags.set(Tag.objects.filter())
        self.post_2.tags.add(self.tag_1)
        self.post_1_like_1 = PostLike.objects.create(value=1, post=self.post_1, user=self.user_1)
        self.post_1_like_2 = PostLike.objects.create(value=1, post=self.post_1, user=self.user_2)
        self.post_2_like_1 = PostLike.objects.create(value=-1, post=self.post_2, user=self.user_1)
        self.post_2_like_2 = PostLike.objects.create(value=-1, post=self.post_2, user=self.user_2)
        self.post_1_show_1 = PostShow.objects.create(post=self.post_1, user=self.user_1)
        self.post_1_show_2 = PostShow.objects.create(post=self.post_1, user=self.user_2)
        self.post_2_show_1 = PostShow.objects.create(post=self.post_2, user=self.user_1)

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
        tag_1, tag_2 = tags
        self.assertIsInstance(tag_1, Tag)
        self.assertIsInstance(tag_2, Tag)
        self.assertEqual(tag_1, self.tag_1)
        self.assertEqual(tag_2, self.tag_2)
        self.assertEqual(tag_1.posts.count(), 2)
        self.assertEqual(tag_2.posts.count(), 1)
