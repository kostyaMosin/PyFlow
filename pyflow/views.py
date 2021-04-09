from django.db.models import Sum, Q
from django.shortcuts import render, redirect

from pyflow.forms import CommentForm, PostForm
from pyflow.models import Post, Comment, CommentLike, PostLike, Tag
from pyflow.tags_creator import tags_creator


def view_main(request):
    posts_content = []
    posts = Post.objects.filter()
    tags = Tag.objects.filter()
    for post in posts.order_by('-create_at'):
        rating = post.likes.aggregate(Sum('value'))['value__sum']
        post_rating = rating if rating else 0
        posts_content.append({
            'post': post,
            'post_rating': post_rating,
        })
    return render(request, 'index.html', {'posts_content': posts_content,
                                          'posts_popular': posts.order_by('-shows')[:5],
                                          'tags': tags,
                                          'tags_popular': tags.order_by('title')})


def view_detail(request, pk):
    if request.method == 'GET':
        post = Post.objects.get(id=pk)
        comments = []
        for comment in post.comments.all():
            comments.append({
                'comment': comment,
                'comment_rating': comment.likes.aggregate(Sum('value'))['value__sum'],
            })
        rating = post.likes.aggregate(Sum('value'))['value__sum']
        context = {
            'post': post,
            'post_rating': rating if rating else 0,
            'comments': comments,
            'form': CommentForm(),
            'post_by_tags': Post.objects.filter(Q(tags=post.tags.first())),
        }
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


def view_edit_post(request, pk):
    if request.method == 'GET':
        post = Post.objects.get(id=pk)
        context = {
            'form': PostForm,
            'post': post,
            'tags': f"#{'#'.join([tag.title for tag in post.tags.all()])}",
        }
        return render(request, 'edit_post.html', context)
    if request.method == 'POST':
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


def view_delete_post(request, pk):
    if request.method == 'POST':
        post = Post.objects.get(id=pk)
        post.delete()
        return redirect('index')


def view_delete_comment(request, pk):
    if request.method == 'POST':
        comment = Comment.objects.get(id=pk)
        post_pk = comment.post.pk
        comment.delete()
        return redirect('detail', post_pk)
