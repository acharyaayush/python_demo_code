from functools import wraps
from django.http.response import JsonResponse
import string
import random

LETTERS = string.ascii_letters
NUMBERS = string.digits
PUNCTUATION = string.punctuation

headers_mapping = {'csv': {'content-type': 'application/csv'},
                   'json': {'content-type': 'application/json'}}


def ok_response(response, status=True, message="OK", headers='json', code=200):
    resp = {"status": status,
                "data": response,
                "message": message,
                "code": code,
                }

    return JsonResponse(resp, safe=False)



def error_response(code, message, response={}, headers='json'):
    return False, response, code, message, headers_mapping[headers]


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)

        if session.get('user_id', False):
            return func(*args, **kwargs)

        app.logger.error("Unauthorized request from %s", request.remote_addr)
        return False, {}, 401, 'Unauthorized', {'Content-Type': 'application/json'}

    return wrapper

def createNewPassword():
    '''
        Generates a random password having the specified length
        :length -> length of password to be generated. Defaults to 8
            if nothing is specified.
        :returns string <class 'str'>
        '''
    # create alphanumerical from string constants
    printable = f'{LETTERS}{NUMBERS}{PUNCTUATION}'

    # convert printable from string to list and shuffle
    printable = list(printable)
    random.shuffle(printable)

    # generate random password and convert to string
    random_password = random.choices(printable, k=8)
    random_password = ''.join(random_password)
    return random_password


def modify_input_for_multiple_files(image):
    dict = {}
    dict['file'] = image
    return dict