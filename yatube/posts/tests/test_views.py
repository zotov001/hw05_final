import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

NUM_OF_POST = 0
NUM_POSTS_LAST_PAGE = 3
NUM_POSTS_FIRST_PAGE = 10


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.author_f = User.objects.create_user(username='author_follow')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
                image=cls.uploaded,
            )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый коммент',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author_f,
        )
        cls.index = ('posts/index.html', 'posts:index', None)
        cls.group_list = (
            'posts/group_list.html', 'posts:group_list',
            {'slug': cls.group.slug}
        )
        cls.profile = (
            'posts/profile.html', 'posts:profile',
            {'username': cls.user}
        )
        cls.post_detail = (
            'posts/post_detail.html', 'posts:post_detail',
            {'post_id': cls.post.id}
        )
        cls.create = (
            'posts/create_post.html', 'posts:post_create', None)
        cls.post_edit = (
            'posts/create_post.html', 'posts:post_edit',
            {'post_id': cls.post.id}
        )
        cls.follow_index = ('posts/follow.html', 'posts:follow_index', None)
        cls.follow = ('posts:profile_follow', None)
        cls.unfollow = ('posts:profile_unfollow', None)
        cls.templates_pages_for_authorized = (
            cls.index,
            cls.group_list,
            cls.profile,
            cls.post_detail,
            cls.create
        )
        cls.templates_for_paginator = (
            cls.index,
            cls.group_list,
            cls.profile
        )
        cls.templates_pages_for_image = (
            cls.index,
            cls.group_list,
            cls.profile,
            cls.post_detail
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_1 = User.objects.create_user(username='user1')
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user_1)

    def template_test(self, test_post):
        """Общие тесты для проверки отображения."""
        self.assertEqual(
            test_post.text, self.post.text)
        self.assertEqual(
            test_post.author.username, self.post.author.username)
        self.assertEqual(
            test_post.group.title, self.group.title)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.guest_client.get(reverse(self.index[1]))
        test_post = response.context['page_obj'][0]
        self.template_test(test_post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(self.group_list[1], kwargs=self.group_list[2])
        )
        test_post = response.context['page_obj'][0]
        self.template_test(test_post)

    def test_profile_show_correct_context(self):
        """Шаблон profile получает правильный контекст."""
        response = self.guest_client.get(
            reverse(self.profile[1], kwargs=self.profile[2]))
        test_post = response.context['page_obj'][0]
        self.template_test(test_post)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail получает правильный контекст."""
        response = self.guest_client.get(
            reverse(self.post_detail[1], kwargs=self.post_detail[2]))
        self.template_test(response.context.get('post'))
        self.assertEqual(
            response.context['comments'][0],
            self.post.comments.select_related('post', 'author')[0]
        )

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(self.create[1])))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            self.post_edit[1], kwargs=self.post_edit[2])))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_correct_create_on_page(self):
        """Проверка, что пост добавился на страницы."""
        cache.clear()
        for url, name, arg in self.templates_for_paginator:
            rev_template = reverse(name, kwargs=arg)
            with self.subTest(rev_template=rev_template):
                response = self.authorized_client.get(rev_template)
                self.assertEqual(
                    response.context.get('page_obj')[NUM_OF_POST], self.post)

    def test_post_in_correct_group(self):
        """Проверка, что пост попал в нужную группу."""
        uncorrect_group = Group.objects.create(
            title='Тестовый заголовок',
            slug='uncorrect-slug',
            description='Тестовое описание',
        )
        response = self.authorized_client.get(
            reverse(self.group_list[1], args=[uncorrect_group.slug]))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_paginator_correct(self):
        """ Проверка паджинатора. """
        cache.clear()
        for url, name, arg in self.templates_for_paginator:
            rev_template = reverse(name, kwargs=arg)
            with self.subTest(rev_template=rev_template):
                response = self.authorized_client.get(rev_template)
                self.assertEqual(len(
                    response.context['page_obj']), NUM_POSTS_FIRST_PAGE)
                response_for_last = self.authorized_client.get(
                    f"{rev_template}{'?page=2'}")
                self.assertEquals(len(
                    response_for_last.context['page_obj']),
                    NUM_POSTS_LAST_PAGE
                )

    def test_index_cache_correct(self):
        """Кэш index."""
        index = self.index[1]
        cache_post = Post.objects.create(author=self.user, text='Пост кэш')
        content_after_create = self.authorized_client.get(
            reverse(index)).content
        cache_post.delete()
        content_after_delete = self.authorized_client.get(
            reverse(index)).content
        cache.clear()
        content_after_clear = self.authorized_client.get(
            reverse(index)).content
        self.assertEqual(
            content_after_delete, content_after_create
        )
        self.assertNotEqual(
            content_after_delete, content_after_clear
        )

    def test_profile_follow(self):
        """Проверка не/отображения поста на странице подписки."""
        Follow.objects.create(user=self.user, author=self.author_f)
        Post.objects.create(
            text='Тестовый пост подписки',
            author=self.author_f
        )
        response = self.authorized_client.get(reverse(self.follow_index[1]))
        len_correct = len(response.context['page_obj'])
        self.assertEqual(
            response.context['page_obj'].object_list[1].author.id,
            self.author_f.id)
        response = self.authorized_client1.get(reverse(self.follow_index[1]))
        self.assertNotEqual(
            len(response.context['page_obj']), len_correct)

    def test_following(self):
        """Проверка подписки."""
        response = self.authorized_client.get(reverse(
            self.follow[0],
            kwargs={'username': self.author_f.username})
        )
        self.assertRedirects(response, '/profile/author_follow/')

    def test_following(self):
        """Проверка отписки."""
        response_unfollow = self.authorized_client.get(reverse(
            self.unfollow[0],
            kwargs={'username': self.author_f.username})
        )
        self.assertRedirects(response_unfollow, '/profile/author_follow/')
