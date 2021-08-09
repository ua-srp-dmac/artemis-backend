import json
import requests
import time
import os
from urllib.parse import urlencode, quote

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.contrib.auth.models import User
from artemis.models import (
  Site,
  Geochemistry,
  Plot,
  Replicate
)
from rest_framework import serializers, viewsets


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name']

class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class PlotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Plot
        fields = '__all__'

class PlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plot.objects.all()
    serializer_class = PlotSerializer


class ReplicateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Replicate
        fields = '__all__'

class ReplicateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Replicate.objects.all()
    serializer_class = ReplicateSerializer


class GeochemistrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Geochemistry
        fields = '__all__'

class GeochemistryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Geochemistry.objects.all()
    serializer_class = GeochemistrySerializer

