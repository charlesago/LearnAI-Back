from django.urls import path
from api.views.auth_views import RegisterView, LoginView, ProfileView
from api.views.blog_views import BlogPostListCreateView, BlogPostDetailView,BlogPostLikeToggleView,BlogPostCommentListCreateView, BlogPostUpdateDeleteView,BlogPostUserPostsView,BlogPostCommentUpdateDeleteView,BlogPostUserCommentsView
from api.views.folder_views import UserFolderListCreateView, UserFolderDetailView, UserFileListCreateView, UserFileDetailView,CreateEmptyFileView,UserFileUpdateView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='complete-profile'),

    path('folders/', UserFolderListCreateView.as_view(), name='folder-list-create'),
    path('folders/<int:folder_id>/', UserFolderDetailView.as_view(), name='folder-detail'),
    path('folders/<int:folder_id>/files/', UserFileListCreateView.as_view(), name='file-list-create'),
    path('files/<int:file_id>/', UserFileDetailView.as_view(), name='file-detail'),
    path('folders/<int:folder_id>/create-file/', CreateEmptyFileView.as_view(), name='create-empty-file'),
    path('files/<int:file_id>/update/', UserFileUpdateView.as_view(), name='file-update'),

    path('blog/', BlogPostListCreateView.as_view(), name='blog-list-create'),
    path('blog/<int:post_id>/', BlogPostDetailView.as_view(), name='blog-detail'),
    path('blog/<int:post_id>/update/', BlogPostUpdateDeleteView.as_view(), name='blog-update'),
    path('blog/<int:post_id>/delete/', BlogPostUpdateDeleteView.as_view(), name='blog-delete'),
    path('blog/user/<int:user_id>/', BlogPostUserPostsView.as_view(), name='blog-user-posts'),

    path('blog/<int:post_id>/like/', BlogPostLikeToggleView.as_view(), name='blog-like-toggle'),
    path('blog/<int:post_id>/comments/', BlogPostCommentListCreateView.as_view(), name='blog-comments-list-create'),
    path('blog/comments/<int:comment_id>/update/', BlogPostCommentUpdateDeleteView.as_view(), name='comment-update'),
    path('blog/comments/<int:comment_id>/delete/', BlogPostCommentUpdateDeleteView.as_view(), name='comment-delete'),
    path('blog/comments/user/<int:user_id>/', BlogPostUserCommentsView.as_view(), name='user-comments'),
]

