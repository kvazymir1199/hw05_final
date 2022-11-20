from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test Post',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_status(self):
        reversed_names = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            'unexciting_page': HTTPStatus.NOT_FOUND,
        }

        for name, status in reversed_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertEqual(response.status_code, status)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /task/test_slug/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            reverse('posts:post_create'),
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_post_id_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /post/post_id/edit перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
            status_code=HTTPStatus.FOUND
        )

    # Проверка шаблонов
    def test_template(self):
        reversed_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',

        }

        for name, templates in reversed_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, templates)
