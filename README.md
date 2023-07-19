![Header](git_hub/preview.png)

[![Django](https://img.shields.io/badge/DJANGO-ff1709?style=for-the-badge&logo=django&logoColor=white&color=darkgreen&labelColor=gray)](https://www.djangoproject.com/)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
[![Python](https://img.shields.io/badge/-Python-464646?style=for-the-badge&logo=Python)](https://www.python.org/)
## Описание

**«Yatube»** является социальной сетью для публикации личных записей с возможностью публикацией и комментированием
постов, а также оформлением подписки на авторов.

## Cтек:

- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- [HTML](https://www.w3.org/html/)
- [Django](https://www.djangoproject.com/)
- [Django ORM](https://docs.djangoproject.com/en/4.2/topics/db/queries/)
- [SQL](https://ru.wikipedia.org/wiki/SQL)
- [Git](https://git-scm.com/)
- [Pytest](https://docs.pytest.org/en/latest/)
- [Pillow](https://python-pillow.org/)

## Запуск проекта в dev-режиме:

Инструкция для операционной системы windows и утилиты git bash.

* Клонировать репозиторий и перейти в него в командной строке:

``` bash
 git clone git@github.com:ralinsg/hw05_final.git
```

``` bash
 cd hw05_final
```

* Cоздать и активировать виртуальное окружение:

``` bash
 py -3.7 -m venv venv
```

``` bash
 source venv/Scripts/activate
```

``` bash
 python3 -m pip install --upgrade pip
```

* Установить зависимости из файла requirements.txt:

``` bash
 pip install -r requirements.txt
```

* Выполнить миграции:

``` bash
 python manage.py makemigrations
```

``` bash
 python manage.py migrate
```

* Создать суперпользователя:

``` bash
 python manage.py createsuperuser
```

* Собрать статику:

``` bash
 python manage.py collectstatic
```

Запускаем проект:

``` bash
 python manage.py runserver
```

После чего проект будет доступен по адресу http://localhost/

## Примеры запросов:

Отображение постов и публикаций (GET, POST)

```bash
http://127.0.0.1:8000/posts/
```

Получение, изменение, удаление поста с соответствующим id (GET, PUT, PATCH, DELETE)

```bash
http://127.0.0.1:8000/posts/{id}/
```

Получение информации о подписках текущего пользователя, создание новой подписки на пользователя (GET, POST)

 ```bash
http://127.0.0.1:8000/posts/follow/
```

## Авторы

- Миронов Денис [@kvazymir1199](https://github.com/kvazymir1199)