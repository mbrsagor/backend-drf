from rest_framework.serializers import Serializer

class CustomSerializer(Serializer):
    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception=raise_exception)
        # Simplify error messages
        if not self.errors:
            return True
        simplified_errors = {field: " ".join([str(err) for err in errors]) for field, errors in self.errors.items()}
        self._errors = simplified_errors  # Override the errors attribute
        return not bool(self._errors)


#  Alternatively, you can create a helper function to simplify errors outside the serializer:
def simplify_errors(errors):
    return {field: " ".join([str(err) for err in errors]) for field, errors in errors.items()}

# Example usage:
from rest_framework.response import Response
from rest_framework import status

def some_view(request):
    serializer = SomeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(simplify_errors(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
