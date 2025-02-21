import stripe

stripe.api_key = "your_secret_key"  # Replace with your test secret key

payment_intent = stripe.PaymentIntent.create(
    amount=50000,  # $500.00 in cents ($500)
    currency="usd",
    payment_method="pm_card_mastercard",  # Use Stripe's test MasterCard
    confirm=True,
)

print("Charge successful! PaymentIntent ID:", payment_intent.id)
