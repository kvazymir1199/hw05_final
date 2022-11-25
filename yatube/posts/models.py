from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="Имя группы",
        max_length=200
    )
    slug = models.SlugField(
        verbose_name="Уникальный номер",
        unique=True
    )
    description = models.TextField(
        verbose_name="Описание"
    )

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name="Пост"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        related_name="group_posts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        # выводим текст поста
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name="Пост",
        related_name="posts_comment",
        on_delete=models.CASCADE,
        blank=True,
        null=False
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name='comment_author'
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор поста",
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
            models.UniqueConstraint(
                name='objects_unique',
                fields=['author', 'user']
            )
        ]
