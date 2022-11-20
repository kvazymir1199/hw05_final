from django.core.paginator import Paginator

POST_NUMBER = 10


def page_paginator(request, post):
    paginator = Paginator(post, POST_NUMBER)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
