from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.db.models import QuerySet
import pytz
from datetime import datetime as dt, timedelta

from pyflow.forms import CommentForm, PostForm, SendEmailForm
from pyflow.models import Post, Tag, PostLike, PostShow, Comment, CommentLike
from pyflow.tags_creator import tags_creator, tags_to_string


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
        self.post_1.tags.add(self.tag_1)
        self.post_1.tags.add(self.tag_2)
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

    def test_view_sort_by_tag_404(self):
        response = self.client.get('/post/tag/33', {'pk': 33})
        self.assertEqual(response.status_code, 404)

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

    def test_view_detail_404(self):
        response = self.client.get('/post/33', {'pk': 33})
        self.assertEqual(response.status_code, 404)

    def test_detail_view_post(self):
        self.client.force_login(self.user_1)
        self.assertEqual(self.post_1.comments.count(), 2)
        comment = 'hello'
        response = self.client.post(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk, 'comment': comment})
        self.assertRedirects(response, f'/post/{self.post_1.pk}', 302, fetch_redirect_response=False)
        self.assertEqual(self.post_1.comments.count(), 3)
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        post_1 = response.context['post']
        self.assertEqual(post_1.comments.count(), 3)
        comments = response.context['comments']
        self.assertEqual(comments[0].comment, comment)
        self.assertEqual(comments[0].user, self.user_1)

    def test_detail_view_post_user_is_not_auth(self):
        comment = 'hello'
        response = self.client.post(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk, 'comment': comment})
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_detail_view_post_form_is_not_valid(self):
        self.client.force_login(self.user_1)
        comment = 'hello'
        response = self.client.post(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk, 'comment': comment})
        self.assertRedirects(response, f'/post/{self.post_1.pk}', 302, fetch_redirect_response=False)

    def test_create_post_view_get(self):
        self.client.force_login(self.user_1)
        response = self.client.get('/post/create/')
        self.assertTemplateUsed(response, 'create.html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_create_post_view_user_is_not_auth(self):
        response = self.client.get('/post/create/')
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_create_post_view_post(self):
        self.client.force_login(self.user_1)
        title = 'title 3'
        content = 'content 3'
        content_code = 'content code 3'
        tags = '#tag3'
        response = self.client.post('/post/create/', {'title': title,
                                                      'content': content,
                                                      'content_code': content_code,
                                                      'tags': tags,
                                                      'user': self.user_1})
        self.assertRedirects(response, '/post/3', 302, fetch_redirect_response=False)
        new_post = Post.objects.filter(title=title).first()
        self.assertIsInstance(new_post, Post)
        self.assertEqual(new_post.title, title)
        self.assertEqual(new_post.content, content)
        self.assertEqual(new_post.content_code, content_code)
        self.assertEqual(tags_to_string(new_post.tags.all()), tags)
        self.assertEqual(new_post.user, self.user_1)
        tag = Tag.objects.get(title='tag3')
        self.assertIsInstance(tag, Tag)
        self.assertEqual(tag.title, tags_creator(tags)[0].title)

    def test_create_post_view_post_form_is_not_valid(self):
        self.client.force_login(self.user_1)
        title = 'title 3'
        content = 'content 3'
        content_code = 'content code 3'
        response = self.client.post('/post/create/', {'title': title,
                                                      'content': content,
                                                      'content_code': content_code,
                                                      'user': self.user_1})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create.html')
        self.assertIn('form', response.context)

    def test_add_like_or_dislike_value_post_method_user_is_not_auth(self):
        response = self.client.post(f'/rating/post/{self.post_1.pk}', {'obj_type': 'post',
                                                                       'pk': self.post_1.pk,
                                                                       'button': 'like'})
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_add_like_or_dislike_value_get_method_user_is_not_auth(self):
        response = self.client.get(f'/rating/post/{self.post_1.pk}')
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_add_like_value_post_method_with_obj_type_comment(self):
        user_3 = User.objects.create_user(username='user3')
        self.client.force_login(user_3)
        obj_type = 'comment'
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        comments = response.context['comments']
        comment_1_in = comments.get(id=self.comment_1.pk)
        self.assertEqual(comment_1_in.likes.count(), 1)
        self.assertEqual(comment_1_in.rating, 1)
        response = self.client.post(f'/rating/{obj_type}/{self.comment_1.pk}', {'obj_type': obj_type,
                                                                                'pk': self.comment_1,
                                                                                'button': 'like'})
        self.assertRedirects(response, f'/post/{self.post_1.pk}', 302, fetch_redirect_response=False)
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        comments = response.context['comments']
        comment_1_out = comments.get(id=self.comment_1.pk)
        self.assertEqual(comment_1_out.likes.count(), 2)
        self.assertEqual(comment_1_out.rating, 2)
        self.assertEqual(comment_1_out.likes.all()[1].user, user_3)
        self.assertEqual(comment_1_in.comment, self.comment_1.comment)
        self.assertEqual(comment_1_out.comment, self.comment_1.comment)

    def test_add_dislike_value_post_method_with_obj_type_comment(self):
        user_3 = User.objects.create_user(username='user3')
        self.client.force_login(user_3)
        obj_type = 'comment'
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        comments = response.context['comments']
        comment_1_in = comments.get(id=self.comment_1.pk)
        self.assertEqual(comment_1_in.likes.count(), 1)
        self.assertEqual(comment_1_in.rating, 1)
        response = self.client.post(f'/rating/{obj_type}/{self.comment_1.pk}', {'obj_type': obj_type,
                                                                                'pk': self.comment_1,
                                                                                'button': 'dislike'})
        self.assertRedirects(response, f'/post/{self.post_1.pk}', 302, fetch_redirect_response=False)
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        comments = response.context['comments']
        comment_1_out = comments.get(id=self.comment_1.pk)
        self.assertEqual(comment_1_out.likes.count(), 2)
        self.assertEqual(comment_1_out.rating, 0)
        self.assertEqual(comment_1_out.likes.all()[1].user, user_3)
        self.assertEqual(comment_1_in.comment, self.comment_1.comment)
        self.assertEqual(comment_1_out.comment, self.comment_1.comment)

    def test_add_like_or_dislike_value_with_obj_type_comment_404(self):
        self.client.force_login(self.user_1)
        response = self.client.post('/rating/comment/33', {'obj_type': 'comment',
                                                            'pk': 33,
                                                            'button': 'like'})
        self.assertEqual(response.status_code, 404)

    def test_add_like_value_post_method_with_obj_type_post(self):
        user_3 = User.objects.create_user(username='user3')
        self.client.force_login(user_3)
        obj_type = 'post'
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        post_1_in = response.context['post']
        post_1_in_rating = response.context['post_rating']
        self.assertEqual(post_1_in.likes.count(), 2)
        self.assertEqual(post_1_in_rating, 2)
        response = self.client.post(f'/rating/{obj_type}/{self.post_1.pk}', {'obj_type': obj_type,
                                                                             'pk': self.post_1,
                                                                             'button': 'like'})
        self.assertRedirects(response, f'/post/{self.post_1.pk}', 302, fetch_redirect_response=False)
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        post_1_out = response.context['post']
        post_1_out_rating = response.context['post_rating']
        self.assertEqual(post_1_out.likes.count(), 3)
        self.assertEqual(post_1_out_rating, 3)
        self.assertEqual(post_1_out.likes.all()[2].user, user_3)
        self.assertEqual(post_1_in.title, self.post_1.title)
        self.assertEqual(post_1_out.title, self.post_1.title)

    def test_add_dislike_value_post_method_with_obj_type_post(self):
        user_3 = User.objects.create_user(username='user3')
        self.client.force_login(user_3)
        obj_type = 'post'
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        post_1_in = response.context['post']
        post_1_in_rating = response.context['post_rating']
        self.assertEqual(post_1_in.likes.count(), 2)
        self.assertEqual(post_1_in_rating, 2)
        response = self.client.post(f'/rating/{obj_type}/{self.post_1.pk}', {'obj_type': obj_type,
                                                                             'pk': self.post_1,
                                                                             'button': 'dislike'})
        self.assertRedirects(response, f'/post/{self.post_1.pk}', 302, fetch_redirect_response=False)
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        post_1_out = response.context['post']
        post_1_out_rating = response.context['post_rating']
        self.assertEqual(post_1_out.likes.count(), 3)
        self.assertEqual(post_1_out_rating, 1)
        self.assertEqual(post_1_out.likes.all()[2].user, user_3)
        self.assertEqual(post_1_in.title, self.post_1.title)
        self.assertEqual(post_1_out.title, self.post_1.title)

    def test_add_like_or_dislike_value_with_obj_type_post_404(self):
        self.client.force_login(self.user_1)
        response = self.client.post('/rating/post/33', {'obj_type': 'post',
                                                         'pk': 33,
                                                         'button': 'like'})
        self.assertEqual(response.status_code, 404)

    def test_edit_delete_post_view_get_method_user_is_not_auth(self):
        response = self.client.get('/post/edit/1', {'pk': self.post_1.pk})
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_edit_delete_post_view_post_method_user_is_not_auth(self):
        response = self.client.post('/post/edit/1', {'pk': self.post_1.pk,
                                                     'button': 'save'})
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_edit_post_view_get_method(self):
        self.client.force_login(self.user_1)
        response = self.client.get('/post/edit/1', {'pk': self.post_1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIn('post', response.context)
        post_1 = response.context['post']
        self.assertIsInstance(post_1, Post)
        self.assertEqual(post_1.title, self.post_1.title)
        self.assertEqual(post_1.content, self.post_1.content)
        self.assertEqual(post_1.content_code, self.post_1.content_code)
        tags = response.context['tags']
        self.assertEqual(tags, tags_to_string(self.post_1.tags.all()))

    def test_edit_post_view_post_method_with_button_is_delete(self):
        self.client.force_login(self.user_1)
        response = self.client.post(f'/post/edit/{self.post_1.pk}', {'pk': self.post_1.pk,
                                                                     'button': 'delete'})
        self.assertRedirects(response, '/', 302, fetch_redirect_response=False)
        posts = Post.objects.all()
        self.assertNotIn(self.post_1, posts)
        response = self.client.get('/')
        posts = response.context['posts']
        self.assertIsInstance(posts, QuerySet)
        self.assertNotIn(self.post_1, posts)

    def test_edit_post_view_post_method_with_button_is_save(self):
        self.client.force_login(self.user_1)
        post_1_in = self.post_1
        tag = self.post_1.tags.all()[0].title
        title = 'title'
        content = 'content'
        content_code = 'content_code'
        tags = '#tag3'
        response = self.client.post(f'/post/edit/{self.post_1.pk}', {'pk': self.post_1.pk,
                                                                     'button': 'save',
                                                                     'title': title,
                                                                     'content': content,
                                                                     'content_code': content_code,
                                                                     'tags': tags})
        self.assertRedirects(response, f'/post/{self.post_1.pk}', 302, fetch_redirect_response=False)
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        post_1_out = response.context['post']
        self.assertEqual(post_1_out.title, title)
        self.assertEqual(post_1_out.content, content)
        self.assertEqual(post_1_out.content_code, content_code)
        self.assertEqual(tags_to_string(post_1_out.tags.all()), tags)
        self.assertNotEqual(post_1_in.title, post_1_out.title)
        self.assertNotEqual(post_1_in.content, post_1_out.content)
        self.assertNotEqual(post_1_in.content_code, post_1_out.content_code)
        self.assertNotEqual(tag, post_1_out.tags.all()[0].title)

    def test_edit_post_view_post_method_form_is_not_valid(self):
        self.client.force_login(self.user_1)
        content = 'content'
        content_code = 'content_code'
        tags = '#tag3'
        response = self.client.post(f'/post/edit/{self.post_1.pk}', {'pk': self.post_1.pk,
                                                                     'button': 'save',
                                                                     'content': content,
                                                                     'content_code': content_code,
                                                                     'tags': tags})
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        post_1 = response.context['post']
        self.assertIsInstance(post_1, Post)
        self.assertEqual(post_1.title, self.post_1.title)
        self.assertEqual(post_1.content, self.post_1.content)
        self.assertEqual(post_1.content_code, self.post_1.content_code)
        self.assertEqual(tags_to_string(post_1.tags.all()), tags_to_string(self.post_1.tags.all()))
        tags = response.context['tags']
        self.assertEqual(tags, tags_to_string(self.post_1.tags.all()))

    def test_edit_or_delete_post_view_404(self):
        self.client.force_login(self.user_1)
        response = self.client.post('/post/edit/33', {'pk': 33,
                                                       'button': 'save',
                                                       'content': 'content',
                                                       'content_code': 'content_code',
                                                       'tags': 'tags'})
        self.assertEqual(response.status_code, 404)

    def test_send_post_by_email_view_with_user_is_not_auth(self):
        response = self.client.get('/send_post/1', {'pk': 1})
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_send_post_by_email_view_get_method(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f'/send_post/{self.post_1.pk}', {'pk': self.post_1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'send_post.html')
        self.assertIn('send_form', response.context)
        self.assertIsInstance(response.context['send_form'], SendEmailForm)
        self.assertIn('post', response.context)
        post_1 = response.context['post']
        self.assertIsInstance(post_1, Post)
        self.assertEqual(post_1, self.post_1)
        self.assertEqual(post_1.title, self.post_1.title)

    def test_send_post_by_email_view_post_method(self):
        self.client.force_login(self.user_1)
        receiver = 'from@example.com'
        topic = 'topic'
        response = self.client.post(f'/send_post/{self.post_1.pk}', {'pk': self.post_1.pk,
                                                                     'receiver': receiver,
                                                                     'topic': topic})
        self.assertRedirects(response, f'/post/{self.post_1.pk}', 302, fetch_redirect_response=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, topic)

    def test_send_post_by_email_view_404(self):
        self.client.force_login(self.user_1)
        response = self.client.post('/send_post/33', {'pk': 33,
                                                      'receiver': 'receiver',
                                                      'topic': 'topic'})
        self.assertEqual(response.status_code, 404)

    def test_send_post_by_email_view_post_method_form_is_not_valid(self):
        self.client.force_login(self.user_1)
        topic = 'topic'
        response = self.client.post(f'/send_post/{self.post_1.pk}', {'pk': self.post_1.pk,
                                                                     'topic': topic})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], SendEmailForm)
        self.assertIn('post', response.context)
        self.assertIsInstance(response.context['post'], Post)

    def test_delete_comment_with_user_is_not_auth(self):
        response = self.client.post('/comment/delete/1', {'pk': 1})
        self.assertRedirects(response, '/accounts/login/', 302, fetch_redirect_response=False)

    def test_delete_comment_get(self):
        self.client.force_login(self.user_1)
        response = self.client.get('/comment/delete/1', {'pk': 1})
        self.assertRedirects(response, '/', 302, fetch_redirect_response=False)

    def test_delete_comment_post(self):
        self.client.force_login(self.user_1)
        response = self.client.post(f'/comment/delete/{self.comment_1.pk}', {'pk': self.comment_1.pk})
        self.assertRedirects(response, f'/post/{self.comment_1.post.pk}', 302, fetch_redirect_response=False)
        comments = Comment.objects.all()
        self.assertNotIn(self.comment_1, comments)
        response = self.client.get(f'/post/{self.post_1.pk}', {'pk': self.post_1.pk})
        self.assertIn('comments', response.context)
        comments = response.context['comments']
        self.assertNotIn(self.comment_1, comments)

    def test_delete_comment_404(self):
        self.client.force_login(self.user_1)
        response = self.client.post(f'/comment/delete/33', {'pk': 33})
        self.assertEqual(response.status_code, 404)

    def test_search_posts_view_get(self):
        kw_1 = self.post_1.title
        kw_2 = self.post_2.content
        key_words = f'{kw_1[3:]} {kw_2[2:]}'
        response = self.client.get('/search/', {'q': key_words})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts_content.html')
        self.assertIn('posts', response.context)
        posts = response.context['posts']
        self.assertIsInstance(posts, QuerySet)
        self.assertIn(self.post_1, posts)
        self.assertIn(self.post_1, posts)
        self.assertEqual(len(posts), 2)
        post_1 = posts.get(id=self.post_1.pk)
        post_2 = posts.get(id=self.post_2.pk)
        self.assertEqual(post_1, self.post_1)
        self.assertEqual(post_2, self.post_2)
        self.assertEqual(post_1.title, kw_1)
        self.assertEqual(post_2.content, kw_2)

    def test_search_posts_view_post(self):
        response = self.client.post('/search/', {'q': 'qqq'})
        self.assertRedirects(response, '/', 302, fetch_redirect_response=False)
