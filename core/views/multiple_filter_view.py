from django.db.models import Q
from rest_framework import status, views
from rest_framework.response import Response

from utils import response, messages


class TransactionListFilterAPI(views.APIView):
    """
    Name: Transaction List Filter API.
    Description: Filter transactions by transfer, expense and income.
    query: Query parameters used for filtering transactions.
    """

    def get(self, request):
        account = self.request.query_params.get('account')
        date = self.request.query_params.get('date')
        types = self.request.query_params.get('types')

        # Transfer
        if types == '1':
            transfer_qs = Transfer.objects.filter(store=self.request.user.storeOwner)
            if account:
                transfer_qs = transfer_qs.filter(Q(account_from=account))
            if date:
                transfer_qs = transfer_qs.filter(Q(date=date))
            transfer_serializer = TransferUtilsSerializer(transfer_qs, many=True).data
            return Response(response.prepare_success_list_response(messages.DATA_RETURN, transfer_serializer),
                            status=status.HTTP_200_OK)

        # Expense
        elif types == '2':
            expense_qs = Expense.objects.filter(store=self.request.user.storeOwner)
            if account:
                expense_qs = expense_qs.filter(Q(account_id=account))
            if date:
                expense_qs = expense_qs.filter(Q(created_date=date))
            expense_serializer = ExpenseUtilsSerializer(expense_qs, many=True).data
            return Response(response.prepare_success_list_response(messages.DATA_RETURN, expense_serializer),
                            status=status.HTTP_200_OK)

        # Income
        elif types == '3':
            income_qs = Income.objects.filter(store=self.request.user.storeOwner)
            if account:
                income_qs = income_qs.filter(Q(account_id=account))
            if date:
                income_qs = income_qs.filter(Q(date=date))
            income_serializer = IncomeUtilsSerializer(income_qs, many=True).data
            return Response(response.prepare_success_list_response(messages.DATA_RETURN, income_serializer),
                            status=status.HTTP_200_OK)
