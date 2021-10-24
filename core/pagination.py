from rest_framework.pagination import CursorPagination, LimitOffsetPagination


class CustomCursorPagination(CursorPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    ordering = '-created_time'


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 6
    offset = 6
