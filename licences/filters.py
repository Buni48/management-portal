import django_filters

from .models import *


class LicenceFilter(django_filters.FilterSet):
    class Meta:
        model = Licence
        fields = '__all__'
