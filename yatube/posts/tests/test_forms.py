import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from ..forms import PostForm
from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateTest(TestCase):
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
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def template_test(self, test_post, form_data):
        """Общие тесты для создания новой/редактирования записи в БД."""
        self.assertEqual(
            test_post.text, form_data['text'])
        self.assertEqual(
            test_post.author.username, self.post.author.username)
        self.assertEqual(
            test_post.group.title, self.post.group.title)
        self.assertEqual(
            test_post.image.name, self.post.image.name)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_create_post(self):
        """Проверка создания новой записи в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.user.username]))
        self.assertEqual(
            Post.objects.count(), posts_count + 1)
        test_post = response.context['page_obj'].object_list[1]
        self.template_test(test_post, form_data)

    def test_edit_post(self):
        """Проверка изменения записи в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[1]), data=form_data, follow=True)
        self.assertRedirects(response, reverse((
            'posts:post_detail'), args=[1]))
        self.assertEqual(Post.objects.count(), posts_count)
        test_edit_post = response.context['post']
        self.template_test(test_edit_post, form_data)
