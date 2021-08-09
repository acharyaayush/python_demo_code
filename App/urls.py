from django.conf.urls import url

from api import views
from api.views import *
from django.urls import path

urlpatterns = [
    path('checkversion', views.get_version),
    path('addversion', views.add_latest_version),
    path('auth', LoginView.as_view()),
    path('adminauth', AdminLoginView.as_view()),
    path('checksocial', SocialLoginView.as_view()),
    path('forgotpassword', ForgotPasswordView.as_view()),
    path('users', UserView.as_view()),
    path('searchuser', UserSearchAPI.as_view()),
    path('category', CategoryView.as_view()),
    path('searchcategory', CategorySearchAPI.as_view()),
    path('changepassword', PasswordAPI.as_view()),
    path('getstatistics', StatisticsAPI.as_view()),
    path('post', PostAPI.as_view()),
    path('changepoststatus', AdminPost.as_view()),
    path('likepost', PostLikeAPI.as_view()),
    path('commentpost', PostCommentAPI.as_view()),
    path('uploadfile', UploadFile.as_view()),
    path('comment_thread', CommentThreadAPI.as_view()),
    path('reportpost', PostReportAPI.as_view()),
    path('books', BooksAPI.as_view()),
    path('likebook', BookLikeAPI.as_view()),
    path('viewbook', BookViewAPI.as_view()),
    path('getuserbook', GetBookByUserAPI.as_view()),
    path('searchbook', SearchBookAPI.as_view()),
    path('bookdetail', BookDetailAPI.as_view()),
    path('schedulebook', ScheduleBookAPI.as_view()),
    path('subscription', SubscriptionAPI.as_view()),
    path('usersubscription', UserSubscriptionAPI.as_view()),
    path('activateuserplan', ActivateUserPlan.as_view()),
    path('getuserplanexpiry', GetUserPlanExpiry.as_view()),
    path('cms', CMSAPI.as_view()),
    path('youtubesearch', YoutubeSearchView.as_view()),
    path('singlebooksearch', SingleBookSearchView.as_view()),
    path('transaction', SaveTransactionAPI.as_view()),
    path('getaudiobook', AudioBookAPIView.as_view()),
    path('pushnotification', SendPushNotifications.as_view())
]