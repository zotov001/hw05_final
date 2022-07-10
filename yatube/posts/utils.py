from django.core.paginator import Paginator


LIMIT_POSTS_ON_PAGE: int = 10


def paginator(request, post_list):
    page_number = request.GET.get('page')
    paginator = Paginator(post_list, LIMIT_POSTS_ON_PAGE).get_page(page_number)
    return paginator
