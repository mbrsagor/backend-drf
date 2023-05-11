from user.models.member import Member


def notification_processor(request):
    try:
        members = Member.objects.filter(merchant=request.user.id, status=1)
        return {'members': members}
    except Member.DoesNotExist:
        return None

