import stripe
from django.views import generic, View

stripe.api_key = settings.STRIPE_SECRET_KEY
from utils import transaction_calculation
from utils.stripe_amount_calculator import AmountConverter


# Todo: Stripe Purchase
class PurchasePackageView(View):
    def post(self, request, *args, **kwargs):
        converter = AmountConverter()  # convert dolor to cents
        # Get data from request
        price = request.POST.get("price")
        package_id = request.POST.get('package_id')
        package = Package.objects.get(id=package_id)

        # Save data to session
        self.request.session['package_id'] = package_id
        self.request.session['price'] = price

        try:
            # You can change the price, currency, and other details as needed
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=self.request.session.get("email"),
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": package.title,  # Set event title
                                "description": "Purchase package"
                            },
                            "unit_amount": converter.to_cents(float(price)),  # amount in cents
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri("/ticket/package-purchase-success/"),
                cancel_url=request.build_absolute_uri("/ticket/payment-cancel/"),
            )
            session_id = checkout_session.id
            self.request.session['checkout_session_id'] = session_id  # Save session id to session
            return redirect(checkout_session.url)
        except Exception as e:
            return render(request, "payment/error.html", {"error": str(e)})


# Todo: Stripepayment successfully view
class SuccessfullyPayPackageView(generic.TemplateView):
    template_name = 'package/package_success_purchase.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        converter = AmountConverter()  # convert dolor to cents
        amount = self.request.session.get("price")
        decimal_amount = float(amount)  # convert string to decimal
        tc = transaction_calculation.transaction_calculate(
            AmountConverter.to_real_amount(decimal_amount)
        )
        # Stripe payment information
        session_id = self.request.session.get('checkout_session_id')
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent_id = session.payment_intent  # This is the transaction ID
        # Optionally, you can retrieve more details about the payment intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        # Purchase event
        PurchaseEvent.objects.create(
            currency="USD",
            price=amount,
            sponsor_id=self.request.session.get('user_id'),
            package_id=self.request.session.get('package_id'),
            event_id=self.request.session.get('event_id'),
        )
        # Save transition history
        TransactionHistory.objects.create(
            name=self.request.session.get("fullname"),
            amount=amount,
            transaction_type=1,
            payment_method="Card",
            country="USA",
            transID=payment_intent.id,  # Get transaction ID from payment intent
            deduction_amount=tc["deduction"],
            fee_deduction=tc["fee_deduction"],
            net_payout=tc["net_payout"],
            admin_payout=tc["admin_payout"],
            company_id=self.request.session.get("company_id"),  # Get company id from session
            event_id=self.request.session.get("event_id"),  # Get event id from session
        )
        # Remove all session data
        self.request.session.pop('fullname')  # Destroy session key for email
        self.request.session.pop('email')  # Destroy session key for email
        self.request.session.pop('user_id')  # Destroy session key for email
        self.request.session.pop('price')  # Destroy session key for price
        self.request.session.pop('company_id')  # Destroy session key for company id
        self.request.session.pop('event_id')  # Destroy session key for event id
        self.request.session.pop('checkout_session_id')  # Destroy session key for event id
        return context


