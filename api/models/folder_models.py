from django.db import models
from django.contrib.auth.models import User
import os
from django.core.files.storage import FileSystemStorage

class UserFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

def get_user_folder_path(instance, filename):
    return os.path.join("user_files", f"user_{instance.user.id}", instance.folder.name, filename)

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    folder = models.ForeignKey(UserFolder, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=get_user_folder_path)
    upload_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"