# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remov` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.core.serializers import json
from django.db import models
from bookiebot.storage_backends import  PublicMediaStorage
import time


class AllowedFeaturesInSubscriptions(models.Model):
    plan = models.ForeignKey('SubscriptionPlans', models.DO_NOTHING)
    feature_list = models.CharField(max_length=255)
    is_active = models.IntegerField()
    is_deleted = models.IntegerField()
    added_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()

    class Meta:
        db_table = 'allowed_features_in_subscriptions'


class BookPagesMedia(models.Model):
    id = models.BigAutoField(primary_key=True)
    book = models.ForeignKey('UsersBooks', models.DO_NOTHING)
    page_no = models.IntegerField()
    pic_url = models.TextField()
    audio_url = models.TextField()
    added_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()

    class Meta:
        db_table = 'book_pages_media'


class Categories(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    is_active = models.IntegerField(default=1)
    is_deleted = models.IntegerField(default=0)
    added_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()

    class Meta:
        db_table = 'categories'

class CMS(models.Model):
    contact = models.TextField()
    terms = models.TextField()
    privacy = models.TextField()
    about = models.TextField()
    added_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()

    class Meta:
        db_table = 'cms'



class PointTransactions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    points = models.FloatField()
    type = models.IntegerField()
    description = models.CharField(max_length=255)
    transaction_date = models.BigIntegerField()

    class Meta:
        db_table = 'point_transactions'


class PostComments(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    post = models.ForeignKey('Posts', models.DO_NOTHING)
    parent_comment_id = models.BigIntegerField()
    comment_text = models.CharField(max_length=255)
    tag_user_id = models.CharField(max_length=255)
    comment_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()
    is_active = models.IntegerField(default=1)
    is_deleted = models.IntegerField(default=0)

    class Meta:
        db_table = 'post_comments'


class PostLikes(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey('Posts', models.DO_NOTHING)
    like_user = models.ForeignKey('Users', models.DO_NOTHING)
    like_on = models.BigIntegerField()

    class Meta:
        db_table = 'post_likes'


class PostReports(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey('Posts', models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    report_cat = models.CharField(max_length=255)
    report_desc = models.CharField(max_length=255)
    reported_on = models.BigIntegerField()

    class Meta:
        db_table = 'post_reports'


class Posts(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    post_text = models.TextField()
    media_url = models.CharField(max_length=255)
    media_typ = models.IntegerField()
    is_approved = models.IntegerField(default=0)
    is_reported = models.IntegerField(default=0)
    reported_count = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    is_deleted = models.IntegerField(default=0)
    added_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()
    parent_post_id = models.BigIntegerField(default=0)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'posts'


class UploadedFiles(models.Model):

    id = models.BigAutoField(primary_key=True)
    file = models.FileField(blank=False, null=False)
    storage = PublicMediaStorage()

    class Meta:
        db_table = 'uploaded_files'

class Users(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phn_no = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)
    users_pic = models.CharField(max_length=255, default="", blank=True, null=True)
    users_referral_code = models.CharField(max_length=255)
    social_id = models.CharField(max_length=255)
    social_id_type = models.CharField(max_length=255)
    bonous_points = models.FloatField(default=0)
    gender = models.CharField(max_length=10)
    child_name = models.CharField(max_length=255,default='')
    child_age = models.CharField(max_length=255,default='')
    is_active = models.IntegerField(default=1)
    user_role = models.IntegerField(default=0)
    is_blocked = models.IntegerField(default=0)
    is_deleted = models.IntegerField(default=0)
    created_at = models.BigIntegerField()
    updated_at = models.BigIntegerField()

    class Meta:
        db_table = 'users'

class UserLoggedIn(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    device_token = models.CharField(max_length=255, default='')
    device_id = models.CharField(max_length=255, default='')
    device_type = models.IntegerField() # 0 for ios 1 for android
    logged_in = models.BigIntegerField()

    class Meta:
        db_table = 'user_loggedin'


class UsersBooks(models.Model):
    id = models.BigAutoField(primary_key=True)
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255)
    book_publisher = models.CharField(max_length=255)
    number_of_pages = models.IntegerField()
    media_path = models.CharField(max_length=255)
    cover_pic_path = models.CharField(max_length=255)
    number_of_views = models.IntegerField(default=0)
    number_of_likes = models.IntegerField(default=0)
    is_admin = models.IntegerField(default=0)
    is_public = models.IntegerField(default=0)
    is_approved = models.IntegerField(default=1)
    type = models.IntegerField()
    added_by = models.ForeignKey(Users, models.CASCADE, db_column='added_by')
    is_active = models.IntegerField(default=1)
    is_deleted = models.IntegerField(default=0)
    added_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()

    class Meta:
        db_table = 'users_books'


class UsersBooksCategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    book = models.ForeignKey(UsersBooks, models.DO_NOTHING)
    cat = models.ForeignKey(Categories, models.DO_NOTHING)

    class Meta:
        db_table = 'users_books_categories'

class UserBookLikes(models.Model):
    id = models.BigAutoField(primary_key=True)
    book = models.ForeignKey(UsersBooks, models.DO_NOTHING)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    like_on = models.BigIntegerField()

    class Meta:
        db_table = 'user_book_likes'

class UserBookViews(models.Model):
    id = models.BigAutoField(primary_key=True)
    book = models.ForeignKey(UsersBooks, models.DO_NOTHING)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    view_on = models.BigIntegerField()

    class Meta:
        db_table = 'user_book_views'



class AppSettings(models.Model):
    id = models.BigAutoField(primary_key=True)
    lowest_version_ios = models.FloatField(default=1.0)
    lowest_version_android = models.FloatField(default=1.0)
    created_at = models.BigIntegerField(default=int(time.time()))
    updated_at = models.BigIntegerField(default=int(time.time()))
    class Meta:
        db_table = 'app_settings'



class UsersLibrary(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    book_id = models.ForeignKey(UsersBooks,models.DO_NOTHING)
    added_on = models.BigIntegerField()
    book_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'users_library'


class UsersSchedule(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Users, models.CASCADE)
    book_id = models.BigIntegerField()
    book_type = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    time = models.CharField(max_length=255)
    datetime_long = models.BigIntegerField()
    is_sent = models.IntegerField()
    added_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()

    class Meta:
        db_table = 'users_schedule'

class SubscriptionPlans(models.Model):
    name = models.CharField(max_length=255)
    amount = models.FloatField()
    expires_in = models.IntegerField()
    is_active = models.IntegerField()
    is_deleted = models.IntegerField()
    added_on = models.BigIntegerField()
    updated_on = models.BigIntegerField()

    #can add
    validity = models.IntegerField(null=True, blank=True) # validity will be in days like 30, 60

    class Meta:
        db_table = 'subscription_plans'


class Transactions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    item_id = models.BigIntegerField()
    description = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    transaction_date = models.BigIntegerField()
    item_type = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255)
    payment_mode = models.CharField(max_length=255)

    # can add amount
    amount = models.FloatField()
    used = models.BooleanField(default=False) # one transaction object cannot used multiple times 

    class Meta:
        db_table = 'transactions'


class UsersSubscriptions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    plan = models.ForeignKey(SubscriptionPlans, models.DO_NOTHING)
    subscribed_on = models.BigIntegerField()
    expires_on = models.BigIntegerField(null=True, blank=True)

    #can add
    payment = models.ForeignKey(Transactions, models.DO_NOTHING)
    isactive = models.BooleanField(default=False) #return false if plan is expired or already have active plan
    updated_at = models.BigIntegerField(blank=True, null=True)

    #can be removed ---------------
    # features_json = models.CharField(max_length=255)
    # expiration_in_days = models.IntegerField()
    # transaction_id = models.CharField(max_length=255)
    # payment_mode = models.IntegerField()
    # amount = models.FloatField() #for which amount user purchased plan
    #-------------------------

    class Meta:
        db_table = 'users_subscriptions'