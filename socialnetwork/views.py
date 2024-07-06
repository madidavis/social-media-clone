from socket import AF_APPLETALK
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core import serializers

from socialnetwork.custom_components import NavigationLink
from socialnetwork.forms import CreatePostForm, EditProfileForm, LoginForm, RegisterForm, UserProfileForm, EditProfileForm
from socialnetwork.models import Profile, Post, Comment

from django.utils import timezone, dateformat
from django.utils.dateparse import parse_datetime
from django.http import Http404, HttpResponse
import time
import datetime

import json

# Create your views here.
# ------------------------------------------------------------------------------------------------------------------------------#
# --- BASE VIEWS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
"""
    @brief      :    load login page upon site launch if user not logged in, otherwise load global stream
    @param[in]  :    GET Request
    @retval     :    render login page or global stream
"""


"""
    @brief      :    get context for navbar links
    @param[in]  :    string specifying current page
    @retval     :    list of links to render on navbar
"""
def navigation_bar_setup(curr_page):
    if (curr_page == "login"):
        return {NavigationLink('id_register_link', 'Register', 'register', 'nav-link px-2')}
    elif (curr_page == "register"):
        return {NavigationLink('id_login_link', 'Login', 'login', 'nav-link px-2')}
    else:
        return {NavigationLink('id_nav_global_stream', 'Global', 'global', 'nav-link px-2 order-1'), NavigationLink('id_nav_follower_stream', 'Follower', 'follower', 'nav-link px-2 order-2'), NavigationLink('id_nav_logout', 'Logout', 'logout', 'nav-link px-2 order-3')}


''' JSON error Handling'''
def json_error_handling(message, status=200):
    response_json = '{"error":"' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)
# ------------------------------------------------------------------------------------------------------------------------------#
# --- LOGIN VIEWS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
"""
    @brief      :    load login page upon site launch
    @param[in]  :    GET Request
    @retval     :    render login page
"""
def login_action(request):
    context = {}

    # - CONTEXT - #
    # Determine Context for Navbar
    context['navigation_links'] = navigation_bar_setup('login')
    # Determine Basic Login Page Context
    context['page_name'] = "Login"
    
    # If GET, render login page
    if request.method == 'GET':
        form = LoginForm()
        context['form'] = form 
        return render(request, 'socialnetwork/login.html', context)

    # Otherwise if POST request
    form = LoginForm(request.POST)
    context['form'] = form

    # Validate form
    if not form.is_valid():
        print(form['username'].errors)
        print(form['password'].errors)
        print(form.non_field_errors)
        return render(request, 'socialnetwork/login.html', context)
    
    # Authenticate User and Log In
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])


    login(request, new_user)
    return redirect(reverse('global'))


"""
    @brief      :    logout user 
    @param[in]  :    GET Request
    @retval     :    render login page
"""
@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

# ------------------------------------------------------------------------------------------------------------------------------#
# --- REGISTER VIEWS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
"""
    @brief      :    load register page upon site launch
    @param[in]  :
    @retval     :    render user registration page
"""
def register_action(request):
    context = {}
    
    # - CONTEXT 
    # Determine Context for Navbar
    context['navigation_links'] = navigation_bar_setup('register')
    # Determine Basic Register Page Context
    context['page_name'] = "Register"

    # If GET display the Regstration form
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    # If POST Request
    form = RegisterForm(request.POST)
    context['form'] = form 

    # Validates the form
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)
    
    # Otherwise return and create new user
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])

    # Create Profile Model for User 
    new_profile = Profile(profile_user=new_user)    
    # Set default profile image    
    new_profile.save()                             

    login(request, new_user)
    return redirect(reverse('global'))

    



# ------------------------------------------------------------------------------------------------------------------------------#
# --- GLOBAL STREAM VIEWS --- #
# ------------------------------------------------------------------------------------------------------------------------------#

"""
    @brief      :    loads home "global stream" page 
    @param[in]  :
    @retval     :    render global stream page when user logs in or clicks link
"""
@login_required
def global_action(request):
    context = {}
    
    # - CONTEXT - #
    # Determine Context for Navbar
    context['navigation_links'] = navigation_bar_setup('')

    # Determine Basic Global Page Context
    context['page_name'] = "Global Stream"
    context['posts'] = []


    if request.method == 'POST':
        new_post = Post()
        new_post.date_time = timezone.now()
        new_post.profile = request.user
        form = CreatePostForm(request.POST, instance=new_post)

        # Check form is valid
        if not form.is_valid():
            try:
                posts = Post.objects.order_by('-date_time').values()
                context['posts'] = posts
            except:
                pass
    
            context['form'] = form
            return render(request, 'socialnetwork/global.html', context)
        
        new_post.post_input_text = form.cleaned_data['post_input_text']
        new_post.save()

    # Load in Empty Forms
    context['post_form'] = CreatePostForm()

    # Load all Existing Posts & Comments
    try:
        posts = Post.objects.order_by('-date_time')
        context['posts'] = posts
    except:
        pass

    return render(request, 'socialnetwork/global.html', context)



"""
    @brief      :    AJAX function to add new comment to post
    @param[in]  :
    @retval     :    
"""
def add_comment(request):
    #error handling
    if not request.user.is_authenticated:
        return json_error_handling("You must be logged in to do this operation", status=401)
    if request.method != "POST":
        return json_error_handling("You must use POST for this operation", status=405)
    if not ('comment_text' in request.POST) or (request.POST["comment_text"] == None) or (request.POST['comment_text'] == ''):
        return json_error_handling("You must enter a comment", status=400)
    if not ('post_id' in request.POST) or (request.POST['post_id'] == None) or (request.POST['post_id'] == ''):
        return json_error_handling("You must enter a comment", status=400)
    if not ('csrfmiddlewaretoken' in request.POST) or (request.POST['csrfmiddlewaretoken'] == None):
        return json_error_handling('forbidden action no csrf token detected', status=403)
    print(request.POST['comment_text'])

    # Get Data From Request  
    post_id = request.POST["post_id"].replace("id_comment_input_text_", "")
    print(type(post_id))

    # Check Post Exists
    if not post_id.isdigit() or not Post.objects.filter(id=post_id).exists():
        return json_error_handling("Bad Parameters", status=400)
    

    # Create New Comment Object
    new_comment = Comment()
    new_comment.date_time = timezone.now()
    new_comment.profile = request.user
    new_comment.post = Post.objects.get(id=int(post_id))
    new_comment.comment_input_text = request.POST["comment_text"]
    new_comment.save()

    return HttpResponse(request, content_type="applications/json", status=200)


"""
    @brief      :    AJAX function to refresh global stream
    @param[in]  :
    @retval     :    
"""
def get_global(request): 
    #error handling
    if not request.user.is_authenticated:
        return json_error_handling("You must be logged in to do this operation", status=401)

    post_response = []
    comment_response = []

    # Get all Post objects
    posts = Post.objects.order_by('date_time').values()
    for post in posts:
        # Find Profile Associated with Post
        profile = Profile.objects.get(id=post['profile_id'])

        # Create JSON
        item = {
            'id': post['id'],
            'post_input_text': post['post_input_text'],
            'profile_id': post['profile_id'],
            'date_time': post['date_time'].strftime("%-m/%-d/%Y %-I:%M %p"),
            'first_name': profile.profile_user.first_name,
            'last_name': profile.profile_user.last_name
        }
        post_response.append(item)
    
    #Get all Comment objects 
    comments = Comment.objects.order_by('-date_time').values()
    for comment in comments:
        # Find Profile Associated with comment
        profile = Profile.objects.get(id=comment['profile_id'])
        print(comment['date_time'], comment['date_time'].strftime("%-m/%-d/%Y %I:%M %p"))
    
        # Find Post associated with comment
        item = {
            'id': comment['id'],
            'comment_input_text': comment['comment_input_text'],
            'profile_id': comment['profile_id'],
            'date_time': comment['date_time'].strftime("%-m/%-d/%Y %I:%M %p"),
            'post_id': comment['post_id'],
            'first_name': profile.profile_user.first_name,
            'last_name': profile.profile_user.last_name
        }

        comment_response.append(item)



    # Seraliase into a Json string
    posts_json = json.dumps({'page': 'global', 'posts': post_response, 'comments': comment_response})

    return HttpResponse(posts_json, content_type="applications/json")





# ------------------------------------------------------------------------------------------------------------------------------#
# --- FOLLOWER STREAM VIEWS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
"""
    @brief      :    loads "follower" stream" page 
    @param[in]  :
    @retval     :    render follower stream page when user clicks link
"""
@login_required
def follower_action(request):
    context = {}
    
    # - CONTEXT - #
    # Determine Context for Navbar
    context['navigation_links'] = navigation_bar_setup('')
    # Determine Basic Follower Page Context
    context['page_name'] = "Follower Stream"

    
    # Load User Profile
    context['profile'] = Profile.objects.get(profile_user=request.user)

    # Load all Existing Posts & Comments from followers
    followers = context['profile'].followers.all()
    try:
        posts = Post.objects.filter(profile__in=followers).order_by('-date_time')
        context['posts'] = posts
    except:
        pass

    # If GET display page
    if request.method == 'GET':
        return render(request, 'socialnetwork/follower.html', context)


"""
    @brief      :    AJAX function to refresh follower stream
    @param[in]  :
    @retval     :    
"""
def get_follower(request):
    #error handling
    if not request.user.is_authenticated:
        return json_error_handling("You must be logged in to do this operation", status=401)

    post_response = []
    comment_response = []
    post_ids = []
    # Get Follower Data
    profile = Profile.objects.get(profile_user=request.user)

    # Load all Existing Posts & Comments from followers
    followers = profile.followers.all()

    # Get all Post objects
    posts = Post.objects.filter(profile__in=followers).order_by('date_time').values()
    for post in posts:
        # Find Profile Associated with Post
        profile = Profile.objects.get(id=post['profile_id'])

        # Create JSON
        item = {
            'id': post['id'],
            'post_input_text': post['post_input_text'],
            'profile_id': post['profile_id'],
            'date_time': post['date_time'].strftime("%-m/%-d/%Y %-I:%M %p"),
            'first_name': profile.profile_user.first_name,
            'last_name': profile.profile_user.last_name
        }
        post_response.append(item)
        post_ids.append(post['id'])
    #Get all Comment objects 
    comments = Comment.objects.filter(post__in=post_ids).order_by('-date_time').values()
    for comment in comments:
        # Find Profile Associated with comment
        profile = Profile.objects.get(id=comment['profile_id'])
    
        # Find Post associated with comment
        item = {
            'id': comment['id'],
            'comment_input_text': comment['comment_input_text'],
            'profile_id': comment['profile_id'],
            'date_time': comment['date_time'].strftime("%-m/%-d/%Y %I:%M %p"),
            'post_id': comment['post_id'],
            'first_name': profile.profile_user.first_name,
            'last_name': profile.profile_user.last_name
        }

        comment_response.append(item)



    # Seraliase into a Json string
    posts_json = json.dumps({'page': 'follower', 'posts': post_response, 'comments': comment_response})

    return HttpResponse(posts_json, content_type="applications/json")


# ------------------------------------------------------------------------------------------------------------------------------#
# --- PROFILE VIEWS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
"""
    @brief      :    loads user's profile page 
    @param[in]  :
    @retval     :    render user profile page
"""
@login_required
def user_profile_action(request):
    context = {}
    
    # - CONTEXT - #
    # Determine Context for Navbar
    context['navigation_links'] = navigation_bar_setup('')

    # Set user = to current user in context
    context['user_page'] = request.user
    context['page_name'] = "Profile page for " 

    # Load User Profile
    context['profile'] = Profile.objects.get(profile_user=request.user)

    # Get List of Followers
    followers = context['profile'].followers.all()
    context["followers"] = Profile.objects.filter(profile_user__in=followers)

    # If GET display page
    if request.method == 'GET':
        # Load in Model Form 
        context['form'] = EditProfileForm(instance=context['profile'])
        return render(request, 'socialnetwork/user_profile.html', context)
    
    # If Post Request Update User Bio
    form = EditProfileForm(request.POST, request.FILES, instance=context['profile'])
    context['form'] = form

    # Check form is valid
    if not form.is_valid():
        return render(request, 'socialnetwork/user_profile.html', context)
    
    # Update Profile model
    context['profile'].user_bio = form.cleaned_data['user_bio']
    context['profile'].user_picture = form.cleaned_data['user_picture']
    context['profile'].picture_type = form.cleaned_data['user_picture'].content_type
    context['profile'].save()
    context['form'].save()

    print("set it!", form.cleaned_data['user_bio'])

    return render(request, 'socialnetwork/user_profile.html', context)


"""
    @brief      :    render user image 
    @param[in]  :
    @retval     :    None
"""
def get_user_photo(request, id):
    #Fetch photo from profile
    profile = get_object_or_404(Profile, id=id)
    print('Picture #{} fetched from db: {} (type={})'.format(id, profile.user_picture, type(profile.user_picture)))


    if not profile.user_picture:
        raise Http404



    return HttpResponse(profile.user_picture, content_type=profile.picture_type)


    

"""
    @brief      :    loads another user's profile
    @param[in]  :
    @retval     :    render profile page base + add on for 
"""
@login_required
def follower_profile_action(request, id):
    context = {}
    
    # - CONTEXT - #
    # Determine Context for Navbar
    context['navigation_links'] = navigation_bar_setup('')
    # Determine Basic Login Page Context
    context['page_name'] = "Profile page for "
    context['profile'] = Profile.objects.get(id=id)

    # Get List of Followers
    followers = context['profile'].followers.all()
    context["followers"] = Profile.objects.filter(profile_user__in=followers)

    # Check whether following if GET
    if request.method == 'GET':
        if (context['profile'].profile_user in Profile.objects.get(profile_user=request.user).followers.all()):
            context["button_text"] = "unfollow"
        else: context["button_text"] = "follow"



    # If POST process Button Form display page
    if request.method == 'POST':
        context["button_text"] = follow_unfollow_user(request, context['profile'])
    
    
    
    
    return render(request, 'socialnetwork/follower_profile.html', context)


"""
    @brief      :   Action function for user follow/unfollow
    @param[in]  :
    @retval     :   text for follow/unfollow button
"""
def follow_unfollow_user(request, profile):
    # get user's profile
    user = request.user
    user_profile = Profile.objects.get(profile_user=user)
    print(user_profile.followers.all())

    # Check if User is Currently following profile
    if (profile.profile_user in user_profile.followers.all()):
        user_profile.followers.remove(profile.profile_user)
        button_text = "follow"
    else: 
        user_profile.followers.add(profile.profile_user)
        button_text = "unfollow"

    return button_text