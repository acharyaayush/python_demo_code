from django.db import models
from bookiebot.storage_backends import  PublicMediaStorage


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



