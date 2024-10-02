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
        converter = AmountConverter()  # convert dolor to cents
        # Price ranges
        ranges = []
        # Get data from request body
        data = request.data
        quantity = data.get('quantity')
        currency = data.get('currency')
        single_ticket_price = data.get('single_ticket_price')
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
                final_price = float({item['price']}.pop())  # Use `pop()` or access it directly
                # For complementary ticket (If single ticket price equals to zero, so host need to pay)
                if single_ticket_price == 0.00:
                    # Configure the stripe payment
                    try:
                        # Create a PaymentIntent
                        intent = stripe.PaymentIntent.create(
                            amount=converter.to_cents(float(final_price)),  # amount in cents,
                            currency=currency,
                            metadata={"integration_check": "accept_a_payment"},
                        )
                        # Create a new customer in Stripe
                        customer = stripe.Customer.create(
                            email=self.request.user.email,
                            name=self.request.user.fullname,
                            description='Payment for complementary bulk ticket'
                        )
                        # Create the ephemeral key for the specified customer
                        ephemeral_key = stripe.EphemeralKey.create(
                            customer=customer, 
                            stripe_version='2022-11-15'
                        )
                        # Custom response
                        resp = responses.bulk_payment_response(
                            intent.id, intent.client_secret, ephemeral_key.secret
                        )
                        return Response(resp, status=status.HTTP_201_CREATED)
                    except Exception as ex:
                        return Response(responses.prepare_error_response(str(ex)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    resp = {
                        'status': 'success',
                        'message': 'Link success send to the phone number.',
                        'is_payment_for_host': False
                    }
                    return Response(resp, status=status.HTTP_200_OK)
                # print(f"{quantity} is within the range {start}-{end} with price: {item['price']}")
                break  # Exit loop after finding the first match
        else:
            resp = responses.prepare_error_response(f"{quantity} is out of the range.")
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

