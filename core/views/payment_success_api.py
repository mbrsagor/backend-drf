# TODO: Successful payment view for single ticket buying
class SuccessfullyPayView(generic.TemplateView):
    template_name = 'payment/payment_success.html'

    def get_context_data(self, **kwargs):
        tickets = []
        context = super().get_context_data(**kwargs)
        event_id = self.request.session.get("event_id")
        quantity = self.request.session.get("quantity")
        ticket = Ticket.objects.filter(event=event_id).values('sponsor', 'event').first()
        for i in range(int(quantity)):
            new_ticket = Ticket.objects.create(
                event_id=ticket["event"], sponsor_id=ticket["sponsor"]
            )
            new_ticket.save()
            tickets.append(new_ticket)
        context["new_ticket"] = tickets  # Add the ticket number to the context
        self.request.session.pop("event_id") # Destroy session key for event
        self.request.session.pop("quantity")  # Destroy session key for quantity
        return context

