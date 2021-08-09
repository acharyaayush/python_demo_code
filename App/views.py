import hashlib
import time

from django.core.mail import send_mail
from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from rest_framework.views import View, APIView
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView

from api.controller.bookie import CMSController
from api.controller.category_module import CategoryController
from api.controller.post_module import PostController
from api.controller.books_module import BooksController
from api.controller.schedule_books_module import ScheduleController
from api.controller.subscription_module import SubscriptionController
from api.controller.user_subscriptions import UserSubscriptionController
from api.controller.transaction_module import TransactionController

from api.models import Users, Categories, AppSettings, Posts, UserLoggedIn
from api.utills import constants
from api.utills.response import ok_response, createNewPassword, modify_input_for_multiple_files
from api.controller.users import UserController
import jwt
from api.utills.serializers import CategorySerializer, UserSerializer, FileSerializer
from bookiebot.settings import EMAIL_HOST_USER
from rest_framework.schemas.openapi import SchemaGenerator
import json
import requests
from bs4 import BeautifulSoup
from django.forms import model_to_dict
import xmltodict
import io
from rest_framework.parsers import JSONParser
from api.utills.swagger_schema import LoginViewSchema, BookAPISchema
from rest_framework.schemas import AutoSchema
import coreapi


@api_view(['GET', 'POST', 'DELETE'])
def get_version(request):
    if request.method == 'GET':
        app_settings = AppSettings.objects.all()
        if len(app_settings) > 0:
            last_obj = list(app_settings)[-1]

            return ok_response({"lowest_version_ios": last_obj.lowest_version_ios, "lowest_version_android": last_obj.lowest_version_android})
        else:
            return ok_response({"lowest_version_ios": 1.0, "lowest_version_android": 1.0})


def add_latest_version(request):
    if request.method == 'POST':
        print(request.POST)
        app_settings = AppSettings()
        app_settings.lowest_version_ios = float(
            request.POST.get('version_ios'))
        app_settings.lowest_version_android = float(
            request.POST.get('version_android'))
        app_settings.updated_at = int(time.time())
        app_settings.created_at = int(time.time())
        app_settings.save()
        return ok_response({"lowest_version_ios": app_settings.lowest_version_ios, "lowest_version_android": app_settings.lowest_version_android})


class LoginView(APIView):
    schema = LoginViewSchema()

    def post(self, request):
        print(request.data)
        if request.POST.get('email') is None or not request.POST.get('email'):
            return ok_response([], message="Email is required", code=201)
        if request.POST.get('password') is None or not request.POST.get('password'):
            return ok_response([], message="Password is required", code=201)
        if request.POST.get('device_token') is None or not request.POST.get('device_token'):
            return ok_response([], message="Device Token is required", code=201)
        if request.POST.get('device_id') is None or not request.POST.get('device_id'):
            return ok_response([], message="Device ID is required", code=201)
        if request.POST.get('device_type') is None or not request.POST.get('device_type'):
            return ok_response([], message="Device Type is required", code=201)

        try:

            user = Users.objects.get(email=request.POST.get('email'))
            pass_obj = hashlib.md5(request.POST.get('password').encode())

            if user.password == request.POST.get('password'):

                userdict = {'id': user.id, 'name': user.name, 'email': user.email, 'users_pic': user.users_pic,
                            'user_role': user.user_role}
                encoded = jwt.encode(
                    userdict, constants.jwt_key, algorithm=constants.jwt_algorithm)
                userloggedin = UserLoggedIn.objects.filter(user_id=user.id, device_id=request.POST.get('device_id'),
                                                           device_token=request.POST.get(
                                                               'device_token'),
                                                           device_type=request.POST.get('device_type'))
                if len(userloggedin) == 0:
                    userlogged = UserLoggedIn()
                    userlogged.device_id = request.POST.get('device_id')
                    userlogged.device_token = request.POST.get('device_token')
                    userlogged.device_type = request.POST.get('device_type')
                    userlogged.user_id = user.id
                    userlogged.logged_in = int(time.time())
                    userlogged.save()
                resp = {'id': user.id, 'token': encoded.decode("utf-8")}
                return ok_response(resp, code=200)
            else:
                return ok_response([], message="Wrong password", code=201)
        except Users.DoesNotExist:

            return ok_response([], message="This email doesn't exist", code=201)

    def delete(self, request):

        reques_data = request.data

        if reques_data.get('device_token') is None or not reques_data.get('device_token'):
            return ok_response([], message="Device Token is required", code=201)
        if reques_data.get('device_id') is None or not reques_data.get('device_id'):
            return ok_response([], message="Device ID is required", code=201)
        if reques_data.get('device_type') is None or not reques_data.get('device_type'):
            return ok_response([], message="Device Type is required", code=201)

        userloggedin = UserLoggedIn.objects.filter(device_id=reques_data.get('device_id'),
                                                   device_token=reques_data.get(
                                                       'device_token'),
                                                   device_type=reques_data.get('device_type'))
        if len(userloggedin) > 0:
            userlogged = userloggedin[0]
            userlogged.delete()
            return ok_response([], message="Device Logged out successfully", code=200)
        else:
            return ok_response([], message="Device Details not found", code=202)


class SocialLoginView(APIView):

    def post(self, request):

        if request.POST.get('social_id') is None or not request.POST.get('social_id'):
            return ok_response([], message="Social ID is required", code=201)
        if request.POST.get('email') is None or not request.POST.get('email'):
            return ok_response([], message="Email is required", code=201)
        if request.POST.get('social_id_type') is None or not request.POST.get('social_id_type'):
            return ok_response([], message="Social ID Type is required", code=201)
        if request.POST.get('device_token') is None or not request.POST.get('device_token'):
            return ok_response([], message="Device Token is required", code=201)
        if request.POST.get('device_id') is None or not request.POST.get('device_id'):
            return ok_response([], message="Device ID is required", code=201)
        if request.POST.get('device_type') is None or not request.POST.get('device_type'):
            return ok_response([], message="Device Type is required", code=201)

        # user = Users.objects.filter(email=request.POST.get('email'), password=request.POST.get('password'))

        try:
            user = Users.objects.get(Q(social_id=request.POST.get(
                'social_id')) | Q(email=request.POST.get('email')))
            if user.user_role == 0:
                userdict = {'id': user.id, 'name': user.name, 'email': user.email, 'users_pic': user.users_pic,
                            'user_role': user.user_role}
                encoded = jwt.encode(
                    userdict, constants.jwt_key, algorithm=constants.jwt_algorithm)
                userloggedin = UserLoggedIn.objects.filter(user_id=user.id, device_id=request.POST.get('device_id'),
                                                           device_token=request.POST.get(
                                                               'device_token'),
                                                           device_type=request.POST.get('device_type'))
                if len(userloggedin) == 0:
                    userlogged = UserLoggedIn()
                    userlogged.device_id = request.POST.get('device_id')
                    userlogged.device_token = request.POST.get('device_token')
                    userlogged.device_type = request.POST.get('device_type')
                    userlogged.user_id = user.id
                    userlogged.logged_in = int(time.time())
                    userlogged.save()
                resp = {'id': user.id, 'token': encoded.decode("utf-8")}
                return ok_response(resp)
            else:
                return ok_response([], message="Sorry, No user account is linked with this social id", code=201)

        except Users.DoesNotExist:
            usernew = Users()
            usernew.email = request.POST.get('email')
            usernew.user_role = '0'
            usernew.phn_no = ''
            usernew.password = ''
            usernew.social_id = request.POST.get('social_id')
            usernew.social_id_type = request.POST.get('social_id_type')
            usernew.save()
            userdict = {'id': usernew.id, 'name': usernew.name, 'email': usernew.email, 'users_pic': usernew.users_pic,
                        'user_role': usernew.user_role}
            encoded = jwt.encode(userdict, constants.jwt_key,
                                 algorithm=constants.jwt_algorithm)
            userloggedin = UserLoggedIn.objects.filter(user_id=usernew.id, device_id=request.POST.get('device_id'),
                                                       device_token=request.POST.get(
                                                           'device_token'),
                                                       device_type=request.POST.get('device_type'))
            if len(userloggedin) == 0:
                userlogged = UserLoggedIn()
                userlogged.device_id = request.POST.get('device_id')
                userlogged.device_token = request.POST.get('device_token')
                userlogged.device_type = request.POST.get('device_type')
                userlogged.user_id = usernew.id
                userlogged.logged_in = int(time.time())
                userlogged.save()
            resp = {'id': usernew.id, 'token': encoded.decode("utf-8")}
            return ok_response(resp, code=202)


class AdminLoginView(APIView):

    def post(self, request):

        if request.POST.get('email') is None or not request.POST.get('email'):
            return ok_response([], message="Email is required", code=201)
        if request.POST.get('password') is None or not request.POST.get('password'):
            return ok_response([], message="Password is required", code=201)

        # user = Users.objects.filter(email=request.POST.get('email'), password=request.POST.get('password'))

        try:
            user = Users.objects.get(email=request.POST.get('email'))
            if user.user_role == 1:
                pass_obj = hashlib.md5(request.POST.get('password').encode())

                if user.password == pass_obj.hexdigest():
                    userdict = {'id': user.id, 'name': user.name, 'email': user.email, 'users_pic': user.users_pic,
                                'user_role': user.user_role}
                    encoded = jwt.encode(
                        userdict, constants.jwt_key, algorithm=constants.jwt_algorithm)

                    resp = {'id': user.id, 'token': encoded.decode("utf-8")}
                    return ok_response(resp, code=200)
                else:
                    return ok_response([], message="Wrong password", code=201)
            else:
                return ok_response([], message="Sorry, No Admin account found linked with this email", code=201)

        except Users.DoesNotExist:
            return ok_response([], message="This email doesn't exist", code=201)


class ForgotPasswordView(APIView):
    def post(self, request):

        if request.POST.get('email') is None or not request.POST.get('email'):
            return ok_response([], message="Email is required", code=201)

        try:
            user = Users.objects.get(email=request.POST.get('email'))
            newpass = createNewPassword()
            new_pass_obj = hashlib.md5(newpass.encode())
            user.password = new_pass_obj.hexdigest()
            user.updated_at = int(time.time())
            user.save()
            subject = 'Bookiebot: Password Changed!'
            message = 'Hello, your request to change password is successful. your new password is :' + newpass
            recepient = request.POST.get('email')
            send_mail(subject, message, EMAIL_HOST_USER,
                      [recepient], fail_silently=False)
            return ok_response([], message="Recovery Email sent to " + request.POST.get('email'))

        except Users.DoesNotExist:
            return ok_response([], message="This email doesn't exist", code=201)


class UploadFile(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request):
        images = dict((request.data).lists())['file']
        flag = 1
        arr = []
        for img_name in images:
            print('abc')
            modified_data = modify_input_for_multiple_files(img_name)
            file_serializer = FileSerializer(data=modified_data)
            if file_serializer.is_valid():
                file_serializer.save()
                arr.append(file_serializer.data)
                print('array')
                print(arr)
                print('==============')
            else:
                flag = 0

        if flag == 1:
            return ok_response(arr, code=200)
        else:
            return ok_response([], message="Images not uploaded ", code=201)


class UserView(APIView):

    def get(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)

                if request.GET.get('id') is None or not request.GET.get('id'):
                    if request.GET.get('page') is None or not request.GET.get('page'):
                        return ok_response([], message="Page is required", code=201)
                    if request.GET.get('size') is None or not request.GET.get('size'):
                        return ok_response([], message="Size is required", code=201)
                    if int(request.GET.get('size')) == 0:
                        if request.GET.get('active') is None or not request.GET.get('active'):
                            user = Users.objects.all()
                        else:
                            user = Users.objects.filter(
                                is_active=1).exclude(is_deleted=1)
                        serializer = UserSerializer(user, many=True)
                        return ok_response(serializer.data, code=200)
                    else:
                        if request.GET.get('active') is None or not request.GET.get('active'):
                            user = Users.objects.all()[(int(request.GET.get('page')) * int(request.GET.get('size'))):(
                                int(request.GET.get('size')) * (int(request.GET.get('page')) + 1))]
                        else:
                            user = Users.objects.filter(is_active=1).exclude(is_deleted=1)[(int(request.GET.get('page')) * int(request.GET.get('size'))):(
                                int(request.GET.get('size')) * (int(request.GET.get('page')) + 1))]
                        serializer = UserSerializer(user, many=True)
                        return ok_response(serializer.data, code=200)
                else:
                    try:
                        user = Users.objects.get(id=request.GET.get('id'))
                        serializer = UserSerializer([user], many=True)

                        return ok_response(serializer.data[0], code=200)
                    except Users.DoesNotExist:
                        return ok_response([], message="No user found", code=201)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def post(self, request):

        reques_data = request.POST

        if reques_data.get('email') is None or not reques_data.get('email'):
            return ok_response([], message="Email is required", code=201)
        if reques_data.get('user_role') is None or not reques_data.get('user_role'):
            return ok_response([], message="User Role is required", code=201)
        if request.POST.get('device_token') is None or not request.POST.get('device_token'):
            return ok_response([], message="Device Token is required", code=201)
        if request.POST.get('device_id') is None or not request.POST.get('device_id'):
            return ok_response([], message="Device ID is required", code=201)
        if request.POST.get('device_type') is None or not request.POST.get('device_type'):
            return ok_response([], message="Device Type is required", code=201)

        if reques_data.get('social_id') is None:
            if reques_data.get('phn_no') is None or not reques_data.get('phn_no'):
                return ok_response([], message="Phone number is required", code=201)
            if reques_data.get('password') is None or not reques_data.get('password'):
                return ok_response([], message="Password is required", code=201)
        else:
            if reques_data.get('social_id_type') is None:
                return ok_response([], message="Social ID Type is required, pass ''(blank) if not used", code=201)

        user_controleler = UserController()
        user, isexist = user_controleler.create_user_object(reques_data)

        if isexist:
            return ok_response(user, code=201, message='User already exist')
        else:
            return ok_response(user, code=200)

    def put(self, request):

        reques_data = request.data
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(header, constants.jwt_key, algorithms=[
                                      constants.jwt_algorithm])

                if reques_data.get('id') is None or not reques_data.get('id'):
                    return ok_response([], message="User ID is required", code=201)
                if int(userdict['id']) == int(reques_data.get('id')) or int(userdict['user_role']) == 1:
                    user_controller = UserController()
                    return user_controller.update_user(reques_data)

                else:
                    return ok_response([], message="Unauthorize", code=403)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)

                reques_data = request.data
                if reques_data.get('id') is None or not reques_data.get('id'):
                    return ok_response([], message="User ID is required", code=201)
                if int(userdict['id']) == int(reques_data.get('id')) or int(userdict['user_role']) == 1:
                    user_controller = UserController()
                    return user_controller.delete_user(reques_data)

                else:
                    return ok_response([], message="Unauthorize", code=403)
            except:
                return ok_response([], message="Unauthorize", code=403)


class CategoryView(APIView):

    def get(self, request):

        # if request.GET.get('id') is None or not request.GET.get('id'):
        #
        #     category = Categories.objects.filter(is_active= 1).exclude(is_deleted= 1)
        #     serializer = CategorySerializer(category, many=True)
        #     return ok_response(serializer.data, code=200)
        # else:
        #
        #     category = Categories.objects.get(id=request.GET.get('id'))
        #     if category.is_deleted:
        #         return ok_response([],message="No Category Found", code=200)
        #     else:
        #         return ok_response(model_to_dict(category), code=200)

        if request.GET.get('id') is None or not request.GET.get('id'):
            if request.GET.get('page') is None or not request.GET.get('page'):
                return ok_response([], message="Page is required", code=201)
            if request.GET.get('size') is None or not request.GET.get('size'):
                return ok_response([], message="Size is required", code=201)
            if int(request.GET.get('size')) == 0:
                if request.GET.get('active') is None or not request.GET.get('active'):
                    category = Categories.objects.all().order_by('-updated_on')
                else:
                    category = Categories.objects.filter(is_active=1).exclude(
                        is_deleted=1).order_by('-updated_on')
                serializer = CategorySerializer(category, many=True)
                return ok_response(serializer.data, code=200)
            else:
                if request.GET.get('active') is None or not request.GET.get('active'):
                    category = Categories.objects.all().order_by('-updated_on')[(int(request.GET.get('page')) * int(request.GET.get('size'))):(
                        int(request.GET.get('size')) * (int(request.GET.get('page')) + 1))]
                else:
                    category = Categories.objects.filter(is_active=1).exclude(is_deleted=1).order_by('-updated_on')[(int(request.GET.get('page')) * int(request.GET.get('size'))):(
                        int(request.GET.get('size')) * (int(request.GET.get('page')) + 1))]
                serializer = CategorySerializer(category, many=True)
                return ok_response(serializer.data, code=200)
        else:
            try:
                category = Categories.objects.get(id=request.GET.get('id'))
                if category.is_deleted:
                    return ok_response([], message="Category has been deleted", code=201)
                else:
                    serializer = CategorySerializer([category], many=True)
                    return ok_response(serializer.data, code=200)
            except Categories.DoesNotExist:
                return ok_response([], message="No category found", code=201)

    def post(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)

                reques_data = request.POST

                if reques_data.get('name') is None or not reques_data.get('name'):
                    return ok_response([], message="Category name is required", code=201)
                if reques_data.get('icon') is None or not reques_data.get('icon'):
                    return ok_response([], message="Category Icon is required", code=201)
                if int(userdict['user_role']) == 0:
                    return ok_response([], message="Unauthorize", code=403)
                else:
                    cat_controller = CategoryController()
                    return cat_controller.create_category(reques_data)

            except:
                return ok_response([], message="Unauthorize", code=403)

    def put(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data

                if reques_data.get('id') is None or not reques_data.get('id'):
                    return ok_response([], message="Category ID is required", code=201)
                if int(userdict['user_role']) == 0:
                    return ok_response([], message="Unauthorize", code=403)
                else:
                    cat_controller = CategoryController()
                    return cat_controller.update_category(reques_data)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                if reques_data.get('id') is None or not reques_data.get('id'):
                    return ok_response([], message="Category ID is required", code=201)
                if int(userdict['user_role']) == 0:
                    return ok_response([], message="Unauthorize", code=403)
                else:
                    cat_controller = CategoryController()
                    return cat_controller.delete_category(reques_data)
            except:
                return ok_response([], message="Unauthorize", code=403)


class CategorySearchAPI(APIView):
    def get(self, request):
        reques_data = request.GET

        if reques_data.get('keyword') is None:
            return ok_response([], message="Keyword is required", code=201)
        if reques_data.get('page') is None or not reques_data.get('page'):
            return ok_response([], message="Page is required", code=201)
        if reques_data.get('size') is None or not reques_data.get('size'):
            return ok_response([], message="Size is required", code=201)

        if reques_data.get('active') is None:
            return ok_response([], message="Active Key is required", code=201)

        cat_controller = CategoryController()
        return cat_controller.search_category(reques_data)


class UserSearchAPI(APIView):
    def get(self, request):
        reques_data = request.GET

        if reques_data.get('keyword') is None:
            return ok_response([], message="Keyword is required", code=201)
        if request.GET.get('page') is None or not request.GET.get('page'):
            return ok_response([], message="Page is required", code=201)
        if request.GET.get('size') is None or not request.GET.get('size'):
            return ok_response([], message="Size is required", code=201)
        if reques_data.get('active') is None:
            return ok_response([], message="Active Key is required", code=201)
        if reques_data.get('to_date') is None:
            return ok_response([], message="To Date is required", code=201)
        if reques_data.get('from_date') is None:
            return ok_response([], message="From Date is required", code=201)

        cat_controller = UserController()
        return cat_controller.search_user(reques_data)


class StatisticsAPI(APIView):
    def get(self, request):
        reques_data = request.GET
        if reques_data.get('active') is None or not reques_data.get('active'):
            user = Users.objects.all().count()
            cat = Categories.objects.all().count()
            post = Posts.objects.all().count()
            resp = {'user_count': user, 'cat_count': cat, 'post_count': post}
            return ok_response(resp, code=200)
        else:
            if int(reques_data.get('active')) == 0:

                user = Users.objects.filter(
                    Q(is_deleted=1) or Q(is_active=0)).count()
                cat = Categories.objects.filter(
                    Q(is_deleted=1) or Q(is_active=0)).count()
                post = Posts.objects.filter(
                    Q(is_deleted=1) or Q(is_active=0)).count()
                resp = {'user_count': user,
                        'cat_count': cat, 'post_count': post}
                return ok_response(resp, code=200)
            else:

                user = Users.objects.filter(
                    Q(is_deleted=0) or Q(is_active=1)).count()
                cat = Categories.objects.filter(
                    Q(is_deleted=0) or Q(is_active=1)).count()
                post = Posts.objects.filter(
                    Q(is_deleted=0) or Q(is_active=1)).count()
                resp = {'user_count': user,
                        'cat_count': cat, 'post_count': post}
                return ok_response(resp, code=200)


class PasswordAPI(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                if reques_data.get('id') is None or not reques_data.get('id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('old_password') is None or not reques_data.get('old_password'):
                    return ok_response([], message="Old Password is required", code=201)
                if reques_data.get('new_password') is None or not reques_data.get('new_password'):
                    return ok_response([], message="New Password is required", code=201)
                if int(userdict['id']) == int(reques_data.get('id')) or int(userdict['user_role']) == 1:

                    user_controller = UserController()
                    return user_controller.change_password(reques_data)
                else:
                    return ok_response([], message="Unauthorize", code=403)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def put(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                if reques_data.get('id') is None or not reques_data.get('id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('new_password') is None or not reques_data.get('new_password'):
                    return ok_response([], message="New Password is required", code=201)
                if int(userdict['user_role']) == 0:
                    return ok_response([], message="Unauthorize", code=403)
                else:
                    user_controller = UserController()
                    return user_controller.change_password_forcefully(reques_data)
            except:
                return ok_response([], message="Unauthorize", code=403)


class PostAPI(APIView):

    def get(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET

                if reques_data.get('id') is None or not reques_data.get('id'):
                    if reques_data.get('page') is None or not reques_data.get('page'):
                        return ok_response([], message="Page is required", code=201)
                    if reques_data.get('size') is None or not reques_data.get('size'):
                        return ok_response([], message="Size is required", code=201)

                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)

                post_controller = PostController()
                return post_controller.checkPost(reques_data)
            except:
                ok_response([], message="Unauthorize", code=403)

    def post(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST

                if int(userdict['id']) == int(reques_data.get('id')) or int(userdict['user_role']) == 1:
                    if reques_data.get('id') is None or not reques_data.get('id'):
                        return ok_response([], message="User ID is required", code=201)
                    if reques_data.get('media_typ') is None or not reques_data.get('media_typ'):
                        return ok_response([], message="Media Type is required", code=201)

                    if int(reques_data.get('media_typ')) == 2:
                        if reques_data.get('text') is None or not reques_data.get('text'):
                            return ok_response([], message="Post Text is required", code=201)
                        if reques_data.get('media_url') is None:
                            return ok_response([], message="Media URL is required", code=201)
                    else:
                        if reques_data.get('text') is None:
                            return ok_response([], message="Post Text is required", code=201)
                        if reques_data.get('media_url') is None or not reques_data.get('media_url'):
                            return ok_response([], message="Media URL is required", code=201)

                    post_controller = PostController()
                    post = post_controller.create(reques_data)
                    return post
                else:
                    return ok_response([], message="Unauthorize", code=403)

            except:
                return ok_response([], message="Unauthorize", code=403)

    def put(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data

                if reques_data.get('id') is None or not reques_data.get('id'):
                    return ok_response([], message="Post ID is required", code=201)

                if int(userdict['user_role']) == 1:

                    post_controller = PostController()
                    return post_controller.update(reques_data)
                else:
                    return ok_response([], message="Unauthorize", code=403)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                if reques_data.get('id') is None or not reques_data.get('id'):
                    return ok_response([], message="Post ID is required", code=201)
                if int(userdict['user_role']) == 1:
                    post_controller = PostController()
                    return post_controller.delete(reques_data)
                else:
                    return ok_response([], message="Unauthorize", code=403)
            except:
                return ok_response([], message="Unauthorize", code=403)


class AdminPost(APIView):

    def put(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data

                if reques_data.get('status') is None or not reques_data.get('status'):
                    return ok_response([], message="Change status is required", code=201)
                if int(userdict['user_role']) == 1:
                    post_controller = PostController()
                    return post_controller.approve_status(reques_data)
                else:
                    return ok_response([], message="Unauthorize", code=403)
            except:
                return ok_response([], message="Unauthorize", code=403)


class PostLikeAPI(APIView):

    def get(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET
                if reques_data.get('post_id') is None or not reques_data.get('post_id'):
                    return ok_response([], message="Post ID is required", code=201)
                reques_data = request.GET
                post_controller = PostController()
                return post_controller.checkPostLikeCount(reques_data)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST

                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('post_id') is None or not reques_data.get('post_id'):
                    return ok_response([], message="Post ID is required", code=201)

                post_controller = PostController()
                post = post_controller.likepost(reques_data)
                return post
            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('post_id') is None or not reques_data.get('post_id'):
                    return ok_response([], message="Post ID is required", code=201)

                post_controller = PostController()
                return post_controller.deletelikedpost(reques_data)
            except:
                return ok_response([], message="Unauthorize", code=403)


class PostCommentAPI(APIView):

    def get(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET
                if reques_data.get('post_id') is None or not reques_data.get('post_id'):
                    return ok_response([], message="Post ID is required", code=201)

                post_controller = PostController()
                return post_controller.checkPostCommentCount(reques_data)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST

                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('post_id') is None or not reques_data.get('post_id'):
                    return ok_response([], message="Post ID is required", code=201)
                if reques_data.get('parent_comment_id') is None or not reques_data.get('parent_comment_id'):
                    return ok_response([], message="Parent comment id is required", code=201)
                if reques_data.get('comment_text') is None or not reques_data.get('comment_text'):
                    return ok_response([], message="Comment text is required", code=201)
                if reques_data.get('tag_user_id') is None or not reques_data.get('tag_user_id'):
                    return ok_response([], message="Tag User ID is required", code=201)

                post_controller = PostController()
                post = post_controller.commentPost(reques_data)
                return post
            except:
                return ok_response([], message="Unauthorize", code=403)

    def put(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data

                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('comment_id') is None or not reques_data.get('comment_id'):
                    return ok_response([], message="Comment ID is required", code=201)
                if reques_data.get('comment_text') is None or not reques_data.get('comment_text'):
                    return ok_response([], message="Comment text is required", code=201)
                post_controller = PostController()
                post = post_controller.updatecomment(reques_data)
                return post
            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('comment_id') is None or not reques_data.get('comment_id'):
                    return ok_response([], message="Comment ID is required", code=201)

                post_controller = PostController()
                return post_controller.deletecomment(reques_data)
            except:
                return ok_response([], message="Unauthorize", code=403)


class CommentThreadAPI(APIView):

    def get(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET
                if reques_data.get('comment_id') is None or not reques_data.get('comment_id'):
                    return ok_response([], message="Comment ID is required", code=201)
                if reques_data.get('page') is None or not reques_data.get('page'):
                    return ok_response([], message="Page is required", code=201)
                if reques_data.get('size') is None or not reques_data.get('size'):
                    return ok_response([], message="Size is required", code=201)

                post_controller = PostController()
                return post_controller.getthreadcomment(reques_data)
            except:
                return ok_response([], message="Unauthorize", code=403)


class PostReportAPI(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST

                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('post_id') is None or not reques_data.get('post_id'):
                    return ok_response([], message="Post ID is required", code=201)
                if reques_data.get('description') is None or not reques_data.get('description'):
                    return ok_response([], message="Description is required", code=201)
                if reques_data.get('category') is None or not reques_data.get('category'):
                    return ok_response([], message="Report category is required", code=201)

                post_controller = PostController()
                post = post_controller.reportpost(reques_data)
                return post
            except:
                return ok_response([], message="Unauthorize", code=403)


class PostShareAPI(APIView):

    def get(self, request):
        reques_data = request.GET
        if reques_data.get('post_id') is None or not reques_data.get('post_id'):
            return ok_response([], message="Post ID is required", code=201)

        return ok_response([], message="Unauthorize", code=403)

    def post(self, request):

        reques_data = request.POST
        return ok_response([], message="Unauthorize", code=403)
        if reques_data.get('user_id') is None or not reques_data.get('user_id'):
            return ok_response([], message="User ID is required", code=201)
        if reques_data.get('post_id') is None or not reques_data.get('post_id'):
            return ok_response([], message="Post ID is required", code=201)
        if reques_data.get('parent_comment_id') is None or not reques_data.get('parent_comment_id'):
            return ok_response([], message="Parent comment id is required", code=201)
        if reques_data.get('comment_text') is None or not reques_data.get('comment_text'):
            return ok_response([], message="Comment text is required", code=201)
        if reques_data.get('tag_user_id') is None or not reques_data.get('tag_user_id'):
            return ok_response([], message="Tag User ID is required", code=201)

        post_controller = PostController()
        post = post_controller.commentPost(reques_data)
        return post

    def put(self, request):

        reques_data = request.data
        return ok_response([], message="Unauthorize", code=403)
        if reques_data.get('user_id') is None or not reques_data.get('user_id'):
            return ok_response([], message="User ID is required", code=201)
        if reques_data.get('comment_id') is None or not reques_data.get('comment_id'):
            return ok_response([], message="Comment ID is required", code=201)
        if reques_data.get('comment_text') is None or not reques_data.get('comment_text'):
            return ok_response([], message="Comment text is required", code=201)
        post_controller = PostController()
        post = post_controller.updatecomment(reques_data)
        return post

    def delete(self, request):

        reques_data = request.data
        return ok_response([], message="Unauthorize", code=403)
        if reques_data.get('user_id') is None or not reques_data.get('user_id'):
            return ok_response([], message="User ID is required", code=201)
        if reques_data.get('comment_id') is None or not reques_data.get('comment_id'):
            return ok_response([], message="Comment ID is required", code=201)

        post_controller = PostController()
        return post_controller.deletecomment(reques_data)


class BooksAPI(APIView):
    schema = BookAPISchema()

    def patch(self, request):

        if not 'authorization' in request.headers.keys():

            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                book_controller = BooksController()

                return book_controller.getallBooks(reques_data)
            except:
                return ok_response([], message="Unauthorized", code=403)

    def post(self, request):

        if not 'authorization' in request.headers.keys():

            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)
                if reques_data.get('cat_id') is None or not reques_data.get('cat_id'):
                    return ok_response([], message="Category ID is required", code=201)
                if reques_data.get('title') is None or not reques_data.get('title'):
                    return ok_response([], message="Title is required", code=201)
                if reques_data.get('author') is None or not reques_data.get('author'):
                    return ok_response([], message="Author is required", code=201)
                if reques_data.get('publisher') is None or not reques_data.get('publisher'):
                    return ok_response([], message="Publisher is required", code=201)
                if reques_data.get('pages') is None or not reques_data.get('pages'):
                    return ok_response([], message="Number of pages is required", code=201)
                if reques_data.get('media_path') is None:
                    return ok_response([], message="Media path is required", code=201)
                if reques_data.get('cover_pic_path') is None or not reques_data.get('cover_pic_path'):
                    return ok_response([], message="Cover pic path is required", code=201)
                if reques_data.get('public') is None or not reques_data.get('public'):
                    return ok_response([], message="Public key is required", code=201)
                if reques_data.get('type') is None or not reques_data.get('type'):
                    return ok_response([], message="Type is required", code=201)
                if reques_data.get('pic_url') is None or not reques_data.get('pic_url'):
                    return ok_response([], message="Pic URLs is required", code=201)
                if reques_data.get('audio_url') is None or not reques_data.get('audio_url'):
                    return ok_response([], message="Audio URLs is required", code=201)
                book_controller = BooksController()

                return book_controller.createBook(reques_data, int(userdict['user_role']))
            except:
                return ok_response([], message="Unauthorize", code=403)

    def put(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                book_controller = BooksController()

                return book_controller.updatebook(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                # in delete api swagger gives params in query
                reques_data = request.query_params

                if reques_data.get('book_id') is None or not reques_data.get('book_id'):
                    return ok_response([], message="Book ID is required", code=201)

                book_controller = BooksController()
                return book_controller.deleteBookUser(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=403)


class BookLikeAPI(APIView):

    def get(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET
                if reques_data.get('page') is None or not reques_data.get('page'):
                    return ok_response([], message="Page is required", code=201)
                if reques_data.get('size') is None or not reques_data.get('size'):
                    return ok_response([], message="Size is required", code=201)
                if reques_data.get('keyword') is None:
                    return ok_response([], message="Keyword is required", code=201)

                book_controller = BooksController()
                return book_controller.getlikedBook(reques_data, userdict['id'])

            except:
                return ok_response([], message="Unauthorize", code=403)

    def post(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                if reques_data.get('book_id') is None or not reques_data.get('book_id'):
                    return ok_response([], message="Book ID is required", code=201)
                if reques_data.get('book_type') is None or not reques_data.get('book_type'):
                    return ok_response([], message="Book Type is required", code=201)
                book_controller = BooksController()
                return book_controller.likeBook(reques_data, userdict['id'])
            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data

                if reques_data.get('book_id') is None or not reques_data.get('book_id'):
                    return ok_response([], message="Book ID is required", code=201)
                if reques_data.get('book_type') is None or not reques_data.get('book_type'):
                    return ok_response([], message="Book Type is required", code=201)

                book_controller = BooksController()
                return book_controller.unlikeBook(reques_data, userdict['id'])

            except:
                return ok_response([], message="Unauthorize", code=403)


class BookViewAPI(APIView):

    def get(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET
                if reques_data.get('page') is None or not reques_data.get('page'):
                    return ok_response([], message="Page is required", code=201)
                if reques_data.get('size') is None or not reques_data.get('size'):
                    return ok_response([], message="Size is required", code=201)
                if reques_data.get('keyword') is None:
                    return ok_response([], message="Keyword is required", code=201)

                book_controller = BooksController()
                return book_controller.getviewedBook(reques_data, userdict['id'])

            except:
                return ok_response([], message="Unauthorize", code=403)

    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                if reques_data.get('book_id') is None or not reques_data.get('book_id'):
                    return ok_response([], message="Book ID is required", code=201)

                book_controller = BooksController()
                return book_controller.viewBook(reques_data, userdict['id'])

            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                if reques_data.get('book_id') is None or not reques_data.get('book_id'):
                    return ok_response([], message="Book ID is required", code=201)

                book_controller = BooksController()
                return book_controller.deleteViewBook(reques_data, userdict['id'])

            except:
                return ok_response([], message="Unauthorize", code=403)


class BookDetailAPI(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                if reques_data.get('book_id') is None or not reques_data.get('book_id'):
                    return ok_response([], message="Book ID is required", code=201)

                book_controller = BooksController()
                return book_controller.getBookDetail(reques_data)

            except:
                return ok_response([], message="Unauthorize", code=403)


class GetBookByUserAPI(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                if reques_data.get('user_id') is None or not reques_data.get('user_id'):
                    return ok_response([], message="User ID is required", code=201)

                book_controller = BooksController()
                return book_controller.getallBooksByUser(reques_data)

            except:
                return ok_response([], message="Unauthorize", code=403)


class SearchBookAPI(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                if reques_data.get('book_title') is None:
                    return ok_response([], message="Book title is required", code=201)
                if reques_data.get('author') is None:
                    return ok_response([], message="Author is required", code=201)
                if reques_data.get('publisher') is None:
                    return ok_response([], message="Publisher is required", code=201)
                if reques_data.get('active') is None or not reques_data.get('active'):
                    return ok_response([], message="active key is required (pass 0 for pending, 1 for active ,2 for rejected and 3 for all)", code=201)
                if reques_data.get('page') is None or not reques_data.get('page'):
                    return ok_response([], message="Page is required", code=201)
                if reques_data.get('size') is None or not reques_data.get('size'):
                    return ok_response([], message="Size is required", code=201)
                book_controller = BooksController()
                if reques_data.get('exclude_user_id') is None or not reques_data.get('exclude_user_id'):
                    if reques_data.get('type') is None or not reques_data.get('type'):
                        return ok_response([], message="Type(0,1,2) is required", code=201)
                    else:
                        type = 2
                        if int(reques_data.get('type')) == 0:
                            type = 1
                        elif int(reques_data.get('type')) == 1:
                            type = 0

                        if reques_data.get('only_admin') is None or not reques_data.get('only_admin'):
                            return book_controller.searchbook(reques_data, userdict, type)
                        else:
                            admin = 2
                            if int(reques_data.get('only_admin')) == 0:
                                admin = 1
                            elif int(reques_data.get('only_admin')) == 1:
                                admin = 0
                            return book_controller.searchbookadmin(reques_data, userdict, type, admin)
                else:
                    return book_controller.searchBookExcludingUser(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=403)


class ScheduleBookAPI(APIView):

    def get(self, request):

        if not 'authorization' in request.headers.keys():

            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET
                book_schedule = ScheduleController()

                if reques_data.get('is_admin') is None or not reques_data.get('is_admin'):

                    return book_schedule.getAllUserScheduleBooks(reques_data, userdict)
                else:
                    print(11)
                    return book_schedule.getAllScheduleBooks(reques_data, userdict)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def post(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST

                book_schedule = ScheduleController()

                return book_schedule.schedule_books(reques_data, userdict)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def put(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                book_schedule = ScheduleController()

                return book_schedule.update_schedule_book(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data

                book_schedule = ScheduleController()
                return book_schedule.deleteScheduleBook(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=403)


class SubscriptionAPI(APIView):

    def get(self, request):

        if not 'authorization' in request.headers.keys():

            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                subscription = SubscriptionController()
                return subscription.getSubscription()
            except:
                return ok_response([], message="Unauthorize", code=403)

    def post(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)

        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                if userdict['user_role'] == 1:
                    subscription = SubscriptionController()
                    return subscription.createSubscriptionPlan(reques_data)
                else:
                    return ok_response([], message="You are not authorize to add subscription", code=403)
            except:
                return ok_response([], message="Unauthorize", code=403)

    def put(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                if userdict['user_role'] == 1:
                    subscription = SubscriptionController()
                    return subscription.updateSubscriptionPlan(reques_data)
                else:
                    return ok_response([], message="You are not authorize to add subscription", code=403)

            except:
                return ok_response([], message="Unauthorize", code=403)

    def delete(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.data
                if userdict['user_role'] == 1:
                    subscription = SubscriptionController()
                    return subscription.deleteSubscriptionPlan(reques_data, userdict)
                else:
                    return ok_response([], message="You are not authorize to delete subscription", code=403)

            except:
                return ok_response([], message="Unauthorize", code=403)


class UserSubscriptionAPI(APIView):

    def get(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)

        else:
            header = request.headers['authorization']

            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET
                user_subscriptions = UserSubscriptionController()
                return user_subscriptions.getUserSubscriptions(reques_data, userdict)

            except:
                return ok_response([], message='unauthorized', code=201)

    def post(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                user_subscriptions = UserSubscriptionController()
                return user_subscriptions.buySubscriptionPlan(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=201)


# for admin
class ActivateUserPlan(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                user_subscriptions = UserSubscriptionController()
                return user_subscriptions.ActivatePlan(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=201)


class CMSAPI(APIView):
    def get(self, request):
        cmscontroller = CMSController()
        return cmscontroller.getCMS()

    def post(self, request):

        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                if userdict['user_role'] == 1:
                    reques_data = request.data

                    cmscontroller = CMSController()
                    return cmscontroller.createCMS(reques_data)

                else:
                    return ok_response([], message="Only admin can add CMS into database", code=202)

            except:
                return ok_response([], message="Unauthorize", code=403)


class GetUserPlanExpiry(APIView):
    def get(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']

            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.GET
                user_subscriptions = UserSubscriptionController()
                return user_subscriptions.getUserPlanExpiry(reques_data, userdict)

            except:
                return ok_response([], message='unauthorized', code=201)


class YoutubeSearchView(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                youtubesearchcontroller = BooksController()
                return youtubesearchcontroller.bookAndYoutubeSearch(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=201)


class SingleBookSearchView(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                youtubesearchcontroller = BooksController()
                return youtubesearchcontroller.singleBookSearch(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=201)


class SaveTransactionAPI(APIView):
    def post(self, request):
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorize", code=403)
        else:
            header = request.headers['authorization']
            try:
                userdict = jwt.decode(
                    header, constants.jwt_key, algorithm=constants.jwt_algorithm)
                reques_data = request.POST
                newtransaction = TransactionController()
                return newtransaction.saveTransaction(reques_data, userdict)

            except:
                return ok_response([], message="Unauthorize", code=201)


class AudioBookAPIView(APIView):
    def post(self, request):
        reques_data = request.data
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorized", code=403)
        if reques_data.get('title') is None or not reques_data.get('title'):
            return ok_response([], message="title is required", code=403)

        header = request.headers['authorization']
        try:
            userdict = jwt.decode(header, constants.jwt_key,
                                  algorithms=constants.jwt_algorithm)
            book_controller = BooksController()
            return book_controller.audioBookSearch(reques_data, userdict)
        except:
            return ok_response([], message="Unauthorized", code=201)
    
# for admin only
class SendPushNotifications(APIView):
    def post(self, request):
        reques_data = request.data
        if not 'authorization' in request.headers.keys():
            return ok_response([], message="Unauthorized", code=403)
        if reques_data.get('notification_title') is None or not reques_data.get('notification_title'):
            return ok_response([], message="notification_title is required", code=403)
        if reques_data.get('notification_body') is None or not reques_data.get('notification_body'):
            return ok_response([], message="notification_body is required", code=403)
        
        header = request.headers['authorization']
        try:
            userdict = jwt.decode(
                header, constants.jwt_key, algorithm=constants.jwt_algorithm)
            usercontroller = UserController()
            return usercontroller.push_notifications(reques_data, userdict)

        except Exception as e:
            return ok_response([e], message="Unauthorize", code=201)
        

