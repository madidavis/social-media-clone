from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from socialnetwork.models import Post, Comment, Profile

# ------------------------------------------------------------------------------------------------------------------------------#
# --- LOGIN FORMS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
class LoginForm(forms.Form):
    #############################################################################################################################
    # @brief      :       Creates django form class for user logins
    #############################################################################################################################
    username = forms.CharField(max_length = 20)                                         #< Unique Username Input for Site
    password = forms.CharField(max_length = 200, widget=forms.PasswordInput())          #< Unique User Password

    # -- CLASS METHODS -- #
    """
        @brief      :       Custom form validation that applies to multiple fields
        @note       :       Overrides the forms.Form.clean function
    """
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirm the Password is correct for given username
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid Username/Password")

        return cleaned_data



# ------------------------------------------------------------------------------------------------------------------------------#
# --- REGISTRATION FORMS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
class RegisterForm(forms.Form):  
    #############################################################################################################################
    # @brief      :       Creates django form class for user account registration
    #############################################################################################################################
    username = forms.CharField(max_length = 20)                                             #< Unique Username Input for Site
    password = forms.CharField(max_length = 200, widget=forms.PasswordInput())              #< Unique User Password
    confirm_password =  forms.CharField(max_length = 200, widget=forms.PasswordInput())     #< Password Confirmation Input
    email = forms.CharField(max_length = 50, widget= forms.EmailInput())                    #< Email Linked to User Account
    first_name = forms.CharField(max_length = 20)                                           #< User's First Name
    last_name = forms.CharField(max_length = 20)                                            #< User's Last Name 


    # -- CLASS METHODS -- #
    """
        @brief      :       Custom form validation that applies to multiple fields
        @note       :       Overrides the forms.Form.clean function
    """
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirm the Password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if (password and confirm_password) and (password != confirm_password):
            raise forms.ValidationError("Passwords did not Match")

        return cleaned_data

# ------------------------------------------------------------------------------------------------------------------------------#
# --- PROFILE FORMS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
class UserProfileForm(forms.Form):
    #############################################################################################################################
    # @brief      :       Creates django form class for user to edit their profile page
    #############################################################################################################################
    bio_input_text = forms.CharField(widget=forms.Textarea)

class EditProfileForm(forms.ModelForm):
    #############################################################################################################################
    # @brief      :       Creates django form class for user to edit their profile page
    #############################################################################################################################
    class Meta:
        model = Profile
        exclude = (
            'profile_user',
            'followers',
            'picture_type'
        )
        widgets = {
            'user_bio': forms.Textarea(attrs={'id': 'id_bio_input_text',}),
            'user_picture': forms.ClearableFileInput(attrs={'id': 'id_profile_picture', 'class' : 'btn btn-light mx-2'}),
        }


# ------------------------------------------------------------------------------------------------------------------------------#
# --- CONTENT FORMS --- #
# ------------------------------------------------------------------------------------------------------------------------------#
class CreatePostForm(forms.ModelForm):
    #############################################################################################################################
    # @brief      :       Creates django form class to create post from post model
    #############################################################################################################################
    class Meta:
        model = Post
        exclude = (
            'profile',
            'date_time'
        )
        widgets = {
            'date_time': forms.HiddenInput(),
            'post_input_text': forms.TextInput(attrs={'id': 'id_post_input_text','class': 'form-control px-2'}),
        }


class CreateCommentForm(forms.ModelForm):
    #############################################################################################################################
    # @brief      :       Creates django form class to create comment from post comment
    #############################################################################################################################
    class Meta:
        model = Comment 
        exclude = (
            'profile',
            'date_time'
        )
        widgets = {
            'date_time': forms.HiddenInput(),
            'input_text': forms.Textarea()
        }