from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# ------------------------------------------------------------------------------------------------------------------------------#
# --- USER MODELS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
class Profile(models.Model):
    #############################################################################################################################
    # @brief      :       Creates django form class for user profile
    #############################################################################################################################
    profile_user = models.ForeignKey(User, on_delete=models.PROTECT)
    user_bio = models.CharField(max_length=200, default=" ")
    user_picture = models.FileField(blank=True)
    picture_type = models.CharField(max_length=200, default="None")
    followers = models.ManyToManyField(User, blank=True, related_name="user_following")

# ------------------------------------------------------------------------------------------------------------------------------#
# --- CONTENT MODELS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
class Post(models.Model):
    #############################################################################################################################
    # @brief      :       Creates django form class for blog post
    #############################################################################################################################
    post_input_text = models.CharField(max_length=200)
    profile = models.ForeignKey(User, on_delete=models.PROTECT, related_name="post_creators")
    date_time = models.DateTimeField()




class Comment(models.Model):
    #############################################################################################################################
    # @brief      :       Creates django form class for comment post
    #############################################################################################################################
    comment_input_text = models.CharField(max_length=200)
    profile = models.ForeignKey(User, on_delete=models.PROTECT, related_name="comment_creators")
    date_time = models.DateTimeField()
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name="comment_post")