from django.contrib import admin
from django.urls import path, include

from chats.views import index,LandingPageView ,chatPage,search_users , close_session, dashboard
from chats.views import search,login_request,creator_profile, edit_creator_profile, my_profile, delete_chat,follower_profile_edit

from chats.views import user_feedback, feedback, callback # ,paymenthandler,
                          
from payment.views import payment_request

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', index, name='home'),
    path('chat/<int:id>/', chatPage, name='chatPage'),
    path('search/', search_users, name='search_users'),
    path('sea/', search, name = 'search'),
    path('', LandingPageView.as_view(), name = "landingpage"),
    path("chats/", include("chats.urls")),
    path('accounts/', include('allauth.urls')),
    path('login/',login_request, name='login_main'),
    path('Creator_profile/<int:id>/', creator_profile, name='creator_profile'),
   
    path('profile_edit/', edit_creator_profile, name='edit_creator_profile'),
    path('my_profile/', my_profile, name='my_profile'),
    path('delete_chat/<int:id>/<int:chat_id>' ,delete_chat, name = "delete_chat"),
    path('close_session/<int:id>', close_session, name = 'close_session'),
    path('dashboard', dashboard, name = 'dashboard'),
    path('follower_profile_edit/', follower_profile_edit, name='follower_profile_edit'),
    path('user_feedback/<int:id>/', user_feedback, name='user_feedback'),
    path('feedback/', feedback, name='feedback'),
    path('payment', payment_request, name = "payment_request"),
    # path('paymenthandler/<int:id>', paymenthandler, name = "paymenthandler"),

    
    path('callback/<int:id>/<int:rid>/', callback, name='callback'),


    
]


from django.conf import settings
from django.conf.urls.static import static


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
