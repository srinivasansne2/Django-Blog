from django.urls import path
from . import views




app_name='blog'

urlpatterns = [
    path("",views.index,name="index"),
    path("post/<str:slug>",views.post,name="post"),
    path("dynamic/",views.new_url_view,name="new_url"),
    path("old_url//",views.old_url_redirect,name="old_url"),
    path("contact/",views.contact,name="contact"),
    path("about/",views.about,name="about"),
    path("register/",views.register,name="register"),
    path("login/",views.login,name="login"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("logout/",views.logout,name="logout"),
    path("forgot-password/",views.forgot_password,name="forgot_password"),
    path("reset-password/<uidb64>/<token>",views.reset_password,name="reset_password"),
    path("new-post/",views.new_post,name="new_post"),
    path("edit-post/<int:post_id>/",views.edit_post,name="edit_post"),
    path("delete-post/<int:post_id>/",views.delete_post,name="delete_post"),
    path("publish-post/<int:post_id>/",views.publish_post,name="publish_post"),
    
]
