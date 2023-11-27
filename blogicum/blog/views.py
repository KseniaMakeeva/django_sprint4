from datetime import datetime
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView,
    ListView, UpdateView, View)
from django.urls import reverse, reverse_lazy

from blog.models import Category, Comment, Post, User

from .forms import (
    CommentForm, PostForm, RegistrationForm, UserForm)

POSTS_ON_PAGE = 10

User = get_user_model()


class CategoryPosts(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        category = get_object_or_404(Category,
                                     is_published=True,
                                     slug=self.kwargs['category_slug'])
        return category.posts.select_related(
            'author',
            'location',
            'category').filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=datetime.now()).annotate(
                    comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = (
            get_object_or_404(Category.objects.values(
                'id',
                'title',
                'description'), slug=self.kwargs['category_slug']))
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        if (
            not self.get_object().is_published and (
                self.get_object().author != request.user)):
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
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
    queryset = Post.objects.select_related(
        'category',
        'author',
        'location').filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()).annotate(
                comment_count=Count('comments')).order_by('-pub_date')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post.author != self.request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post,
                                          pk=kwargs['pk'],
                                          is_published=True,
                                          category__is_published=True,
                                          pub_date__lte=datetime.now())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs=self.kwargs)


class CommentMixin(LoginRequiredMixin, View):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment,
                                    pk=self.kwargs['comment_id'])
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm
    pass


class CommentDeleteView(CommentMixin, DeleteView):
    pass


class ProfileListView(ListView):
    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username'])
        queryset = super().get_queryset().select_related('author',
                                                         'location',
                                                         'category').filter(
            author__username=self.profile).annotate(
                comments_count=Count('comments')).order_by(
                    '-pub_date')
        if self.request.user != self.profile:
            queryset = queryset.filter(is_published=True,
                                       pub_date__lte=datetime.now(),
                                       category__is_published=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class Registration(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('blog:index')
