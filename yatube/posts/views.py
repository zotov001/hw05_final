from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from . import utils
from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow


LIMIT_POSTS_ON_PAGE: int = 10


@cache_page(20, cache='default', key_prefix='index_page')
def index(request):
    """Все посты, разбивает по LIMIT_POSTS_ON_PAGE штук на странице"""
    post_list = Post.objects.select_related('author', 'group')
    return render(
        request, 'posts/index.html', {
            'page_obj': utils.paginator(request, post_list),
        }
    )


def group_posts(request, slug):
    """Посты группы, разбивает по LIMIT_POSTS_ON_PAGE штук на странице."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'page_obj': utils.paginator(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Посты автора, разбивает по LIMIT_POSTS_ON_PAGE штук на странице."""
    author = User.objects.get(username=username)
    post_list = author.posts.all()
    post_count = post_list.count()
    following = True
    if request.user.id is not None:
        user = request.user
        follower = Follow.objects.filter(user=user, author=author)
        if user != author and not follower.exists():
            following = False
        else:
            following = True
    context = {
        'author': author,
        'page_obj': utils.paginator(request, post_list),
        'posts_count': post_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводит определенный пост и инф о нем."""
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': CommentForm(request.POST or None),
        'comments': post.comments.all()
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request, is_edit=False):
    """Создание нового поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, "posts/create_post.html", {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect('posts:profile', request.user.username)
    context = {
        'form': form,
        'is_edit': True
    }
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Посты авторов подписка"""
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': utils.paginator(request, posts),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка"""
    user = request.user
    author = User.objects.get(username=username)
    follower = Follow.objects.filter(user=user, author=author)
    if user != author and not follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка"""
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=author)
