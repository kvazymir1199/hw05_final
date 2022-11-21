import shutil
import tempfile
from http import HTTPStatus
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model

from ..forms import PostForm, CommentForm
from ..models import Post, User, Group, Comment
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group_1 = Group.objects.create(
            title='Тестовый заголовок Группы 1',
            description='текст группы 1',
            slug='test-slug'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок Группы 2',
            description='текст группы 2',
            slug='test-slug_2'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст для проверки изменения',
            author=cls.user,
            group=cls.group_1
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_without_group(self):
        '''Проверка на создание поста без указания группы'''
        posts_count_before_creation = Post.objects.count()
        form_data = {
            'text': 'Текст для поста без группы',
            'group': ''
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        posts_count_after_creation = Post.objects.count()
        self.assertEqual(
            posts_count_before_creation + 1,
            posts_count_after_creation
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text']
            ).exists()
        )

    def test_create_post_with_group(self):
        '''Проверка на создание поста без указания группы'''
        posts_count_before_creation = Post.objects.count()
        form_data = {
            'text': 'Текст для поста с группой',
            'group': self.group_1.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        posts_count_after_creation = Post.objects.count()
        self.assertNotEqual(
            posts_count_before_creation,
            posts_count_after_creation
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group_1.id
            ).exists()
        )

    def test_post_can_be_edit(self):
        ''' Проверка на изменение информации и группы в посте'''
        old_post = self.post
        form = {
            'text': 'Измененный текст',
            'group': self.group_2.id
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': old_post.id}
            ),
            data=form,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                id=old_post.id,
                text=form['text'],
                group=self.group_2.id
            ).exists()
        )


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group = Group.objects.create(
            title='Тестовый заголовок Группы 2',
            description='текст группы 2',
            slug='test-slug_2'
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='Test.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        """Валидная форма создает запись в Task."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст для поста с группой',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверю создалась ли запись в базе данных
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст для поста с группой',
                # image=form_data['image']
            ).exists()
        )

    def test_correct_context(self):
        self.post = Post.objects.create(
            text='Тестовый текст для проверки изменения',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )

        test_reverses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user})
        ]
        for page in test_reverses:
            with self.subTest(page=page):
                response = self.authorized_client.post(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(
                    response.context['page_obj'][0].image,
                    'posts/Test.gif'
                )


class CommentsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Denis')
        cls.group = Group.objects.create(
            title='Тестовый заголовок Группы 2',
            description='текст группы 2',
            slug='test-slug_2'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст для проверки изменения',
            author=cls.user,
            group=cls.group,
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_by_authorized_client(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Текст для поста с группой',
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(comment_count, Comment.objects.count())

    def test_post_page_have_comment(self):
        form_data = {
            'text': 'Текст коментария',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.post(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context['comments'][0].text,
            form_data['text']
        )
