from django.db import models

class Update(models.Model):
    version      = models.CharField(max_length = 16)
    release_date = models.DateTimeField(auto_now_add = True)
    content      = models.BinaryField()
    product      = models.ForeignKey(
        to                  = 'licences.SoftwareProduct',
        on_delete           = models.CASCADE,
        related_name        = 'updates',
        related_query_name  = 'update',
        null                = False,
    )
