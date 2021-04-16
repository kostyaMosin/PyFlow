from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.test import TestCase

from pyflow.models import Tag, Post, PostLike, PostShow, Comment, CommentLike


class ViewTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(username='user1')
        self.user_2 = User.objects.create_user(username='user2')
        self.tag_1 = Tag.objects.create(title='tag1')
        self.tag_2 = Tag.objects.create(title='tag2')
        self.post_1 = Post.objects.create(
            title='title1', content='content1', content_code='content_code1', user=self.user_1
        )
        self.post_2 = Post.objects.create(
            title='title2', content='content2', content_code='content_code2', user=self.user_1
        )
        self.post_1.tags.set(Tag.objects.all())
        self.post_2.tags.set(Tag.objects.all())
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
        self.comment_1_like_1 = CommentLike.objects.create(value=1, comment=self.comment_1, user=self.user_2)

    def test_view_user_profile_user_is_not_auth(self):
        response = self.client.get('/accounts/profile/')
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_view_user_profile_get(self):
        self.client.force_login(self.user_1)
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertIn('user', response.context)
        self.assertIn('posts', response.context)
        self.assertIn('comments', response.context)
        self.assertIn('tags', response.context)
        self.assertIn('reputation', response.context)
        self.assertIn('posts_shows', response.context)
        self.assertIn('posts_likes', response.context)
        self.assertIn('comments_likes', response.context)
        user = response.context['user']
        posts = response.context['posts']
        comments = response.context['comments']
        tags = response.context['tags']
        reputation = response.context['reputation']
        posts_shows = response.context['posts_shows']
        posts_likes = response.context['posts_likes']
        comments_likes = response.context['comments_likes']
        self.assertIsInstance(user, User)
        self.assertEqual(user, self.user_1)
        self.assertEqual(user.username, self.user_1.username)
        self.assertIsInstance(posts, QuerySet)
        self.assertIn(self.post_1, posts)
        self.assertIn(self.post_2, posts)
        self.assertEqual(list(posts), [self.post_2, self.post_1])
        self.assertEqual(len(posts), 2)
        post_1 = posts.all()[1]
        self.assertEqual(post_1.title, self.post_1.title)
        self.assertEqual(post_1.content, self.post_1.content)
        self.assertEqual(post_1.content_code, self.post_1.content_code)
        self.assertEqual(post_1.tags, self.post_1.tags)
        self.assertEqual(post_1.create_at, self.post_1.create_at)
        self.assertEqual(post_1.user, self.post_1.user)
        self.assertIsInstance(comments, QuerySet)
        self.assertIn(self.comment_1, comments)
        self.assertEqual(len(comments), 1)
        self.assertIsInstance(tags, QuerySet)
        self.assertIn(self.tag_1, tags)
        self.assertIn(self.tag_2, tags)
        self.assertEqual(tags.count(), 2)
        self.assertIsInstance(reputation, int)
        self.assertEqual(reputation, 4)
        self.assertEqual(sum([posts_shows, posts_likes, comments_likes]), 4)
        self.assertIsInstance(posts_shows, int)
        self.assertEqual(posts_shows, 3)
        self.assertIsInstance(posts_likes, int)
        self.assertEqual(posts_likes, 0)
        self.assertIsInstance(comments_likes, int)
        self.assertEqual(comments_likes, 1)

