from django.db import models

class GeneratedImage(models.Model):
    object_name = models.CharField(max_length=255)
    object_description = models.TextField()
    generated_image_url = models.URLField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='generated_images/', null=True, blank=True)  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.object_name
