from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.models.folder_models import UserFolder
from api.serializers.folder_serializers import UserFolderSerializer, UserFileSerializer
import os
from django.conf import settings
from django.http import FileResponse

class UserFolderListCreateView(APIView):
    permission_classes= [IsAuthenticated]

    def get(self, request):
        folders = UserFolder.objects.filter(user=request.user)
        serializer  = UserFolderSerializer(folders, many=True)
        return Response(serializer.data)

    def post(self, request):
        folder_name = request.data.get('folder_name')
        if not folder_name:
            return Response({'error': 'Nom du dossier requis'}, status=status.HTTP_400_BAD_REQUEST)

        folder, created = UserFolder.objects.get_or_create(user=request.user, name=folder_name)

        # 🔥 Créer le dossier physiquement
        folder_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", folder_name)
        os.makedirs(folder_path, exist_ok=True)

        return Response(UserFolderSerializer(folder).data, status=status.HTTP_201_CREATED)

class UserFolderDetailView(APIView):
    permission_classes= [IsAuthenticated]

    def get_object(self, folder_id, user):
        try:
            return UserFolder.objects.get(id=folder_id, user=user)
        except UserFolder.DoesNotExist:
            return None

    def put(self, request, folder_id):
        folder = self.get_object(folder_id, request.user)
        if not folder:
            return Response({"error": "Non autorisé ou dossier inexistant."}, status=status.HTTP_403_FORBIDDEN)

        old_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", folder.name)
        new_name = request.data.get('folder_name', folder.name)
        new_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", new_name)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)

        folder.name = new_name
        folder.save()

        return Response(UserFolderSerializer(folder).data, status=status.HTTP_200_OK)

    def delete(self, request, folder_id):
        folder = self.get_object(folder_id, request.user)
        if not folder:
            return Response({"error": "Non autorisé ou dossier inexistant."}, status=status.HTTP_403_FORBIDDEN)
        folder.delete()
        return Response({"message": "Dossier supprimé."}, status=status.HTTP_200_OK)

class UserFileListCreateView(APIView):
    permission_classes= [IsAuthenticated]

    def get(self, request, folder_id):
        files = UserFile.objects.filter(folder=folder_id)
        serializer  = UserFileSerializer(files, many=True)
        return Response(serializer.data)

    def post(self, request, folder_id):
        file = request.data.get('file')
        if not file:
            return Response({"error": "Le fichier est requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            folder = UserFolder.objects.get(id=folder_id, user=request.user)
        except UserFolder.DoesNotExist:
            return Response({"error": "Dossier non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        file_instance = UserFile.objects.create(user=request.user, folder=folder, file=file)
        return Response(UserFileSerializer(file_instance).data, status=status.HTTP_201_CREATED)

class UserFileEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        new_content = request.data.get("content")

        if not new_content:
            return Response({"error": "Le contenu est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file = UserFile.objects.get(id=file_id, user=request.user)
        except UserFile.DoesNotExist:
            return Response({"error": "Fichier non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        file_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", file.folder.name, file.file.name)

        if not os.path.exists(file_path):
            return Response({"error": "Fichier introuvable sur le serveur."}, status=status.HTTP_404_NOT_FOUND)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return Response({"message": "Fichier mis à jour avec succès."}, status=status.HTTP_200_OK)

class UserFileMoveView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        new_folder_id = request.data.get("new_folder_id")

        if not new_folder_id:
            return Response({"error": "Le nouvel ID du dossier est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file = UserFile.objects.get(id=file_id, user=request.user)
            new_folder = UserFolder.objects.get(id=new_folder_id, user=request.user)
        except (UserFile.DoesNotExist, UserFolder.DoesNotExist):
            return Response({"error": "Fichier ou dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        old_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", file.folder.name, file.file.name)
        new_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", new_folder.name, file.file.name)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)

        file.folder = new_folder
        file.save()

        return Response({"message": "Fichier déplacé avec succès."}, status=status.HTTP_200_OK)

class UserFileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        try:
            file = UserFile.objects.get(id=file_id, user=request.user)
        except UserFile.DoesNotExist:
            return Response({"error": "Fichier non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        file_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", file.folder.name, file.file.name)

        if not os.path.exists(file_path):
            return Response({"error": "Fichier introuvable sur le serveur."}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(open(file_path, 'rb'), as_attachment=True)

class UserFileDetailView(APIView):
    persission_classes= [IsAuthenticated]

    def delete(self, request, file_id):
        try:
            file = UserFile.objects.get(id=file_id, user=request.user)
        except UserFile.DoesNotExist:
            return Response({"error": "Fichier non trouvé."}, status=status.HTTP_404_NOT_FOUND)
        file.delete()
        return Response({"message": "Fichier supprimé."}, status=status.HTTP_200_OK)

class UserFileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        try:
            file = UserFile.objects.get(id=file_id, user=request.user)
        except UserFile.DoesNotExist:
            return Response({"error": "Fichier non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        new_name = request.data.get('new_name')
        if not new_name:
            return Response({"error": "Le nouveau nom est requis."}, status=status.HTTP_400_BAD_REQUEST)

        old_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", file.folder.name, file.file.name)
        new_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", file.folder.name, new_name)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)

        file.file.name = os.path.join(file.folder.name, new_name)
        file.save()

        return Response(UserFileSerializer(file).data, status=status.HTTP_200_OK)

class CreateEmptyFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, folder_id):
        file_name = request.data.get('file_name')
        if not file_name:
            return Response({'error': 'Le nom du fichier est requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            folder = UserFolder.objects.get(id=folder_id, user=request.user)
        except UserFolder.DoesNotExist:
            return Response({'error': 'Dossier non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        file_path = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}", folder.name, file_name)

        if os.path.exists(file_path):
            return Response({'error': 'Un fichier avec ce nom existe déjà'}, status=status.HTTP_400_BAD_REQUEST)

        with open(file_path, 'w') as f:
            f.write('')  # Créer un fichier vide

        file_instance = UserFile.objects.create(user=request.user, folder=folder, file=file_name)
        return Response(UserFileSerializer(file_instance).data, status=status.HTTP_201_CREATED)
