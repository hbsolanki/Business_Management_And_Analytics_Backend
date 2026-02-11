from rest_framework.pagination import CursorPagination

class CursorPagination(CursorPagination):
    page_size = 6
    ordering = "-created_at"
    cursor_query_param = "cursor"
