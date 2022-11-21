from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post, Follow
from django.urls import reverse
from django import forms
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()

PAGE_LEN = 10


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group = Group.objects.create(
            title='Тестовый заголовок Группы 1',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок группы 2',
            description='Текст группы 2',
            slug='test-slug_2'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Test Post Text',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': self.group.slug}
                        ),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': self.user}
                        ),
            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': self.post.id}
                        ),
            'posts/create_post.html':
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}
                        ),

        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        text = response.context['page_obj'][0].text
        self.assertEqual(text, self.post.text)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            )
        )
        text = response.context['page_obj'][0].text

        self.assertEqual(text, self.post.text)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.user}
            )
        )
        text = response.context['page_obj'][0].text
        author = response.context['author']
        self.assertEqual(text, self.post.text)
        self.assertEqual(author, self.user)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        text = response.context['post'].text
        count = response.context['post'].author.posts.count()
        self.assertEqual(text, self.post.text)
        self.assertEqual(count, 1)

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )

        for post in range(12):
            cls.new_post = Post.objects.create(
                author=cls.user,
                text=f'Text Post {post + 1}',
                group=cls.group
            )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_index_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), PAGE_LEN)

    def test_second_page_index_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            Post.objects.count() - len(response.context['page_obj']),
            PAGE_LEN
        )

    def test_first_page_group_lists_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), PAGE_LEN)

    def test_second_page_group_lists_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}
            ) + '?page=2'

        )
        self.assertEqual(
            Post.objects.count() - len(response.context['page_obj']),
            PAGE_LEN
        )

    def test_first_page_profile_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']),
            PAGE_LEN
        )

    def test_second_page_profile_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ) + '?page=2'
        )
        self.assertEqual(
            Post.objects.count() - len(response.context['page_obj']),
            PAGE_LEN
        )


class PagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        for group in range(1, 3):
            Group.objects.create(
                title=f'Тестовый заголовок Группы {group}',
                description=f'текст группы {group}',
                slug=f'test-slug-{group}'
            )
        cls.new_post = Post.objects.create(
            author=cls.user,
            text='Test Post Text',
            group=Group.objects.last(),
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_post_after_creation(self):
        first_group = Group.objects.first()
        last_group = Group.objects.last()
        reverses = {
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': last_group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            )
        }
        # Проверю появится ли созданный пост на страницах по его id
        for template in reverses:
            with self.subTest():
                response = self.authorized_client.get(template)
                post_id = response.context['page_obj'][0].id
                self.assertEqual(post_id, self.new_post.id)
        # проверяю пренадлежит ли пост одной группе:
        # значит в группе 2 не должно быть постов
        self.assertFalse(
            Post.objects.filter(
                group=first_group.id
            ).exists()
        )


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index_page_test(self):
        self.post = Post.objects.create(
            author=self.user,
            text='Cache Test Index Page',
            group=Group.objects.last(),
        )
        response = self.authorized_client.get(
            reverse('posts:index')
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        index_page_content_1 = response.content
        self.post.delete()
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        index_page_content_2 = response.content
        self.assertEqual(index_page_content_1, index_page_content_2)
        cache.clear()
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        index_page_contex_3 = response.content
        self.assertNotEqual(index_page_content_1, index_page_contex_3)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.user2 = User.objects.create_user(username='Julia')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Post user 1',
        )
        cls.post = Post.objects.create(
            author=cls.user2,
            text='Post user2',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user2)

    def test_auth_user_can_follow(self):
        follow_count = Follow.objects.filter(user=self.user).count()
        context = {
            'user': self.user,
            'author': self.user2,
        }
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user2}),
            data=context,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        follow_count_1 = Follow.objects.filter(user=self.user).count()
        self.assertNotEqual(follow_count, follow_count_1)
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user2}
            ),
            data=context,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        follow_count_2 = Follow.objects.filter(user=self.user).count()
        self.assertEqual(follow_count, follow_count_2)

    def test_post_exists_in_auth_feed(self):
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        posts_before_following = len(response.context['page_obj'])
        Follow.objects.create(
            user=self.user,
            author=self.user2
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        posts_after_following = len(response.context['page_obj'])
        self.assertEqual(posts_before_following,
                         posts_after_following - 1)

        response = self.authorized_client_2.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        posts_new_user = len(response.context['page_obj'])
        self.assertEqual(posts_before_following,
                         posts_new_user)
