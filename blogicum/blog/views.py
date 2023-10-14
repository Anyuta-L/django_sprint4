from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count


from django.http import Http404, HttpResponseRedirect


from django.shortcuts import get_object_or_404, redirect, render

from django.urls import reverse, reverse_lazy


from django.utils import timezone

from django.views.generic import (CreateView, DeleteView, DetailView, 
                                  UpdateView, View)

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

NUM_POSTS_TO_DISPLAY = 5
app_name = 'blog'


class ProfileView(View):
    def get(self, request, username):
        profile = get_object_or_404(User, username=username)
        post_list = Post.objects.filter(
            author__username=username
        ).order_by('-pub_date').annotate(num_comments=Count('comments'))
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'profile': profile,
            'page_obj': page_obj,
        }
        return render(request, 'blog/profile.html', context)


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/edit_profile.html'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_object(self, queryset=None):
        return self.request.user
    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username}) if username else reverse('blog:index')


class CreatePostView(LoginRequiredMixin, CreateView):
    def get(self, request):
        form = PostForm()
        return render(request, 'blog/create.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            username = self.request.user.username
            print(f"Username: {username}")  # Отладочный вывод

            return redirect(reverse('blog:profile', kwargs={'username': username}))
        return render(request, 'blog/create.html', {'form': form})


class EditPostView(LoginRequiredMixin, View):
    template_name = 'blog/create.html'

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id, author=request.user)
        form = PostForm(instance=post)
        return render(request, self.template_name, {'form': form})
   
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id, author=request.user)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect(reverse('blog:post_detail', args=[post_id]))
        return render(request, self.template_name, {'form': form})

    def dispatch(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        
        if post.author != request.user:
            return redirect(reverse('blog:post_detail', args=[post_id]))
        
        return super().dispatch(request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if (
            post.author == self.request.user or
            (post.is_published and post.pub_date <= timezone.now() and
            post.category.is_published)
        ):
            return post
        else: 
            raise Http404("Доступ запрещен")

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(context.get("object"), Post):
            context["comment_form"] = CommentForm()
            context['comments'] = (
                context['object'].comments.select_related('author')
                                                .order_by('pub_date')
            ) 
        return context
    

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author.username})

    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return HttpResponseRedirect(reverse('blog:index'))
        else:
            return super().delete(request, *args, **kwargs)


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
        return redirect('blog:post_detail', pk=post_id)
    

class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.post.id})
        
    def get_object(self, queryset=None):
            # Get the comment object to be edited
            comment_id = self.kwargs.get('pk')
            return get_object_or_404(Comment, pk=comment_id, author=self.request.user)
    
    def form_valid(self, form):
        comment = self.get_object()
        if self.request.user != comment.author and not self.request.user.is_staff:
            raise Http404("You don't have permission to edit this comment.")
        return super().form_valid(form)
    

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.post.id])
    
    def get_object(self, queryset=None):
            # Get the comment object to be edited
            comment_id = self.kwargs.get('pk')
            return get_object_or_404(Comment, pk=comment_id, author=self.request.user)
    
    def form_valid(self, form):
        comment = self.get_object()
        if self.request.user != comment.author and not self.request.user.is_staff:
            raise Http404("You don't have permission to edit this comment.")
        return super().form_valid(form)
    
            
def index(request):
    post_lists = Post.objects.all().filter(
        pub_date__lt=timezone.now(),
        is_published=True,
        category__is_published=True
        ).order_by('-pub_date').annotate(num_comments=Count('comments'))
    paginator = Paginator(post_lists, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    post_list = Post.objects.filter(
        category__slug=category_slug,
        is_published=True,
        pub_date__lte=timezone.now(),
    ).order_by('-pub_date').annotate(num_comments=Count('comments'))
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj
    }
    
    return render(request, 'blog/category.html', context)

