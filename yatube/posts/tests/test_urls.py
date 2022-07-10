from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        )
        cls.index = ('posts/index.html', '/')
        cls.group_list = ('posts/group_list.html', '/group/test_slug/')
        cls.profile = ('posts/profile.html', '/profile/auth/')
        cls.post_detail = ('posts/post_detail.html', '/posts/1/')
        cls.create = ('posts/create_post.html', '/create/')
        cls.post_edit = ('posts/create_post.html', '/posts/1/edit/')
        cls.post_comment = ('posts/post_detail.html', '/posts/1/comment/')

        cls.url_names_guest = (
            cls.index, cls.group_list, cls.profile, cls.post_detail
        )
        cls.url_names_auth = (
            cls.index, cls.group_list, cls.profile, cls.post_detail, cls.create
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Any')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_exists_at_desired_location_guest(self):
        """Проверка доступности адреса."""
        for adress, template in self.url_names_guest:
            with self.subTest():
                response = self.guest_client.get(template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_authorized_user(self):
        """Проверка доступности адреса."""
        for adress, template in self.url_names_auth:
            with self.subTest():
                response = self.authorized_client.get(template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_url_redirect(self):
        """Проверка работы перенаправления гостя при попытке правки поста."""
        response = self.guest_client.get(self.post_edit[1])
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_urls_uses_correct_template(self):
        """Проверка шаблона для адресов."""
        for adress, template in self.url_names_auth:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, adress,)

    def test_404_url_exists_at_desired_location(self):
        """Проверка ответа /страница не найдена/ на рандомный запрос"""
        response = self.guest_client.get('/random/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_post_url_redirect(self):
        """Проверка работы перенаправления неавтор при попытке правки поста."""
        response = self.authorized_client.get(self.post_edit[1])
        self.assertRedirects(response, '/profile/Any/')

    def test_comment_post_url_redirect(self):
        """Проверка работы перенаправления гостя при попытке коммента поста."""
        response = self.guest_client.get(self.post_comment[1])
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
