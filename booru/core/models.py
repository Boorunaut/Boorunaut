from django.db import models

class BannedHash(models.Model):
    content = models.CharField(max_length=32, blank=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    update_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    creator = models.ForeignKey('account.Account', null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = 'Banned hashes (MD5)'
        permissions = (
            ("ban_hashes", "Can ban hashes of media"),
        )

class PostFlag(models.Model):
    post = models.ForeignKey('booru.Post', on_delete=models.CASCADE)
    reason = models.CharField(max_length=500, blank=False)
    creator = models.ForeignKey('account.Account', null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    update_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)

    PENDING = 0
    RESOLVED = 1
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (RESOLVED, 'Resolved'),
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    
    def __str__(self):
        return "{} -> {}".format(self.id, self.post)

    class Meta:
        verbose_name_plural = 'Post flags'
