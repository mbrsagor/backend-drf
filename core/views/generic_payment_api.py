import stripe
from rest_framework import views, status
from rest_framework.response import Response

from user.models import User
from utils import responses, messages

# Set stripe secret key
stripe.api_key = "stripe_key"


class CreateStripeCustomerAPI(views.APIView):
    """
    Name: Create Stripe Customer
    Description: Create a new Stripe customer with card and bank details.
    """

    def post(self, request, *args, **kwargs):
        # Requested parameters
        data = request.data
        payment_env = data.get('payment_env')
        payment_type = data.get('payment_type')
        # card details
        card_number = data.get('card_number')
        exp_month = data.get('exp_month')
        exp_year = data.get('exp_year')
        cvc = data.get('cvc')
        # bank details
        bank_account_holder_name = data.get('bank_account_holder_name')
        bank_account_number = data.get('bank_account_number')
        bank_routing_number = data.get('bank_routing_number')

        # Save customer data to the database and return the stripe_customer_id.
        try:
            # Create Stripe Customer
            customer = stripe.Customer.create(name=self.request.user.fullname, email=self.request.user.email)

            card_token = None  # Ensure the variable is always initialized

            # For development
            if payment_env == 1:
                if payment_type == 1: # For Bank Account
                    bank_token = "btok_us_verified"
                    # Attach Card to Customer
                    stripe.Customer.create_source(customer.id, source=bank_token)
                    # Save stripe_customer_id the requested user
                    userId = self.request.user.id
                    user = User.objects.get(id=userId)
                    user.stripe_customer_id = customer.id
                    user.save()
                    return Response(responses.create_customer_with_card_bank(customer.id), status=200)

                else: # For Card 
                    card_token = "tok_visa"
                    # Attach Card to Customer
                    stripe.Customer.create_source(customer.id, source=card_token)
                    # Save stripe_customer_id the requested user
                    userId = self.request.user.id
                    user = User.objects.get(id=userId)
                    user.stripe_customer_id = customer.id
                    user.save()
                    return Response(responses.create_customer_with_card_bank(customer.id), status=200)
            else:
                if payment_type == 1: # For Bank Account
                    # Create Bank Token
                    bank_token = stripe.Token.create(
                        bank_account={
                            "country": "US",
                            "currency": "usd",
                            "account_holder_name": bank_account_holder_name,
                            "account_holder_type": "individual",
                            "routing_number": bank_routing_number,
                            "account_number": bank_account_number,
                        }
                    )
                    # Attach Bank Account to Customer
                    stripe.Customer.create_source(customer.id, source=bank_token.id)
                    return Response(responses.create_customer_with_card_bank(customer.id), status=200)
                if payment_type == 2: # For Card 
                    # Create Card Token
                    card_token = stripe.Token.create(
                        card={
                            "number": card_number,
                            "exp_month": exp_month,
                            "exp_year": exp_year,
                            "cvc": cvc
                        }
                    )
        
            # Ensure card_token is not None before attaching
            if card_token:
                # Attach Card to Customer
                stripe.Customer.create_source(customer.id, source=card_token.id)
            return Response(responses.create_customer_with_card_bank(customer.id), status=200)
        except Exception as e:
            return Response(responses.prepare_error_response(str(e)), status=status.HTTP_400_BAD_REQUEST)


class AddMoreBankCardAccountToCustomer(views.APIView):
    """
    Name: Add more account to Customer
    Description: Add more bank accounts or credit cards to an existing customer.
    """

    def post(self, request, *args, **kwargs):
        # Requested parameters
        data = request.data
        payment_env = data.get('payment_env')
        payment_type = data.get('payment_type')
        customer_id = data.get('stripe_customer_id')
        card_token = None  # Ensure the variable is always initialized

        try:
            # For development
            if payment_env == 1:
                if payment_type == 1: # For Bank Account
                    bank_token = "btok_us_verified"
                    bank_account = stripe.Customer.create_source(
                        customer_id,
                        source=bank_token
                    )
                    print(f"Bank Account: {bank_account}")
                    return Response(responses.create_customer_with_card_bank(customer_id), status=200)

                else: # For Card 
                    # card_token = "tok_visa"
                    card_token = "tok_mastercard"
                    # Attach the payment method to the customer
                    payment_method = stripe.PaymentMethod.create(
                        type="card",
                        card={"token": card_token},
                    )
                    stripe.PaymentMethod.attach(
                        payment_method.id,
                        customer=customer_id
                    )
                    return Response(responses.add_more_bank_card_response_to_customer(), status=200)
            else:
                if payment_type == 1: # For Bank Account
                    # Create Bank Token
                    bank_token = stripe.Token.create(
                        bank_account={
                            "country": "US",
                            "currency": "usd",
                            "account_holder_name": bank_account_holder_name,
                            "account_holder_type": "individual",
                            "routing_number": bank_routing_number,
                            "account_number": bank_account_number,
                        }
                    )
                    # Attach Bank Account to Customer
                    stripe.Customer.create_source(customer_id, source=bank_token.id)
                    return Response(responses.add_more_bank_card_response_to_customer(), status=200)
                if payment_type == 2: # For Card 
                    # Create Card Token
                    card_token = stripe.Token.create(
                        card={
                            "number": card_number,
                            "exp_month": exp_month,
                            "exp_year": exp_year,
                            "cvc": cvc
                        }
                    )
                    # Attach the payment method to the customer
                    stripe.Customer.create_source(customer_id, source=card_token.id)
                    return Response(responses.add_more_bank_card_response_to_customer(), status=200)
        except Exception as e:
            return Response(responses.prepare_error_response(str(e)), status=status.HTTP_400_BAD_REQUEST)


class GetCustomerAllAddedAccountAPIView(views.APIView):
    """
    Name: Get all added accounts to Customer
    Description: Get all added bank accounts or credit cards to an existing customer.
    """
    def get(self, request, *args, **kwargs):
        customer_id = request.query_params.get('stripe_customer_id')

        try:
           # Fetch all cards and bank accounts
            cards = stripe.PaymentMethod.list(customer=customer_id, type="card").data
            bank_accounts = stripe.PaymentMethod.list(customer=customer_id, type="us_bank_account").data

            # Initialize lists for the response
            card_list = []
            bank_list = []

            # Add default indicator to each card
            for card in cards:
                card_resp = {
                    'payment_method_id': card['id'],
                    'card_name': card['card']['brand'],
                    'exp_month': card['card']['exp_month'],
                    'exp_year': card['card']['exp_year'],
                    'last4': card['card']['last4']
                }
                card_list.append(card_resp)

            # Add default indicator to each bank account
            for bank_account in bank_accounts:
                # Ensure previous default bank accounts are reset properly
                bank_resp = {
                    'payment_method_id': bank_account['id'],
                    'bank_name': bank_account['us_bank_account']['bank_name'],
                    'account_holder_type': bank_account['us_bank_account']['account_holder_type'],
                    'routing_number': bank_account['us_bank_account']['routing_number'],
                    'last4': bank_account['us_bank_account']['last4']
                }
                bank_list.append(bank_resp)
            # Prepare the response
            resp = {
                'status': 'success',
                'message': 'Accounts fetched successfully',
                'card_info': card_list,
                'bank_info': bank_list,
            }
            return Response(resp, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            return Response(responses.prepare_error_response(str(e)), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                responses.prepare_error_response(f"An unexpected error occurred: {str(e)}"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SetStripeAccountAsDefaultAPIView(views.APIView):
    """
    Name: Set Stripe Account as Default
    Description: Set a specific bank account or credit card as the default for an existing customer.
    """

    def post(self, request, *args, **kwargs):
        customer_id = request.data.get('stripe_customer_id')
        payment_method_id = request.data.get('payment_method_id')

        try:
            stripe.Customer.modify(customer_id, invoice_settings={"default_payment_method": payment_method_id})
            return Response(responses.set_stripe_account_as_default(), status=200)
        except stripe.error.InvalidRequestError as e:
            return Response(responses.prepare_error_response(str(e)), status=status.HTTP_400_BAD_REQUEST)


class DeleteBankCardAPIView(views.APIView):
    """
    Delete a specific bank account or credit card from an existing customer.
    """
    def post(self, request, *args, **kwargs):
        # Retrieve data from request
        payment_method_id = request.data.get('payment_method_id')
        customer_id = request.data.get('stripe_customer_id')

        # Validate inputs
        if not payment_method_id:
            return Response(
                {"error": "Payment method ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(payment_method_id, str):
            return Response(
                {"error": f"Invalid payment method ID format: {type(payment_method_id)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Detach the payment method from the customer
            stripe.PaymentMethod.detach(payment_method_id)

            # Success response
            return Response(
                responses.prepare_success_response(messages.STRIPE_ACCOUNT_DELETE),
                status=status.HTTP_200_OK
            )
        except stripe.error.InvalidRequestError as e:
            # Stripe-specific errors (e.g., invalid payment method ID)
            return Response(
                responses.prepare_error_response(f"Stripe error: {str(e)}"),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Catch unexpected errors
            return Response(
                responses.prepare_error_response(f"An unexpected error occurred: {str(e)}"),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetDefaultStripePaymentID(views.APIView):
    """
    Name: Get Default Stripe Payment ID
    Description: Retrieve the ID of the default payment method for a customer.
    """

    def get(self, request, *args, **kwargs):
        customer_id = request.data.get('stripe_customer_id')
        try:
            # Retrieve the customer object
            customer = stripe.Customer.retrieve(customer_id)
            default_payment_method_id = customer['invoice_settings'].get('default_payment_method')

            if not default_payment_method_id:
                return Response(responses.prepare_error_response('No default payment method set.'), status=status.HTTP_404_NOT_FOUND)

            # Fetch all payment methods (cards & bank accounts)
            cards = stripe.PaymentMethod.list(customer=customer_id, type="card").data
            bank_accounts = stripe.PaymentMethod.list(customer=customer_id, type="us_bank_account").data

            # Find the default payment method
            default_payment_method = None

            for pm in cards + bank_accounts:
                if pm['id'] == default_payment_method_id:
                    default_payment_method = pm
                    break

            if default_payment_method:
                resp = {
                    'status': 'success',
                    "message": "Default payment method retried successfully",
                    "default_payment_id": default_payment_method['id'],
                    "default_type": default_payment_method['type']

                }
                return Response(resp, status=status.HTTP_200_OK)
            else:
                return Response(responses.prepare_error_response('Default payment method not found in available methods.'), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(responses.prepare_error_response(f"An unexpected error occurred: {str(e)}"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkPaymentView(views.APIView):
    """
    Name: Bulk payment system
    Description: A system to handle bulk payments, including creating a payment intent, 
    transferring funds to different accounts, and handling Stripe errors.
    method: POST
    request_body:
    """
    def post(self, request):
        try:
            total_amount = request.data.get("total_amount")  # Total charge
            currency = request.data.get("currency", "usd")
            payment_method_id = request.data.get("payment_method_id")
            transfers = request.data.get("transfers")  # List of account transfers

            # Step 1: Create PaymentIntent (Charge Customer)
            intent = stripe.PaymentIntent.create(
                amount=total_amount,
                currency=currency,
                payment_method=payment_method_id,
                confirm=True,
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never"
                })

            # Step 2: Transfer funds to different accounts
            for transfer in transfers:
                stripe.Transfer.create(
                    amount=transfer["amount"],  # Amount to send
                    currency=currency,
                    destination=transfer["account_id"],  # Stripe Connected Account ID
                    transfer_group=intent.id
                )
            resp = {
                'status': 'success',
                "message": "Bulk payment successful"

            }
            return Response(resp, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentMethodIDForCardAPIView(views.APIView):
    """
    Name: Create Payment Method ID for Card.
    Desc: Create Payment Method for Card
    """
    def post(self, request):
        try:
            # Get the card or bank details from the frontend (usually the request body)
            card_number = request.data.get("card_number")
            exp_month = request.data.get("exp_month")
            exp_year = request.data.get("exp_year")
            cvc = request.data.get("cvc")
            card_token = request.data.get("card_token") # 
            
            # For development purposes
            if card_token is not None:
                 # Create a PaymentMethod using the provided card details
                payment_method = stripe.PaymentMethod.create(
                    type="card",
                    card={"token": card_token}
                )

                # Return the payment method id back to the frontend
                return Response({
                    "payment_method_id": payment_method.id
                }, status=status.HTTP_200_OK)
            else:
                # Create a PaymentMethod using the provided card details
                payment_method = stripe.PaymentMethod.create(
                    type="card",
                    card={
                        "number": card_number,
                        "exp_month": exp_month,
                        "exp_year": exp_year,
                        "cvc": cvc,
                    }
                )

                # Return the payment method id back to the frontend
                return Response({
                    "payment_method_id": payment_method.id
                }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            # Handle errors from the Stripe API
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentMethodIdForBankAPIView(views.APIView):
    """
    Name: Create Payment Method for Bank.
    Desc: Create Payment Method for Bank
    """
    def post(self, request):
        try:
            # Get the bank account details from the frontend (usually the request body)
            routing_number = request.data.get("routing_number")
            account_number = request.data.get("account_number")
            account_holder_type = request.data.get("account_holder_type", "individual")  # 'individual' or 'company'
            bank_token = request.data.get("bank_token")
            
            if bank_token is not None:
                # Create a PaymentMethod using the provided bank account details
                payment_method = stripe.PaymentMethod.create(
                    type="us_bank_account",  # For U.S. bank accounts
                    us_bank_account={"token": bank_token}
                )
                # Return the payment method id back to the frontend
                return Response({
                    "payment_method_id": payment_method.id
                }, status=status.HTTP_200_OK)
            else:
                # Create a PaymentMethod using the provided bank account details
                payment_method = stripe.PaymentMethod.create(
                    type="us_bank_account",  # For U.S. bank accounts
                    us_bank_account={
                        "routing_number": routing_number,
                        "account_number": account_number,
                        "account_holder_type": account_holder_type,  # 'individual' or 'company'
                    }
                )

                # Return the payment method id back to the frontend
                return Response({
                    "payment_method_id": payment_method.id
                }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            # Handle errors from the Stripe API
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CreateStripeAccountForSellerAPIView(views.APIView):
    def post(self, request):
        # Get data from requested parameter
        email = request.data.get('email')

        try:
            # Step 1: Create a Stripe Standard Account for the seller
            account = stripe.Account.create(
                type="express",  # Standard account type
                country="US",  # Seller's country (can be dynamic)
                email=email,  # Seller's email address
                capabilities={ "card_payments": {"requested": True}, "transfers": {"requested": True}},
            )
            
            # Step 2: Generate the account link for Stripe onboarding
            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url="https://your-site.com/reauth",  # URL to refresh the link if needed
                return_url="https://your-site.com/return_from_stripe",  # URL after onboarding is completed
                type="account_onboarding",
            )
            
            # Return the account ID and the link for the seller to complete onboarding
            return Response({
                "account_id": account.id,
                "account_link": account_link.url
            })

        except stripe.error.StripeError as e:
            # Handle Stripe API errors
            return Response(responses.prepare_error_response(str(e)), status=400)
