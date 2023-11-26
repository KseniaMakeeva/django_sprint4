from django import forms
# from django.core.exceptions import ValidationError
# from django.core.mail import send_mail

from .models import Comment, Post, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {'post': forms.DateInput(attrs={'type': 'date'})}


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
            'email'
        }
