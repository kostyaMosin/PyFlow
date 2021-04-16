from django.core.mail import send_mail
from django.db.models import Sum, Count, F, Q
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime as dt, timedelta
import pytz

from django.template import loader

from pyflow.forms import CommentForm, PostForm, SendEmailForm
from pyflow.models import Post, Comment, CommentLike, PostLike, Tag, PostShow
from pyflow.tags_creator import tags_creator, tags_to_string
from src import settings


def view_main(request):
    posts = Post.objects.filter()
    tags = Tag.objects.filter()
    context = {
        'posts': posts.annotate(rating=Sum(F('likes__value'))).order_by('-create_at'),
        'posts_popular': posts.annotate(shows_count=Count(F('shows'))).order_by('-shows_count')[:5],
        'tags': tags.annotate(tag_posts=Count(F('posts'))).order_by('-tag_posts'),
    }
    return render(request, 'index.html', context)


def view_sort_by_tag(request, pk):
    tag = get_object_or_404(Tag, id=pk)
    posts = Post.objects.filter(tags=tag)
    tags = Tag.objects.filter()
    context = {
        'posts': posts.annotate(rating=Sum(F('likes__value'))).order_by('-create_at'),
        'tags': tags.annotate(tag_posts=Count(F('posts'))).order_by('-tag_posts'),
    }
    return render(request, 'posts_content.html', context)


def view_sort_by_date(request):
    if request.method == 'GET':
        button = request.GET['button']
        posts = Post.objects.filter()
        time = dt.now(tz=pytz.UTC)
        if button == 'week':
            time = time - timedelta(7)
        if button == 'month':
            time = time - timedelta(30)
        posts_sorted = posts.filter(create_at__gt=time).annotate(rating=Sum(F('likes__value'))).order_by('-create_at')
        if button == 'top':
            posts_sorted = posts.annotate(rating=Sum(F('likes__value'))).order_by('-rating')
        tags = Tag.objects.filter()
        context = {
            'posts': posts_sorted,
            'tags': tags.annotate(tag_posts=Count(F('posts'))).order_by('-tag_posts'),
        }
        return render(request, 'posts_content.html', context)


def view_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    tags = post.tags.all()
    if request.method == 'GET':
        comments = post.comments
        rating = post.likes.aggregate(Sum('value'))['value__sum']
        posts = Post.objects.exclude(id=post.pk).filter(tags=tags.first())
        for tag in tags:
            if posts_sort := posts.filter(tags=tag):
                posts = posts_sort
            else:
                break
        context = {
            'post': post,
            'post_rating': rating if rating else 0,
            'comments': comments.annotate(rating=Sum(F('likes__value'))).order_by('create_at'),
            'form': CommentForm(),
            'posts_by_tags': posts,
            'liked_post_by_user': False,
        }
        if comment_error := request.session.get('errors'):
            context['errors'] = comment_error['comment']
        if request.user.is_authenticated:
            user = request.user
            if post.likes.filter(user=user):
                context['liked_post_by_user'] = True
            context['comment_add_or_comment_like_by_user'] = list(comments.filter(user=user))
            for comment in comments.all():
                if comment.likes.filter(user=user):
                    context['comment_add_or_comment_like_by_user'].append(comment)
            if not post.shows.filter(user=user):
                PostShow.objects.create(post=post, user=user)
        return render(request, 'detail.html', context)
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                comment = cd['comment']
                Comment.objects.create(comment=comment, post=post, user=request.user)
                return redirect('detail', post.pk)
            request.session['errors'] = form.errors
            return redirect('detail', post.pk)
        return redirect('login')


def view_create_post(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            context = {
                'form': PostForm(),
            }
            return render(request, 'create.html', context)
        if request.method == 'POST':
            form = PostForm(request.POST)
            user = request.user
            if form.is_valid():
                cd = form.cleaned_data
                data = {
                    'title': cd['title'],
                    'content': cd['content'],
                    'content_code': cd['content_code'],
                    'user': user,
                }
                post = Post.objects.create(**data)
                post.tags.set(tags_creator(cd['tags']))
                post.save()
                return redirect('detail', post.pk)
            context = {'form': form}
            return render(request, 'create.html', context)
    return redirect('login')


def view_add_like_or_dislike_value(request, obj_type, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            post_pk = pk
            user = request.user
            button = request.POST['button']
            value = 1 if button == 'like' else -1
            if obj_type == 'comment':
                comment = get_object_or_404(Comment, id=pk)
                data = {
                    'value': value,
                    'comment': comment,
                    'user': user,
                }
                CommentLike.objects.create(**data)
                post_pk = comment.post.pk
            if obj_type == 'post':
                data = {
                    'value': value,
                    'post': get_object_or_404(Post, id=post_pk),
                    'user': user,
                }
                PostLike.objects.create(**data)
            return redirect('detail', post_pk)
        if request.method == 'GET':
            return redirect('index')
    return redirect('login')


def view_edit_delete_post(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=pk)
        tags = tags_to_string(post.tags.all())
        if request.method == 'GET':
            context = {
                'form': PostForm(),
                'post': post,
                'tags': tags,
            }
            return render(request, 'edit.html', context)
        if request.method == 'POST':
            if request.POST['button'] == 'delete':
                post.delete()
                return redirect('index')
            if request.POST['button'] == 'save':
                form = PostForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    post.title = cd['title']
                    post.content = cd['content']
                    post.content_code = cd['content_code']
                    post.tags.set(tags_creator(cd['tags']))
                    post.save()
                    return redirect('detail', post.pk)
                context = {
                    'form': form,
                    'post': post,
                    'tags': tags
                }
                return render(request, 'edit.html', context)
    return redirect('login')


def view_delete_comment(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment = get_object_or_404(Comment, id=pk)
            post_pk = comment.post.pk
            comment.delete()
            return redirect('detail', post_pk)
        return redirect('index')
    return redirect('login')


def view_send_post_by_email(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=pk)
        if request.method == 'GET':
            context = {
                'send_form': SendEmailForm(),
                'post': post
            }
            return render(request, 'send_post.html', context)
        if request.method == 'POST':
            form = SendEmailForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                html_message = loader.render_to_string(
                    'email.html', {'post': post},
                )
                send_mail(
                    subject=cd['topic'],
                    message='',
                    html_message=html_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[cd['receiver']],
                    fail_silently=False,
                )
                return redirect('detail', pk)
            context = {
                'form': form,
                'post': post
            }
            return render(request, 'send_post.html', context)
    return redirect('login')


def view_search_posts(request):
    if request.method == 'GET':
        key_words = request.GET.get('q').strip().split(' ')
        posts = Post.objects.filter()
        posts_query = Post.objects.none()
        for kw in key_words:
            posts_query |= posts.filter(Q(title__icontains=kw) | Q(content__icontains=kw))
        tags = Tag.objects.filter()
        context = {
            'posts': posts_query.annotate(rating=Sum(F('likes__value'))).order_by('-create_at'),
            'tags': tags.annotate(tag_posts=Count(F('posts'))).order_by('-tag_posts'),
        }
        return render(request, 'posts_content.html', context)
    return redirect('index')
