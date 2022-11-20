from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from .utils import page_paginator
from django.views.decorators.cache import cache_page


@cache_page(60 * 15)
def index(request):
    post_list = Post.objects.all()
    title = "Последние обновления на сайте"
    page_obj = page_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    # Получаю объект класса групп
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    page_obj = page_paginator(request, posts)
    title = f"Последние {posts.count()} поста группы {slug}"
    context = {
        'page_obj': page_obj,
        'group': group,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    following = Follow.objects.filter(author=author).exists()
    print(following)
    # Не совсем понял про related_name ведь его нет в модели Post
    # и что именно нужно передать в него
    name = author.get_full_name()
    title = f"Профайл пользователя {name}"
    context = {
        'page_obj': page_paginator(request, post_list),
        'title': title,
        'author': author,
        'count': post_list.count(),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post = get_object_or_404(Post, id=post_id)
    total_author_posts = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments_list = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'total_posts': total_author_posts,
        'form': form,
        'comments': comments_list
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    username = request.user.username
    form = PostForm(files=request.FILES or None)
    context = {
        'title': 'Новый пост',
        'form': form,
    }
    if request.method == "POST":
        form = PostForm(request.POST,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=username)
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    username = request.user
    post = Post.objects.filter(author__following__user=username)
    post_obj = page_paginator(request, post)
    context = {
        'page_obj': post_obj,
        'title': "Мои подписки",
    }
    return render(
        request,
        "posts/follow.html", context
    )


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        author = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username=username)
