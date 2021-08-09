from rest_framework import serializers
from api.models import *


class UserSerializer (serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
    phn_no = serializers.CharField(max_length=255)
    pin = serializers.CharField(max_length=10)
    users_pic = serializers.CharField(max_length=255)
    users_referral_code = serializers.CharField(max_length=255)
    social_id = serializers.CharField(max_length=255)
    social_id_type = serializers.CharField(max_length=255)
    bonous_points = serializers.FloatField()
    gender = serializers.CharField()
    child_name = serializers.CharField()
    child_age = serializers.CharField()
    is_active = serializers.IntegerField()
    user_role = serializers.IntegerField()
    is_blocked = serializers.IntegerField()
    is_deleted = serializers.IntegerField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()

    def create(self, validated_data):
        return Users.objects.create(**validated_data)



class UsersScheduleSerializer(serializers.ModelSerializer):
    book_detail = serializers.SerializerMethodField('getBookDetail')

    def getBookDetail(self, userbook):

        booklist = UsersBooks.objects.filter(id=userbook.book_id)
        serializer = BooksSerializer(booklist, many=True)

        return serializer.data[0]
    class Meta:
        model = UsersSchedule
        fields = "__all__"


