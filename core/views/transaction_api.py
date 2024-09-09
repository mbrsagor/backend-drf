from django.db.models import Q
from rest_framework import generics


class TransactionHistoryListAPIView(generics.ListAPIView):
    """
    Name: Transaction History list API
    Description: Lists all Transaction History objects
    URL: /api/v1/sponsor/transaction-history/
    Method: GET
    :param
    :return
    """

    queryset = TransactionHistory.objects.all()
    serializer_class = transaction_history_serializer.TransactionHistorySerializer
    pagination_class = custom_pagination.CustomPagination
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_class = filter_utils.TransactionHistoryFilter

    def get_queryset(self):
        # THe company ID parameter will fix
        company_id = self.request.query_params.get("company_id")
        # queryset
        queryset = TransactionHistory.objects.filter(company_id=company_id)
        # Get data from request
        amount = self.request.query_params.get('amount')
        transaction_type = self.request.query_params.get('transaction_type')
        transID = self.request.query_params.get('transID')
        created_at = self.request.query_params.get('created_at')

        if str(amount):
            queryset = queryset.filter(Q(amount__icontains=amount))

        if str(transaction_type):
            queryset = queryset.filter(Q(transaction_type=transaction_type))

        if str(transID):
            queryset = queryset.filter(Q(transID__icontains=transID))

        if str(created_at):
            queryset = queryset.filter(Q(created_at__date__icontains=created_at))
        return queryset

