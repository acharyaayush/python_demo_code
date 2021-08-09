import hashlib

import jwt
from django.core.serializers import json
from django.forms import model_to_dict

from api.models import Users, UserLoggedIn
from api.utills import constants
from api.utills.response import ok_response
from django.db.models import Q
import time

from api.utills.serializers import UserSerializer
from api.models import UserLoggedIn
from push_notifications.apns import apns_send_message
from push_notifications.gcm import send_message


class UserController(Users):

    def __init__(self, id=None):
        self.id = id
        self.user = None

    def create_user_object(self, request_param):

        if not request_param.get('social_id'):
            user = Users.objects.filter(email=request_param.get('email'))
        else:
            user = Users.objects.filter(
                Q(email=request_param.get('email')) | Q(social_id=request_param.get('social_id')))

        isexist = True

        if len(list(user)) > 0:
            return model_to_dict(user[0]), isexist
        else:

            isexist = False
            usernew = Users()
            usernew.email = request_param.get('email')
            usernew.user_role = request_param.get('user_role')

            if not request_param.get('social_id'):
                usernew.phn_no = request_param.get('phn_no')
                pass_obj = hashlib.md5(request_param.get('password').encode())
                usernew.password = pass_obj.hexdigest()
                usernew.social_id = ''
                usernew.social_id_type = ''
            else:
                print(request_param.get('social_id'))
                usernew.phn_no = ''
                usernew.password = ''
                usernew.social_id = request_param.get('social_id')
                usernew.social_id_type = request_param.get('social_id_type')
            usernew.created_at = int(time.time())
            usernew.updated_at = int(time.time())
            usernew.save()
            userdict = {'id': usernew.id, 'name': usernew.name, 'email': usernew.email, 'users_pic': usernew.users_pic, 'user_role': usernew.user_role}
            encoded = jwt.encode(userdict, constants.jwt_key, algorithm=constants.jwt_algorithm)
            userloggedin = UserLoggedIn.objects.filter(user_id=usernew.id, device_id=request_param.get('device_id'),
                                                       device_token=request_param.get('device_token'),
                                                       device_type=request_param.get('device_type'))
            if len(userloggedin) == 0:
                userlogged = UserLoggedIn()
                userlogged.device_id = request_param.get('device_id')
                userlogged.device_token = request_param.get('device_token')
                userlogged.device_type = request_param.get('device_type')
                userlogged.user_id = usernew.id
                userlogged.logged_in = int(time.time())
                userlogged.save()
            resp = {'id': usernew.id, 'token': encoded.decode("utf-8")}
            return resp, isexist

    def update_user(self, request_param):
        try:

            user = Users.objects.get(id=request_param.get('id'))
            if bool(request_param.get('name')):
                user.name = request_param.get('name')

            if bool(request_param.get('phn_no')):
                user.phn_no = request_param.get('phn_no')

            if bool(request_param.get('pin')):
                user.pin = request_param.get('pin')

            if bool(request_param.get('users_pic')):
                user.users_pic = request_param.get('users_pic')

            if bool(request_param.get('gender')):
                user.gender = request_param.get('gender')

            if bool(request_param.get('child_name')):
                user.child_name = request_param.get('child_name')

            if bool(request_param.get('child_age')):
                user.child_age = request_param.get('child_age')

            user.updated_at = int(time.time())

            user.save()
            return ok_response(model_to_dict(user), code=200)
        except Users.DoesNotExist:
            return ok_response([], message="No user found", code=201)

    def delete_user(self, request_param):
        try:
            user = Users.objects.get(id=request_param.get('id'))
            user.is_deleted = 1
            user.is_active = 0
            user.save()
            return ok_response(model_to_dict(user), code=200)
        except Users.DoesNotExist:
            return ok_response([], message="No user found", code=201)

    def change_password(self, request_param):
        try:
            user = Users.objects.get(id=request_param.get('id'))
            pass_obj = hashlib.md5(request_param.get('old_password').encode())

            if user.password == pass_obj.hexdigest():
                new_pass_obj = hashlib.md5(request_param.get('new_password').encode())
                user.password = new_pass_obj.hexdigest()
                user.save()
                return ok_response([], message="Password changed successfully.", code=200)
            else:
                return ok_response([], message="Old Password doesn't match.", code=201)

        except Users.DoesNotExist:
            return ok_response([], message="No user found", code=201)

    def change_password_forcefully(self, request_param):
        try:
            user = Users.objects.get(id=request_param.get('id'))

            new_pass_obj = hashlib.md5(request_param.get('new_password').encode())
            user.password = new_pass_obj.hexdigest()
            user.save()
            return ok_response([], message="Password changed successfully.", code=200)


        except Users.DoesNotExist:
            return ok_response([], message="No user found", code=201)

    def search_user(self, request_param):

        try:

            if int(request_param.get('size')) == 0:
                if int(request_param.get('active')) == 1:
                    if not request_param.get('to_date') or request_param.get('from_date'):
                        result_category_count = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                                     is_deleted=0).count()
                        result_category = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                               is_deleted=0).order_by(
                            '-updated_at')
                    else:
                        result_category_count = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                                     is_deleted=0,
                                                                     created_at__gte=int(request_param.get('to_date')),
                                                                     created_at__lte=int(
                                                                         request_param.get('from_date'))).count()
                        result_category = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                               is_deleted=0,
                                                               created_at__gte=int(request_param.get('from_date')),
                                                               created_at__lte=int(
                                                                   request_param.get('to_date'))).order_by(
                            '-updated_at')

                else:

                    if not request_param.get('to_date') or request_param.get('from_date'):
                        result_category_count = Users.objects.filter(name__icontains=request_param.get('keyword')).count()
                        result_category = Users.objects.filter(name__icontains=request_param.get('keyword')).order_by(
                            '-updated_at')
                    else:
                        result_category_count = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                                     created_at__gte=int(request_param.get('to_date')),
                                                                     created_at__lte=int(
                                                                         request_param.get('from_date'))).count()
                        result_category = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                               created_at__gte=int(request_param.get('from_date')),
                                                               created_at__lte=int(
                                                                   request_param.get('to_date'))).order_by(
                            '-updated_at')

            else:
                if int(request_param.get('active')) == 1:
                    if not request_param.get('to_date') or request_param.get('from_date'):

                        result_category_count = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                                    is_deleted=0).count()

                        result_category = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                                    is_deleted=0).order_by('-updated_at')[
                                          (int(request_param.get('page')) * int(request_param.get('size'))):(
                                                  int(request_param.get('size')) * (int(request_param.get('page')) + 1))]
                    else:
                        result_category_count = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                                     is_deleted=0,
                                                               created_at__gte=int(request_param.get('from_date')),
                                                               created_at__lte=int(
                                                                   request_param.get('to_date'))).count()

                        result_category = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                               is_deleted=0,
                                                               created_at__gte=int(request_param.get('from_date')),
                                                               created_at__lte=int(
                                                                   request_param.get('to_date'))).order_by('-updated_at')[
                                          (int(request_param.get('page')) * int(request_param.get('size'))):(
                                                  int(request_param.get('size')) * (
                                                      int(request_param.get('page')) + 1))]

                else:
                    if not request_param.get('to_date') or request_param.get('from_date'):

                        result_category_count = Users.objects.filter(name__icontains=request_param.get('keyword')).count()
                        result_category = Users.objects.filter(name__icontains=request_param.get('keyword')).order_by('-updated_at')[
                                          (int(request_param.get('page')) * int(request_param.get('size'))):(
                                                  int(request_param.get('size')) * (int(request_param.get('page')) + 1))]
                    else:
                        result_category_count = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                               created_at__gte=int(request_param.get('from_date')),
                                                               created_at__lte=int(
                                                                   request_param.get('to_date'))).count()
                        result_category = Users.objects.filter(name__icontains=request_param.get('keyword'),
                                                               created_at__gte=int(request_param.get('from_date')),
                                                               created_at__lte=int(
                                                                   request_param.get('to_date'))).order_by('-updated_at')[
                                          (int(request_param.get('page')) * int(request_param.get('size'))):(
                                                  int(request_param.get('size')) * (int(request_param.get('page')) + 1))]

            serializer = UserSerializer(result_category, many=True)
            resp = {'count': result_category_count, 'users': serializer.data}
            return ok_response(resp, code=200)
        except:
            return ok_response([], message="No User found", code=201)


    def push_notifications(self, request_param, userDict):
        try:
            user = Users.objects.get(id=userDict['id'])
            if user:
                if user.user_role == 1: #only admin can send push notifications
                    try:
                        # For ios devices
                        ios_devices = UserLoggedIn.objects.filter(device_type=0)
                        
                        registration_id = []
                        for device in ios_devices:
                            registration_id.append(device.device_token)

                        message={"title" : request_param.get('notification_title'), "body" : request_param.get('notification_body')}

                        for id in registration_id:
                            apns_send_message(
                            registration_id=id,
                            alert=message,creds=None,
                            )


                        # For Android
                        android_devices = UserLoggedIn.objects.filter(device_type=1)

                        registration_id = []
                        for device in android_devices:
                            registration_id.append(device.device_token)
                        
                        message={"title" : request_param.get('notification_title'), "body" : request_param.get('notification_body')}

                        for ids in registration_id:
                            send_message(
                            ids, message, "FCM"
                            )

                        return ok_response('notifications sent', code=201)
                    except Exception as e:
                        return ok_response([e], message="Internal server error", code=201)
                else:
                    return ok_response([], message="You are not authorized to send push notifications", code=201)
            else:
                return ok_response([], message="user not found", code=201)
        except Exception as e:
            return ok_response([e], message="Internal server error", code=201)


