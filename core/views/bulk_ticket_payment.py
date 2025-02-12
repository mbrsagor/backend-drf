import stripe
from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response

from event.models import Event
from sponsor.models import TransactionHistory, Ticket
from bulk.api.serializers import bulk_ticket_serializer
from bulk.models import BulkTicket, ComplementaryTicketPrice
from utils import custom_pagination, responses, messages, price_range_calculation, stripe_amount_calculator, sms_helper

# Set stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY


class BulkTicketListCreateAPIView(generics.ListCreateAPIView):
    """
    Name: Bulk Ticket List and Create API
    Description: List all bulk tickets and create a new bulk ticket.
    Method: GET, POST
    URL: /api/v1/bulk/tickets/
    params:
    :return
    """
    queryset = BulkTicket.objects.all()
    serializer_class = bulk_ticket_serializer.BulkTicketSerializer
    pagination_class = custom_pagination.CustomPagination

    def get_queryset(self):
        return BulkTicket.objects.filter(company_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        converter = stripe_amount_calculator.AmountConverter()  # convert dolor to cents
        # Price ranges
        ranges = []
        # Get data from request body
        data = request.data
        quantity = data.get('quantity')
        currency = data.get('currency')
        event = data.get('event')
        phone = data.get('phone')
        single_ticket_price = data.get('single_ticket_price')
        payment_method_id = request.data.get("payment_method_id")  # Stored Stripe payment method
        # Get complementary ticket prices
        complementary_ticket_prices = ComplementaryTicketPrice.objects.all()
        for ticket in complementary_ticket_prices:
            range_with_price = {
                'qnt': ticket.ticket_qnt_range,
                'price': ticket.price
            }
            ranges.append(range_with_price)

        # Update the 'qnt' value for each dictionary by removing the hyphen
        for item in ranges:
            item['qnt'] = item['qnt'].replace('-', ',')  # Replace '-' with an empty string

        # Iterate through each dictionary and check if quantity is within any range
        for item in ranges:
            start, end = map(int, item['qnt'].split(','))  # Split and convert to integers
            if start <= quantity <= end:  # Check if number falls within the range
                # final_price = float({item['price']}.pop())  # Use `pop()` or access it directly
                _final_price = price_range_calculation.calculate_total(quantity)
                # For complementary ticket (If single ticket price equals to zero, so host need to pay)
                if single_ticket_price == 0.00:
                    # Make stripe payment
                    amount=converter.to_cents(float(_final_price)),  # amount in cents,
                    final_amount= amount[0] # Final amount in plain cents 
                    # print(f"Amount: {final_amount}")
                    # Configure the stripe payment
                    try:
                        # Start stripe payment system
                        if not final_amount or not payment_method_id:
                            return Response(responses.prepare_error_response(messages.STRIPE_REQUIRED_PAYMENT_MSG), status=400)

                        # Retrieve stored customer ID
                        customer_id = request.user.stripe_customer_id  # Ensure this is stored in User model

                        # Attach payment method to customer if not already attached
                        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

                        # Create and confirm the PaymentIntent
                        intent = stripe.PaymentIntent.create(
                            amount=final_amount,
                            currency=currency,
                            customer=customer_id,
                            payment_method=payment_method_id,
                            confirm=True,
                            off_session=True,  # Allows for stored payment methods
                        )

                        # Extract transaction details
                        transaction_id = intent.id  # PaymentIntent ID (useful as a transaction reference)
                        status = intent.status  # Possible values: 'succeeded', 'requires_action', 'requires_payment_method', etc.
                        amount_received = intent.amount_received  # Amount successfully charged
                        payment_method = intent.payment_method  # Payment method ID used
                        created_at = intent.created  # Timestamp of transaction (Unix timestamp)

                        # Crete bulk ticket
                        serializer = bulk_ticket_serializer.BulkTicketSerializer(data=request.data)
                        if serializer.is_valid():
                            serializer.save(company_id=self.request.user.id)
                            # Save transaction history
                            TransactionHistory.objects.create(
                                name=self.request.user.fullname,
                                phone=self.request.user.phone,
                                company_id=self.request.user.id,
                                event_id=event,
                                payment_method="visa",
                                country="US",
                                transID=transaction_id,
                                transaction_type=2,
                                amount=final_amount,
                                deduction_amount=0.00,
                                fee_deduction=0.00,
                                net_payout=0.00,
                                admin_payout=final_amount,
                            )
                            ambassador = serializer.data
                            ambassador_id = ambassador.get('id')
                            # Generate tickets
                            for _ticket in range(quantity):
                                Ticket.objects.create(
                                    ambassador_id=ambassador_id,
                                    event_id=event,
                                    sponsor_id=self.request.user.id,
                                    ticket_type=2,
                                )
                        # generate link for complementary_ticket_link to send to customer
                        link = f"{settings.SITE_URL}/bulk-ticket/complementary/{ambassador_id}"
                        # Get event title from event ID:
                        event_title = Event.objects.get(id=event)
                        # Send SMS
                        message = f"Welcome to our {event_title.title}. Link: {link}"
                        sms_helper.send_sms(sender=phone, message=message)
                        
                        # Custom response
                        resp = {
                            "status": "success",
                            "message": messages.PAYMENT_SUCCESS_MSG,
                            "link": link,
                            "is_payment_for_host": True,
                            "amount_received": amount_received,
                            "transaction_id": transaction_id,
                            "payment_method": payment_method,
                            "created_at": created_at,
                        }
                        return Response(resp, status=201)
                    except Exception as ex:
                        return Response(responses.prepare_error_response(str(ex)), status=500)
                    except stripe.error.CardError as e:
                        return Response(responses.prepare_error_response(str(e)), status=400)
                    except stripe.error.StripeError as e:
                        return Response(responses.prepare_error_response(str(e)), status=400)
                    except Exception as e:
                        return Response(responses.prepare_error_response(str(e)), status=500)
                else:
                    # Create bulk ticket for premium
                    _ambassador_id = None # TODO: Here, default ID is none
                    serializer = bulk_ticket_serializer.BulkTicketSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save(company_id=self.request.user.id)
                        ambassador = serializer.data
                        ambassador_id = ambassador.get("id")
                        _ambassador_id = ambassador_id
                    # Get event title from event ID:
                    event_title = Event.objects.get(id=event)
                    # Generate premium_ticket_link
                    link = f"{settings.SITE_URL}/bulk-ticket/premium/{phone}/{_ambassador_id}/{event}/{self.request.user.id}/{quantity}/{single_ticket_price}"
                    message = f"Welcome to our {event_title.title}. Link: {link}"
                    # Send SMS
                    sms_helper.send_sms(sender=phone, message=message)
                    resp = responses.prepare_generate_ticket_response(
                        message=messages.PAYMENT_SUCCESS_MSG,
                        link=link,
                        is_payment_for_host=False
                    )
                    return Response(resp, status=201)
                # print(f"{quantity} is within the range {start}-{end} with price: {item['price']}")
                break  # Exit loop after finding the first match
        else:
            resp = responses.prepare_error_response(f"{quantity} is out of the range.")
            return Response(resp, status=400)
