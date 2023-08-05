from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404,  JsonResponse
from django.views import generic
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import FollowerSignUpForm, CreatorSignUpForm
from chats.models import ChatModel
import uuid
from .helper import send_forget_password_mail
from .models import User,User, UserProfile,Creator,users_feedback
from django.utils import timezone



class LandingPageView(generic.TemplateView):
    template_name = "landing.html"


def register(request):
    return render(request, 'new_register.html')


class Follower_register(CreateView):
   
    model = User
    form_class = FollowerSignUpForm
    template_name = 'new_follower_register.html'

    def form_valid(self, form):
        print("hello world")
        user = form.save()
        login(self.request, user, backend='chats.authenticate.EmailAuthBackend')
        return redirect('/')


class Creator_register(CreateView):
    # print("hello ap bye bye ycp111111")
    model = User
    form_class = CreatorSignUpForm
    template_name = 'new_creator_register.html'

    
    def form_valid(self, form):
        # print("hello ap bye bye ycp")
        user = form.save()
        login(self.request, user, backend='chats.authentication.EmailAuthBackend')
        return redirect('/')
    


def login_request(request):
    if request.method == 'POST':
        # form = AuthenticationForm(data=request.POST)
        # if form.is_valid():
        # email = form.cleaned_data.get('username') 
        # password = form.cleaned_data.get('password')

        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        user = authenticate(username=email, password=password)
        #print("user", user)
        if user is not None:
            if user.is_active:
                login(request, user, backend='chats.authentication.EmailAuthBackend')
                return redirect('/')
            else:
                return HttpResponse('Disabled Account')
        else:
            messages.error(request, "Invalid username or password")
    else:
        messages.error(request, "Invalid username or password")
    return render(request, 'new_login.html')


def Logout(request):
    logout(request)
    return redirect('/')


def ChangePassword(request, token):
    context = {}
    try:
        profile_obj = get_object_or_404(User, token=token)
        context = {'user_id': profile_obj.id}
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            if user_id is None:
                messages.success(request, 'No user id found.')
                return redirect(f'/chats/change-password/{token}/')
            if new_password != confirm_password:
                messages.success(request, 'both should be equal.')
                return redirect(f'/chats/change-password/{token}/')
            try:
                validate_password(new_password, profile_obj)
            except Exception as e:
                for error in e:
                    messages.success(request, error)
                    return redirect(f'/chats/change-password/{token}/')
            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.token = ""
            user_obj.save()
            messages.success(request, "Login with new password id")
            return redirect('/chats/login/')
    except Exception as e:
        raise Http404("url not found")
    return render(request, 'change-password.html', context)


def ForgetPassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('username')
            if not email:
                messages.success(request, 'Please Enter email')
                return redirect('/chats/forget-password/')
            if not User.objects.filter(email=email).first():
                messages.success(request, 'No user found with this username.')
                return redirect('/chats/forget-password/')
            user_obj = User.objects.get(email=email)
            token = str(uuid.uuid4())
            profile_obj = User.objects.get(email=user_obj)
            profile_obj.token = token
            profile_obj.save()
            send_forget_password_mail(user_obj.email, token)
            messages.success(request, 'An email is sent.')
            return redirect('/chats/forget-password/')
    except Exception as e:
        print(e)
    return render(request, 'forget-password.html')


@login_required
def index(request):
    try:
        UserProfile_obj = UserProfile.objects.filter(user_id=request.user.id).all().order_by('-last_message')
    except Exception as e:
        print(e)
    return render(request, 'new_chatlist.html', context={'friends': UserProfile_obj})


ALLOWED_EXTENSIONS = ['.m4a','.ogg','.mp3','.jpg', '.jpeg', '.png', '.mp4','.avi','.mov','.pdf','.doc','.docx', '.html', '.txt']


@csrf_exempt
def chatPage(request, id):
    try:
        UserProfile_obj = UserProfile.objects.filter(user_id=request.user.id).all().order_by('-last_message')
        
    except Exception as e:
        print(e)
    try:
        UserProfile.objects.filter(Follower_id=id, user_id=request.user.id).update(message_seen=True)
    except Exception as e:
        print(e)
    user_obj = User.objects.get(id=id)
    if request.user.id > user_obj.id:
        thread_name = f'chat_{request.user.id}-{user_obj.id}'
    else:
        thread_name = f'chat_{user_obj.id}-{request.user.id}'
    if request.method == 'POST':
        if request.FILES.get('fileInput'):
            file = request.FILES['fileInput']
            if not any(file.name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                messages.error(request, 'Invalid file type. Only JPG, JPEG, and PNG files are allowed.')
                return JsonResponse({'success': False, 'message': 'Invalid file type.'})
            chat = ChatModel.objects.create(sender=request.user.username, thread_name=thread_name, file=file)
            chat.save()
            file_url = chat.file.url
            file_name = chat.file.name

            response_data = {
                'success': True,
                'message': 'File uploaded successfully.',
                'file_url': file_url,
                'file_name': file_name
                
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'message': 'No file provided.'})
    
    session_opened = UserProfile.objects.get(user = request.user , Follower = user_obj).is_session_opened
    print(session_opened)
        

    message_objs = ChatModel.objects.filter(thread_name=thread_name).all().order_by('timestamp')
    try:
        if users_feedback.objects.filter(Creator = id, Follower = request.user.id).latest('id').Rating:
            Is_Rating_given = True 
            
        else :
            Is_Rating_given = False
    except Exception as e:
        Is_Rating_given = False

    return render(request, 'main_chat_test.html', context={'user': user_obj, 'users': UserProfile_obj, 'msgs': message_objs, 'session_status' : session_opened , 'Is_Rating_given' : Is_Rating_given  })


def search(request):
    return render(request, 'search_users.html')


def search_users(request):
    search_query = request.GET.get('search', '')
    creators = Creator.objects.filter(user__first_name__icontains=search_query)
    search_results = [{'first_name': creator.user.first_name, 'last_name': creator.user.last_name,
                       'image_url': creator.user.image.url, 'id': creator.user_id, 'username': creator.user.username,
                       'profession': creator.Professional_label} for creator in creators]
    return JsonResponse(search_results, safe=False)


import razorpay
from django.conf import settings 

from django.http import HttpResponseBadRequest



def creator_profile(request, id):
    creator_profile = Creator.objects.get(user_id=id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)) 
    response = client.order.create({
    'amount': int(100) * 100,  # Amount in paise (e.g., ₹500 = 50000 paise)
    'currency': 'INR',
    'payment_capture': '1'  # Auto-capture payments after successful redirection
})
    
    callback_url = "http://" + "127.0.0.1:8000" + "/callback/" + str(id) + "/" + str(request.user.id) + "/"
    order_id = response['id']
    api_key = settings.RAZORPAY_KEY_ID
   
    return render(request, 'creator_profile.html', {'profile': creator_profile ,'callback_url': callback_url, 'order_id':order_id, 'api_key':api_key })






from .constants import PaymentStatus
@csrf_exempt
def callback(request, id, rid):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    
    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        # order = Order.objects.get(provider_order_id=provider_order_id)
        # order.payment_id = payment_id
        # order.signature_id = signature_id
        # order.save()
        if verify_signature(request.POST):
            # order.status = PaymentStatus.SUCCESS
            # order.save()
            print("sucesss - 1 ")
            user1 = User.objects.get(id = rid) ### follower
            user2 = User.objects.get(id = id) #### Creator
            if not UserProfile.objects.filter(user = user1, Follower = user2 ) :
                # if the user is paying for firsttime
                UserProfile.objects.create(user = user1, Follower = user2 )
                UserProfile.objects.create(user = user2, Follower = user1 )
                

            else:
                print("second time")
                userprofile_obj = UserProfile.objects.filter(user = user1, Follower = user2).latest('id')
                userprofile_obj.is_session_opened = True
                userprofile_obj.save()
                
            
            

            users_feedback.objects.create(Creator = user2, Follower = user1, chat_start_time = timezone.now())
            return redirect(f'/chat/{id}/')
        else:
            # order.status = PaymentStatus.FAILURE
            # order.save()
            print("Failure - 1 ")
            return redirect(f'/Creator_profile/{id}/')
    else:
        # payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        # provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
        #     "order_id"
        # )
        # order = Order.objects.get(provider_order_id=provider_order_id)
        # order.payment_id = payment_id
        # order.status = PaymentStatus.FAILURE
        # order.save()
        print("Failure - 2 ")
        return redirect(f'/Creator_profile/{id}/')




# @csrf_exempt
# def paymenthandler(request, id):
 
#     # only accept POST request.
#     if request.method == "POST":
#         try:
           
#             # get the required parameters from post request.
#             payment_id = request.POST.get('razorpay_payment_id', '')
#             razorpay_order_id = request.POST.get('razorpay_order_id', '')
#             signature = request.POST.get('razorpay_signature', '')
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature
#             }
 
#             # verify the payment signature.
#             result = client.utility.verify_payment_signature(
#                 params_dict)
#             print(result)
#             if result :
#                 # amount = 50000  # Rs. 200
#                 # try:
 
#                 #     # capture the payemt
#                 #     client.payment.capture(payment_id, amount)
 
#                 #     # render success page on successful caputre of payment
#                 user1 = User.objects.get(id = request.user.id)
#                 user2 = User.objects.get(id = id)
#                 UserProfile.objects.create(user = user1, Follower = user2 )
#                 UserProfile.objects.create(user = user2, Follower = user1 )

#                 users_feedback.objects.create(Creator = user2, Follower = user1, chat_start_time = timezone.now())
                

#                 return redirect(f'/chat/{id}/')
#                 # except:
 
#                     # if there is an error while capturing payment.
#                     # return redirect(f'/Creator_profile/{id}/')
#             else:
 
#                 # if signature verification fails.
#                 return redirect(f'/Creator_profile/{id}/')
#         except:
 
#             # if we don't find the required parameters in POST data
#             return redirect(f'/Creator_profile/{id}/')
#     else:
#        # if other than POST request is made.
#         return HttpResponseBadRequest()


def edit_creator_profile(request):
    if request.method == 'POST':
        try :
            creator_obj = Creator.objects.get(user=request.user)
            image_obj = User.objects.get(id = request.user.id)
            if request.FILES.get('profile-pic'):
                print(request.FILES['profile-pic'])
                
                image_obj.image = request.FILES['profile-pic']

        except Exception as e:
            print(e)
            
            
           

        if request.POST.get('profession'):
            creator_obj.Professional_label = request.POST.get('profession')
        if request.POST.get('about_me'):
            creator_obj.About = request.POST.get('about_me')
        if  request.POST.get('insta'):
            creator_obj.insta = request.POST.get('insta')
        if request.POST.get('twitter'):
            creator_obj.twitter = request.POST.get('twitter')
        if request.POST.get('youtube'):
            creator_obj.youtube = request.POST.get('youtube')
        if request.POST.get('Service'):
            creator_obj.service = request.POST.get('Service')
        if request.POST.get('name'):
            image_obj.first_name = request.POST.get('name')
            
        if request.POST.get('username'):
            image_obj.username = request.POST.get('username')
        image_obj.save()
        
        creator_obj.save()
        messages.success(request, "profile_updated")
        return redirect('/my_profile/')

    obj = Creator.objects.get(user=request.user)
    return render(request, 'edit_creator_profile.html', {'creator_profile': obj})

def my_profile(request):
    creator_profile = Creator.objects.get(user = request.user)
    return render(request, 'my_profile.html', {'profile': creator_profile})

def delete_chat(request , id , chat_id):
    try:
        chat_obj  = ChatModel.objects.get(id = chat_id)
        user_obj = User.objects.get(id = request.user.id)
        if chat_obj.sender == request.user.username:
            chat_obj.delete()
        
    except Exception as e:
        print(e)
    return redirect(f'/chat/{id}/')


def close_session(request, id):
    sender_obj = User.objects.get(id = request.user.id)
    receiver_obj = User.objects.get(id = id)
    

    #if creator closes the session 
    try:
        if sender_obj.is_Follower or receiver_obj.is_Follower:

            if sender_obj.is_Creator :
                obj = UserProfile.objects.get(user = receiver_obj , Follower = sender_obj)
                obj.is_session_opened = False
                obj.save()
            #if floower closes the session
            else:
                obj = UserProfile.objects.get(user = sender_obj  , Follower = receiver_obj )
                obj.is_session_opened = False
                obj.save()
        else:
            obj = UserProfile.objects.get(user = sender_obj , Follower = receiver_obj)
            obj.is_session_opened = False
            obj.save()
            
    except Exception as e:
        print(e)


    if request.user.id >receiver_obj.id:
        thread_name = f'chat_{request.user.id}-{receiver_obj.id}'
    else:
        thread_name = f'chat_{receiver_obj.id}-{request.user.id}'

    chat = ChatModel.objects.create(sender='info-message', message = "The session was ended", thread_name=thread_name)
    chat.save()
    print("yes")
   
    return redirect(f'/chat/{id}/')

from chats.models import dashboard as dash
from django.db.models import Avg, Sum, Count

def dashboard(request ):
   

    creator_obj = User.objects.get(id = request.user.id)
    
    dashboard_obj = dash.objects.filter(Creator = creator_obj).all().order_by('-timestamp')
    

    average_rating = dash.objects.filter(Creator=creator_obj).aggregate(avg_rating=Avg('Rating'))['avg_rating']

    average_rating = round(average_rating, 1) if average_rating else None
    # Get sum of amount
    total_amount = dash.objects.filter(Creator=creator_obj).aggregate(sum_amount=Sum('amount'))['sum_amount']

    # Get total number of records filtered by creator
    record_count = dash.objects.filter(Creator=creator_obj).count()

   

    return render(request , "dashboard.html", {'dashboard_data' : dashboard_obj, 'average_rating': average_rating , 'total_amount': total_amount,'record_count': record_count })

    # except Exception as e:
    #     print(e)

    # return render(request ,"dashboard.html")


def follower_profile_edit(request):
    return render(request , "follower_profile_edit.html")




def user_feedback(request ,id):

    follower = request.user.id
    creator = id

    feedback_obj = users_feedback.objects.filter(Creator = creator, Follower = follower).latest('id')


    if request.method == 'POST':
        
        if request.POST.get('rating'):
            feedback_obj.Rating = request.POST.get('rating')
        else:
            return redirect(f'/chat/{id}/')
            
        if request.POST.get('feedback'):
            feedback_obj.Feedback = request.POST.get('feedback')

        feedback_obj.chat_end_time = timezone.now()
        
        feedback_obj.save()

    return redirect(f'/chat/{id}/')
            

def feedback(request):
    user_obj = User.objects.get(id = request.user.id)
    user_feedback_obj = users_feedback.objects.filter(Creator = user_obj )

    return render(request , 'feedback.html', {'user_feedback_obj':user_feedback_obj})

        
   
    
    
    
    

   
    


    

    
