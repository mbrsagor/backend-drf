# Todo: This serializer use for sponsor API
class FollowUserSerializer(serializers.ModelSerializer):
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'host_name', 'total_follower',
            'is_followed', 'host_id', 'avatar'
        )

    def get_is_followed(self, obj):
        # Accessing the current user from the context
        user = self.context.get("request").user
        # Checking if the current user is following the host
        if Follow.objects.filter(sponsor_id=user.id, host_id=obj.host_id).exists():
            return True
        return False


# Call the view how to get the current user
# Who to follow
follow = User.objects.filter(role=3)[:10]
follower = follow_serializer.FollowUserSerializer(follow, many=True, context={'request': request}).data
who_to_follow = {
    'name': 'Who to follow',
    'data': follower
}
