from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView,
    ListView, UpdateView)
from django.urls import reverse, reverse_lazy

from blog.models import Category, Post, User
from .forms import (
    CommentForm, PostForm, RegistrationForm, UserForm)
from .utils import (
    annotate_comments,
    CommentMixin,
    filtered_posts,
    PostMixin,
    UserIsAuthorMixin)

POSTS_ON_PAGE = 10

User = get_user_model()


class CategoryPosts(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_ON_PAGE

    def get_object(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)

    def get_queryset(self):
        return annotate_comments(filtered_posts(
            self.get_object().posts))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['category'] = category
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        if (
            not self.get_object().is_published
            and request.user != self.get_object().author
        ):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_ON_PAGE
    queryset = annotate_comments(filtered_posts(Post.objects))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(PostMixin, UpdateView):
    pass


class PostDeleteView(PostMixin, DeleteView):
    pass


class CommentCreateView(CommentMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['pk'])
        return super().form_valid(form)


class CommentUpdateView(UserIsAuthorMixin, CommentMixin, UpdateView):
    pass


class CommentDeleteView(UserIsAuthorMixin, CommentMixin, DeleteView):
    pass


class ProfileListView(ListView):
    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username'])

    def get_queryset(self):
        profile = self.get_object()
        posts = annotate_comments(profile.posts)
        if self.request.user != profile:
            posts = filtered_posts(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class Registration(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('blog:index')
