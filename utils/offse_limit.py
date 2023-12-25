from drf_multiple_model.views import ObjectMultipleModelAPIView
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination

class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 2


class ObjectLimitPaginationView(ObjectMultipleModelAPIView):
    pagination_class = LimitPagination
    querylist = (
        {'queryset': Article.objects.all(), 'serializer_class': ArticleSerializer},
        {'queryset': Comment.objects.all(), 'serializer_class': CommentSerializer},
    )
