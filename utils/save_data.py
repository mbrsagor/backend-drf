from myapp.models import MyModel  # Replace with your model

def save_data_to_database(data):
    for item in data:
        MyModel.objects.update_or_create(
            external_id=item['id'],  # Use a unique identifier from the API
            defaults={
                'field1': item['field1'],  # Map API fields to your model fields
                'field2': item['field2'],
                # Add other fields as necessary
            },
        )


