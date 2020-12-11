from django.db import models

class Update(models.Model):
    """
    The model 'Update' is the update to roll out for a specific software product.

    Attributes:
    version      (str)      : The version number of the update
    release_date (datetime) : The day when the update is released
    content      (binary)   : Content to install the update
    product      (int)      : The product the update belongs to
    """
    version      = models.CharField(max_length = 16)
    release_date = models.DateTimeField(auto_now_add = True)
    content      = models.BinaryField()
    product      = models.ForeignKey(
        to                  = 'licenses.SoftwareProduct',
        on_delete           = models.CASCADE,
        related_name        = 'updates',
        related_query_name  = 'update',
        null                = False,
    )
