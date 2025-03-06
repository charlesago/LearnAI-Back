from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.models.blog_models import BlogPost, BlogPostLike, BlogPostComment
from api.serializers.blog_serializers import BlogPostSerializer, BlogPostCommentSerializer


class BlogPostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = BlogPost.objects.all().order_by('-created_at')
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['author'] = request.user.id
        serializer = BlogPostSerializer(data=data)

        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogPostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, post_id):
        try:
            return BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            return None

    def get(self, request, post_id):
        post = self.get_object(post_id)
        if not post:
            return Response({"error": "Publication non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BlogPostSerializer(post)
        return Response(serializer.data)


class BlogPostUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, post_id, user):
        try:
            post = BlogPost.objects.get(id=post_id, author=user)
            return post
        except BlogPost.DoesNotExist:
            return None

    def put(self, request, post_id):
        post = self.get_object(post_id, request.user)
        if not post:
            return Response({"error": "Non autorisé ou publication inexistante."}, status=status.HTTP_403_FORBIDDEN)

        serializer = BlogPostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = self.get_object(post_id, request.user)
        if not post:
            return Response({"error": "Non autorisé ou publication inexistante."}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({"message": "Publication supprimée."}, status=status.HTTP_204_NO_CONTENT)


class BlogPostUserPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        posts = BlogPost.objects.filter(author_id=user_id).order_by('-created_at')
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)


class BlogPostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            return Response({"error": "Publication non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        like, created = BlogPostLike.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            return Response({"message": "Like retiré."}, status=status.HTTP_200_OK)

        return Response({"message": "Like ajouté."}, status=status.HTTP_201_CREATED)


class BlogPostCommentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            return Response({"error": "Publication non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        comments = BlogPostComment.objects.filter(post=post).order_by('-created_at')
        serializer = BlogPostCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            return Response({"error": "Publication non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BlogPostCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogPostCommentUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, comment_id, user):
        try:
            return BlogPostComment.objects.get(id=comment_id, user=user)
        except BlogPostComment.DoesNotExist:
            return None

    def put(self, request, comment_id):
        comment = self.get_object(comment_id, request.user)
        if not comment:
            return Response({"error": "Non autorisé ou commentaire inexistant."}, status=status.HTTP_403_FORBIDDEN)

        serializer = BlogPostCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = self.get_object(comment_id, request.user)
        if not comment:
            return Response({"error": "Non autorisé ou commentaire inexistant."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({"message": "Commentaire supprimé."}, status=status.HTTP_204_NO_CONTENT)


class BlogPostUserCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        comments = BlogPostComment.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = BlogPostCommentSerializer(comments, many=True)
        return Response(serializer.data)
