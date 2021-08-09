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
    # class Meta:
    #     model = Users
    #     fields = "__all__"
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
        # user_id = self.context.get("user_id")
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

class BookPagesMediaSerializer(serializers.ModelSerializer):

    book_detail = serializers.SerializerMethodField('getBookDetail')
    book_category = serializers.SerializerMethodField('getBookCategory')


    def getBookDetail(self, userbook):
        booklist = UsersBooks.objects.filter(id=userbook.book.id)
        book = booklist[0]
        return {'book_id':book.id,'book_title':book.book_title,'book_author':book.book_author,'book_publisher':book.book_publisher,'media_path':book.media_path, 'cover_pic_path':book.cover_pic_path, 'number_of_views':book.number_of_views, 'number_of_likes':book.number_of_likes, 'is_public':book.is_public, 'is_approved':book.is_approved, 'type':book.type}

    def getBookCategory(self,userbook):
        booklist = UsersBooksCategories.objects.filter(book=userbook.book)

        book_category = booklist[0]
        dictdata = model_to_dict(book_category)
        return dictdata.get('cat')

    class Meta:
        model = BookPagesMedia
        fields = "__all__"

class PostsCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField('getUserName')
    user_pic = serializers.SerializerMethodField('getUserImage')
    child_comment = serializers.SerializerMethodField('getChildComment')
    def getUserName(self, postComment):
        #user_id = self.context.get("user_id")
        user = postComment.user.id
        try:
            userModel = Users.objects.get(id=user)
            return userModel.name
        except:
            return 'Not Available'

    def getUserImage(self, postComment):
        #user_id = self.context.get("user_id")
        user = postComment.user.id
        try:
            userModel = Users.objects.get(id=user)
            return userModel.users_pic
        except:
            return 'Not Available'

    def getChildComment(self, postComment):
        #user_id = self.context.get("user_id")
        user = postComment.user.id
        try:
            postcommentCount = PostComments.objects.filter(post=postComment.post, parent_comment_id=postComment.id).exclude(is_deleted=1)
            postcommentTemp = PostComments.objects.filter(post=postComment.post,
                                                          parent_comment_id=postComment.id).exclude(is_deleted=1)[0:2]
            serializer = PostsCommentSerializer(postcommentTemp, many=True)

            return {'count':len(postcommentCount), 'child':serializer.data}
        except:
            return {'count':0, 'child':[]}


    class Meta:
        model = PostComments
        fields = "__all__"


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFiles
        fields = "__all__"

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlans
        fields = "__all__"

class CMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = CMS
        fields = "__all__"

class UserSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsersSubscriptions
        fields = "__all__"