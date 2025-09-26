from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Post, Comment
from .forms import CommentForm


# -----------------------------
# Home page: shows all posts with like + comment counts
# -----------------------------
def home(request):
    posts = Post.objects.all().order_by("-date_posted")
    return render(request, "blog/home.html", {"posts": posts})


# -----------------------------
# Class-based views
# -----------------------------
class PostListView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = "blog/user_posts.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_posted")


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context["comments"] = post.comments.all().order_by("-created_at")
        context["form"] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "content"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "content"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("blog-home")  # <-- use your URL name

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


# -----------------------------
# About page
# -----------------------------
def about(request):
    return render(request, "blog/about.html", {"title": "about"})


# -----------------------------
# Like / Unlike toggle
# -----------------------------
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)  # unlike
    else:
        post.likes.add(request.user)     # like
    return redirect("blog-home")        # <-- redirect to homepage


# -----------------------------
# Add comment to a post
# -----------------------------
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user  # assuming Comment model has 'user'
            comment.save()
    return redirect("post-detail", pk=pk)

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)

    # Only allow the comment owner to edit
    if comment.user != request.user:
        return redirect('post-detail', pk=comment.post.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post-detail', pk=comment.post.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, id=pk)

    # Only allow the comment owner to delete
    if comment.user == request.user:
        post_id = comment.post.id
        comment.delete()
        return redirect('post-detail', pk=post_id)
    return redirect('post-detail', pk=comment.post.id)

