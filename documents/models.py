from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200, default="Без названия")
    content = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class DocumentImage(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="doc_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)