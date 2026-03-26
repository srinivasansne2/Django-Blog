from urllib import request

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
import logging
from blog.models import Category, Post,AboutUs
from django.core.paginator import Paginator
from .forms import ContactForm, ForgotPasswordForm, PostForm, RegisterForm,LoginForm, ResetPasswordForm
from django.contrib import messages
from django.contrib.auth.models import Group, User 
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group


# posts=[
#         {"id":1,"title":"First Post","content":"This is the content of the first post."},
#         {"id":2,"title":"Second Post","content":"This is the content of the second post."},
#         {"id":3,"title":"Third Post","content":"This is the content of the  third post."}  ,
#         {"id":4,"title":"Fourth Post","content":"This is the content of the  fourth post."}
#     ]

def index(request):
    blog_title="Latest Post "

    #Using this since we are using a database and not a static list of posts
    posts=Post.objects.filter(is_published= True).order_by("-created_at")

    #Pagination
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    posts= paginator.get_page(page_number)

    return render(request,"index.html",{"blog_title":blog_title, "posts":posts})

def post(request,slug):

    if not request.user.is_authenticated:
        messages.warning(request, 'You need to be logged in to view the post details.')
        return redirect('blog:login')
    #Using this we get static list of posts and not from database
    #post=next((post for post in posts if post["id"]==int(post_id)),None)

    #Using this we get post from database and not from static list of posts
    post = Post.objects.filter(slug=slug).first()
    related_posts = Post.objects.filter(category=post.category).exclude(id=post.id)[:3]

    if not post:
        raise Http404("Post not found")

    #to check in logger results in console
    # logger=logging.getLogger("Testing")
    # logger.debug(f"Post with id {post_id} accessed.")

    return render(request,"detail.html",{"post":post, "related_posts":related_posts})

def old_url_redirect(request):
    return redirect(reverse('blog:new_url'))

def new_url_view(request):
    return HttpResponse("This is the New Url")

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        logger = logging.getLogger("TESTING")
        if form.is_valid():
            logger.debug(f'POST Data is {form.cleaned_data['name']} {form.cleaned_data['email']} {form.cleaned_data['message']}')
            #send email or save in database
            success_message = 'Your Email has been sent!'
            return render(request,'contact.html', {'form':form,'success_message':success_message})
        else:
            logger.debug('Form validation failure')
        return render(request,'contact.html', {'form':form, 'name': name, 'email':email, 'message': message})
    return render(request,'contact.html')

def about(request):
    about_obj = AboutUs.objects.first()

    about_content = about_obj.content if about_obj else "This is a blog website where you can find various articles."

    return render(request, 'about.html', {'about_content': about_content})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            #add user to readers group
            readers_group,created = Group.objects.get_or_create(name="Readers")
            user.groups.add(readers_group)
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('blog:login')  # Redirect to the login page or another page
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('blog:dashboard') 

    return render(request, 'login.html' , {'form': form})

def dashboard(request):
    blog_title = "My Posts"
    #get posts of the logged in user
    all_posts = Post.objects.filter(user=request.user).order_by("-created_at")

    #Pagination
    paginator = Paginator(all_posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    posts= paginator.get_page(page_number)


    return render(request, 'dashboard.html' , {'blog_title': blog_title, 'posts': all_posts})

def logout(request):
    auth_logout(request)
    return redirect('blog:index')

def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == 'POST':
        #form
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            #send email to reset password
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            domain = current_site.domain
            subject = "Reset Password Requested"
            message = render_to_string('reset_password_email.html', {
                'domain': domain,
                'uid': uid,
                'token': token
            })

            send_mail(subject, message, 'noreply@jvlcode.com', [email])
            messages.success(request, 'Email has been sent')


    return render(request,'forgot_password.html', {'form': form})

def reset_password(request, uidb64, token):
    form = ResetPasswordForm()
    if request.method == 'POST':
        #form
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('blog:login')
            else :
                messages.error(request,'The password reset link is invalid')

    return render(request,'reset_password.html', {'form': form})

@login_required
@permission_required('blog.add_post', raise_exception=True)
def new_post(request):
    categories = Category.objects.all()
    form = PostForm()
    if request.method == 'POST':
        #form
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('blog:dashboard')
    return render(request,'new_post.html', {'categories': categories, 'form': form})

@login_required
@permission_required('blog.change_post', raise_exception=True)
def edit_post(request, post_id):
    categories = Category.objects.all()
    post = get_object_or_404(Post, id=post_id)
    form = PostForm()
    if request.method == "POST":
        #form
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post Updated Succesfully!')
            return redirect('blog:dashboard')

    return render(request,'edit_post.html', {'categories': categories, 'post': post, 'form': form})

@login_required
@permission_required('blog.delete_post', raise_exception=True)
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    messages.success(request, 'Post Deleted Succesfully!')
    return redirect('blog:dashboard')

@login_required
@permission_required('blog.can_publish', raise_exception=True)
def publish_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_published = True
    post.save()
    messages.success(request, 'Post Published Succesfully!')
    return redirect('blog:dashboard')