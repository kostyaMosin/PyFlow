from django.core.mail import send_mail
from django.db.models import Sum, Q, Count, F
from django.shortcuts import render, redirect
from datetime import datetime as dt, timedelta

from django.template import loader

from pyflow.forms import CommentForm, PostForm, SendEmailForm
from pyflow.models import Post, Comment, CommentLike, PostLike, Tag, PostShow
from pyflow.tags_creator import tags_creator
from src import settings


def view_main(request):
    posts = Post.objects.filter()
    tags = Tag.objects.filter()
    return render(request, 'index.html', {
        'posts': posts.annotate(rating=Sum(F('likes__value'))).order_by('-create_at'),
        'posts_popular': posts.annotate(shows_count=Count(F('shows'))).order_by('-shows_count')[:5],
        'tags': tags.annotate(tag_posts=Count(F('posts'))).order_by('-tag_posts')[:10],
    })


def view_sort_by_tag(request, pk):
    tag = Tag.objects.get(id=pk)
    posts = Post.objects.filter(tags=tag)
    tags = Tag.objects.filter()
    return render(request, 'sort_posts_by_tag.html', {
        'posts': posts.annotate(rating=Sum(F('likes__value'))).order_by('-create_at'),
        'tags': tags.annotate(tag_posts=Count(F('posts'))).order_by('-tag_posts')[:10],
    })


def view_sort_by_date(request):
    if request.method == 'GET':
        button = request.GET['button']
        posts = Post.objects.filter()
        time = dt.now()
        if button == 'week':
            time = dt.now() - timedelta(days=7)
        if button == 'month':
            time = dt.now() - timedelta(days=30)
        posts_sorted = posts.filter(create_at__gt=time).annotate(rating=Sum(F('likes__value'))).order_by('-create_at')
        if button == 'top':
            posts_sorted = posts.annotate(rating=Sum(F('likes__value'))).order_by('-rating')
        tags = Tag.objects.filter()
        return render(request, 'sort_posts_by_date.html', {
            'posts': posts_sorted,
            'tags': tags.annotate(tag_posts=Count(F('posts'))).order_by('-tag_posts'),
        })


def view_detail(request, pk):
    if request.method == 'GET':
        post = Post.objects.get(id=pk)
        comments = Comment.objects.filter(post=post)
        rating = post.likes.aggregate(Sum('value'))['value__sum']
        context = {
            'post': post,
            'post_rating': rating if rating else 0,
            'comments': comments.annotate(rating=Sum(F('likes__value'))).order_by('-create_at'),
            'form': CommentForm(),
            'post_by_tags': Post.objects.exclude(id=post.pk).filter(
                Q(tags=post.tags.all()[0]) | Q(tags=post.tags.all()[1])),
        }
        PostShow.objects.create(post=post)
        return render(request, 'detail.html', context)
    if request.method == 'POST':
        post = Post.objects.get(id=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            comment = cd['comment']
            Comment.objects.create(comment=comment, post=post)
            return redirect('detail', post.pk)


def view_create_post(request):
    if request.method == 'GET':
        context = {
            'form': PostForm(),
        }
        return render(request, 'create.html', context)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            data = {
                'title': cd['title'],
                'content': cd['content'],
                'content_code': cd['content_code'],
            }
            post = Post.objects.create(**data)
            post.tags.set(tags_creator(cd['tags']))
            post.save()
            return redirect('detail', post.pk)


def view_add_like_or_dislike_value(request, obj_type, pk):
    if request.method == 'POST':
        button = request.POST['button']
        value = 1 if button == 'like' else -1
        if obj_type == 'comment':
            comment = Comment.objects.get(id=pk)
            data = {
                'value': value,
                'comment': comment,
            }
            CommentLike.objects.create(**data)
            post_pk = comment.post.pk
        if obj_type == 'post':
            data = {
                'value': value,
                'post': Post.objects.get(id=pk),
            }
            PostLike.objects.create(**data)
            post_pk = pk
        return redirect('detail', post_pk)


def view_edit_delete_post(request, pk):
    if request.method == 'GET':
        post = Post.objects.get(id=pk)
        context = {
            'form': PostForm,
            'post': post,
            'tags': f"#{' #'.join([tag.title for tag in post.tags.all()])}",
        }
        return render(request, 'edit.html', context)
    if request.method == 'POST':
        if request.POST['button'] == 'Удалить пост':
            post = Post.objects.get(id=pk)
            post.delete()
            return redirect('index')
        if request.POST['button'] == 'Сохранить пост':
            form = PostForm(request.POST)
            post = Post.objects.get(id=pk)
            if form.is_valid():
                cd = form.cleaned_data
                post.title = cd['title']
                post.content = cd['content']
                post.content_code = cd['content_code']
                post.tags.set(tags_creator(cd['tags']))
                post.save()
                return redirect('detail', post.pk)


def view_delete_comment(request, pk):
    if request.method == 'POST':
        comment = Comment.objects.get(id=pk)
        post_pk = comment.post.pk
        comment.delete()
        return redirect('detail', post_pk)


def view_send_post(request, pk):
    if request.method == 'GET':
        context = {
            'send_form': SendEmailForm(),
            'post': Post.objects.get(id=pk)
        }
        return render(request, 'send_post.html', context)
    else:
        form = SendEmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            html_message = loader.render_to_string(
                'email.html', {'post': Post.objects.get(id=pk)},
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
