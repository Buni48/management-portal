from django.db import models

class Update(models.Model):
    version      = models.CharField(max_length = 16)
    release_date = models.DateTimeField(auto_now_add = True)
    software     = models.ForeignKey(to = 'licences.Software', on_delete = models.CASCADE, null = False)
    active       = models.BooleanField(default = True)
