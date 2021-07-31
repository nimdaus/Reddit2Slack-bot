import django_filters

from .models import *

class redditFilter(django_filters.FilterSet):
    class Meta:
        model = TEST
        fields = '__all__'