import hashlib
import time

from django.core.mail import send_mail
from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView

from api.controller.post_module import PostController
from api.models import Users, UserLoggedIn
from api.utills import constants
from api.utills.response import ok_response, createNewPassword, modify_input_for_multiple_files
from api.controller.users import UserController
import jwt
from api.utills.serializers import UserSerializer, FileSerializer
from bookiebot.settings import EMAIL_HOST_USER


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




        

