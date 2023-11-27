from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post, User


class RegistrationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {'pub_date': forms.DateInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',)}


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = {
            'username',
            'first_name',
            'last_name',
            'email', }
        exclude = ('password',)
