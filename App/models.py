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



