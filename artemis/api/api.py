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
  Replicate,
  Treatment
)
from rest_framework import serializers, viewsets, generics, views
from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = ['label', 'description']

class TreatmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Treatment.objects.all()
    serializer_class = TreatmentSerializer

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name']

class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class PlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plot
        fields = '__all__'

class PlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plot.objects.all()
    serializer_class = PlotSerializer


class ReplicateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Replicate
        fields = '__all__'

class ReplicateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Replicate.objects.all()
    serializer_class = ReplicateSerializer


class GeochemistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geochemistry
        fields = '__all__'

class GeochemistryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Geochemistry.objects.all()
    serializer_class = GeochemistrySerializer


# class SiteGeochemistryList(generics.ListAPIView):
#     serializer_class = GeochemistrySerializer

#     def get_queryset(self):
#         """
#         This view should return a list of all the Geochemistry entries for
#         the site as determined by the site_id portion of the URL.
#         """

#         site_id = self.kwargs['site_id']
#         return Geochemistry.objects.filter(site=site_id)


class SiteGeochemistryList(views.APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        Return a list of all users.
        """

        site_id = kwargs['site_id']
        site_geochem = Geochemistry.objects.filter(site=site_id)
        
        
        
        
        
        geochem = GeochemistrySerializer(site_geochem, many=True)
        return Response(geochem.data)