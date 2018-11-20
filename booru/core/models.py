from django.db import models

class BannedHash(models.Model):
    content = models.CharField(max_length=100, blank=False)
    
    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = 'Banned hashes (MD5)'