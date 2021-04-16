from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, F, Sum
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from pyflow.models import Post, Comment, Tag


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def view_user_profile(request):
    if request.user.is_authenticated:
        user = request.user
        posts = Post.objects.filter(user=user)
        comments = Comment.objects.filter(user=user)
        tags = Tag.objects.filter(posts__user=user).annotate(posts_count=Count(F('posts'))).order_by('-posts_count')
        posts_likes = posts.aggregate(likes=Sum(F('likes__value')))['likes']
        posts_likes = posts_likes if posts_likes else 0
        posts_shows = posts.aggregate(count=Count(F('shows')))['count']
        posts_shows = posts_shows if posts_shows else 0
        comments_likes = comments.aggregate(likes=Sum(F('likes__value')))['likes']
        comments_likes = comments_likes if comments_likes else 0
        context = {
            'user': user,
            'posts': posts.order_by('-create_at'),
            'comments': comments,
            'tags': tags,
            'reputation': sum([posts_likes, posts_shows, comments_likes]),
            'posts_shows': posts_shows,
            'posts_likes': posts_likes,
            'comments_likes': comments_likes,
        }

        posts_comment_by_user = []

        for post in Post.objects.all():
            if user_comments := post.comments.filter(user=user):
                posts_comment_by_user.append({'post': post, 'user_comments': user_comments})

        context['posts_comment_by_user'] = posts_comment_by_user

        return render(request, 'profile.html', context)
    return redirect('login')
