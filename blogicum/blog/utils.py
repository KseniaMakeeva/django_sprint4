from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse

from blog.models import Post
from .models import Post, Comment
from .forms import PostForm, CommentForm


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['pk']})


class UserIsAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(LoginRequiredMixin, UserIsAuthorMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


def annotate_comments(queryset):
    return queryset.select_related(
        'author',
        'location',
        'category').annotate(
            comment_count=Count('comments')).order_by('-pub_date')


def filtered_posts(queryset):
    return queryset.filter(is_published=True,
                           category__is_published=True,
                           pub_date__lte=datetime.now())
