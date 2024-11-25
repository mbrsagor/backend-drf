@method_decorator(login_required(login_url="/user/login"), name="dispatch")
class TransactionUpdateView(View):

    def get(self, request, pk):
        transaction = Transaction.objects.get(id=pk)
        projects = Project.objects.all()
        labors = Worker.objects.filter(worker_type=1)
        vendors = Worker.objects.filter(worker_type=2)
        context = {
            "projects": projects,
            "labors": labors,
            "vendors": vendors,
            "transaction": transaction,
        }
        return render(request, "transaction/update_transaction.html", context)

    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, id=pk)
        # Update transaction fields
        transaction.project_id = request.POST.get("project")
        transaction.source_type = request.POST.get("source_type")
        transaction.save()

        # Clear and recreate profits
        transaction.profits.clear()
        data = [
            {
                "date": request.POST.get(f"date[{i}]"),
                "quantity": request.POST.get(f"quantity[{i}]"),
                "amount": request.POST.get(f"amount[{i}]"),
                "worker_ids": request.POST.get(f"worker[{i}]"),
                "notes": request.POST.get(f"notes[{i}]"),
            }
            for i in range(len(request.POST.getlist("date[]")))
        ]
        for profit_data in data:
            worker_id = int(profit_data["worker_ids"])
            worker_instance = Worker.objects.get(id=worker_id)
            profit = Profit(
                amount=profit_data["amount"],
                quantity=profit_data["quantity"],
                date=profit_data["date"],
                notes=profit_data["notes"],
                worker=worker_instance,
            )
            profit.save()
            transaction.profits.add(profit)
        transaction.save()
        return redirect(
            "transaction_detail", pk=transaction.id
        )  # Adjust the URL name as needed

