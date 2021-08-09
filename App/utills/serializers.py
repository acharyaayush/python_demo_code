from django.forms import model_to_dict
from rest_framework import serializers
from api.models import *


class CategorySerializer (serializers.ModelSerializer):
    total_books = serializers.SerializerMethodField('get_book_count')
    def get_book_count(self, cat):
        # user_id = self.context.get("user_id")
        cat_id = cat.id

        try:
            book_count = UsersBooksCategories.objects.filter(cat=cat).count()
            return book_count
        except:
            return 10
    class Meta:
        model = Categories
        fields = "__all__"


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

class PostSerializer(serializers.ModelSerializer):

    is_liked = serializers.SerializerMethodField('isLikedByMe')
    user_name = serializers.SerializerMethodField('getUserName')
    user_pic = serializers.SerializerMethodField('getUserImage')

    def getUserName(self, post):
        # user_id = self.context.get("user_id")
        user = post.user.id
        print(user)
        try:
            userModel = Users.objects.get(id=user)
            return userModel.name
        except:
            return 'Not Available'

    def getUserImage(self, post):
        user = post.user.id
        try:
            userModel = Users.objects.get(id=user)
            return userModel.users_pic
        except:
            return ''

    def isLikedByMe(self,post):
        user_id = self.context.get("user_id")
        postLike = PostLikes.objects.filter(post=post, like_user=user_id)
        return len(postLike) > 0

    class Meta:
        model = Posts
        fields = "__all__"


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLikes
        fields = "__all__"

class BooksSerializer(serializers.ModelSerializer):

    is_liked = serializers.SerializerMethodField('isLikedByMe')

    
    def isLikedByMe(self,book):
        user_id = self.context.get("user_id")
        bookLike = UsersLibrary.objects.filter(book_id=book.id, user=user_id)
        return len(bookLike) > 0

    class Meta:
        model = UsersBooks
        fields = "__all__"

class UsersLibrarySerializer(serializers.ModelSerializer):

    book_detail = serializers.SerializerMethodField('getBookDetail')
    def getBookDetail(self, userbook):
        booklist = UsersBooks.objects.filter(id=userbook.book_id.id)
        serializer = BooksSerializer(booklist, many=True)

        return serializer.data[0]

    class Meta:
        model = UsersLibrary
        fields = "__all__"

class UsersScheduleSerializer(serializers.ModelSerializer):
    book_detail = serializers.SerializerMethodField('getBookDetail')

    def getBookDetail(self, userbook):

        booklist = UsersBooks.objects.filter(id=userbook.book_id)
        serializer = BooksSerializer(booklist, many=True)

        return serializer.data[0]
    class Meta:
        model = UsersSchedule
        fields = "__all__"


class UserBookViewSerializer(serializers.ModelSerializer):

    book_type = serializers.SerializerMethodField('getBookType')
    book_detail = serializers.SerializerMethodField('getBookDetail')


    def getBookType(self, userbook):
        return 0

    def getBookDetail(self, userbook):

        booklist = UsersBooks.objects.filter(id=userbook.book.id)
        serializer = BooksSerializer(booklist, many=True)

        return serializer.data[0]

    class Meta:
        model = UserBookViews
        fields = "__all__"




class PostsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReports
        fields = "__all__"
