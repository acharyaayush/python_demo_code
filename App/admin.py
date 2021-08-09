from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register((UsersSubscriptions, SubscriptionPlans, Users, Transactions, UsersBooks, Categories, UserLoggedIn))

