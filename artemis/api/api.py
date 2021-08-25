import json
import requests
import time
import os
from urllib.parse import urlencode, quote

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Avg
from django.core.cache import cache 

from django.contrib.auth.models import User
from django.shortcuts import render
from artemis.models import (
  Site,
  Geochemistry,
  Plot,
  Replicate,
  Treatment,
  Mineralogy,
  Extraction
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
        fields = ['id', 'name', 'coordinates']

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

class SiteGeochemistryCached(views.APIView):

    def get(self, request, *args, **kwargs):

        json_data = cache.get('site-geochem')
        return JsonResponse(json_data, safe=False)

class SiteMineralogyCached(views.APIView):

    def get(self, request, *args, **kwargs):

        json_data = cache.get('site-mineralogy')
        return JsonResponse(json_data, safe=False)


class SiteGeochemistry(views.APIView):
    """
    Gets site geochemistry data for all time points, treatments, elements, and depths.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):

        elements = [
            'Ag',
            'Al',
            'As',
            'Au',
            'Ba',
            'Be',
            'Bi',
            'Br',
            'Ca',
            'Cd',
            'Ce',
            'Co',
            'Cr',
            'Cs',
            'Cu',
            'Dy',
            'Er',
            'Eu',
            'Fe',
            'Ga',
            'Gd',
            'Ge',
            'Hf',
            'Ho',
            'In',
            'Ir',
            'K',
            'La',
            'Lu',
            'Mg',
            'Mn',
            'Mo',
            'Na',
            'Nb',
            'Nd',
            'Ni',
            'P',
            'Pb',
            'Pr',
            'Rb',
            'S',
            'Sb',
            'Sc',
            'Se',
            'Si',
            'Sm',
            'Sn',
            'Sr',
            'Ta',
            'Tb',
            'Th',
            'Ti',
            'Tl',
            'Tm',
            'U',
            'V',
            'W',
            'Y',
            'Yb',
            'Zn',
            'Zr',
        ]

        depths_time0 = [
            [0, 5],
            [5, 15],
            [15, 25], 
            [25, 35],
            [35, 38],
            [38, 54],
            [180, 183],
        ]

        depths = [
            [0, 20],
            [20, 40], 
            [40, 60],
            [60, 90]
        ]

        depths_mapping = {
            '0-20': [[0, 5], [5, 15], [15, 25]],
            '20-40': [[25, 35], [35, 38]],
            '40-60': [[38, 54]],
            '60-90': [],
        }


        site_id = kwargs['site_id']
        site_geochem = Geochemistry.objects.filter(site=site_id)
        
        response = {}
        time_labels = list(site_geochem.values_list('time_label', flat=True).distinct())

        # get plots, replicates & treatments for this site
        replicate_ids = site_geochem.exclude(replicate=None).values_list('replicate', flat=True).distinct()
        replicates = Replicate.objects.filter(id__in=replicate_ids)
        plots = Plot.objects.filter(site_id=site_id)
        treatment_ids = plots.values_list('treatment', flat=True).distinct()
        
        for time in time_labels:
            response[time] = {}

            for treatment_id in treatment_ids:
                treatment_name = Treatment.objects.get(id=treatment_id).description
                response[time][treatment_name] = {}
                response[time]['raw'] = {}
                treatment_replicates = replicates.filter(plot__treatment=treatment_id)
                treatment_geochem = site_geochem.filter(time_label=time, replicate__in=treatment_replicates)

                for element in elements:
                    response[time][treatment_name][element] = {}

                    if time == 0:
                        response[time]['raw'][element] = {}
                        for depth in depths_time0:
                            min_depth = depth[0]
                            max_depth = depth[1]
                            depth_str = '{}-{}'.format(min_depth, max_depth)
                            depth_geochem = site_geochem.get(min_depth=min_depth, time_label=0)
                            response[time]['raw'][element][depth_str] = getattr(depth_geochem, element)
                
                    for depth in depths:
                        min_depth = depth[0]
                        max_depth = depth[1]
                        depth_str = '{}-{}'.format(min_depth, max_depth)

                        if time == 0:
                            approx_depths = depths_mapping[depth_str]
                            approx_mins = [item[0] for item in approx_depths]
                            depth_geochem = site_geochem.filter(time_label=time, min_depth__in=approx_mins)
                            response[time][treatment_name][element][depth_str] = depth_geochem.aggregate(Avg(element))[ element + '__avg']
                        else:
                            depth_geochem = treatment_geochem.filter(time_label=time, min_depth=min_depth)
                            response[time][treatment_name][element][depth_str] = depth_geochem.aggregate(Avg(element))[ element + '__avg']

        cache.set('site-geochem', response)

        return JsonResponse(response, safe=False)

class SiteMineralogy(views.APIView):
    """
    Gets site geochemistry data for all time points, treatments, elements, and depths.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):

        minerals = [
            'quartz',
            'plagioclase',
            'illite',
            'chlorite',
            'kaolinite',
            'pyrite',
            'gypsum',
            'jarosite',
            'melanternite',
            'ankerite',
            'siderite',
            'amorphous',
        ]
        
        depths_time0 = [
            [0, 5],
            [5, 15],
            [15, 25], 
            [25, 35],
            [35, 38],
            [38, 54],
            [180, 183],
        ]

        depths = [
            [0, 20],
            [20, 40], 
            [40, 60],
            [60, 90]
        ]

        depths_mapping = {
            '0-20': [[0, 5], [5, 15], [15, 25]],
            '20-40': [[25, 35], [35, 38]],
            '40-60': [[38, 54]],
            '60-90': [],
        }

        site_id = kwargs['site_id']
        site_mineralogy = Mineralogy.objects.filter(site=site_id)
        
        response = {}
        time_labels = list(site_mineralogy.values_list('time_label', flat=True).distinct())

        # get plots, replicates & treatments for this site
        replicate_ids = site_mineralogy.exclude(replicate=None).values_list('replicate', flat=True).distinct()
        replicates = Replicate.objects.filter(id__in=replicate_ids)
        plots = Plot.objects.filter(site_id=site_id)
        treatment_ids = plots.values_list('treatment', flat=True).distinct()
        
        for time in time_labels:
            response[time] = {}

            for treatment_id in treatment_ids:
                treatment_name = Treatment.objects.get(id=treatment_id).description
                response[time][treatment_name] = {}
                response[time]['raw'] = {}
                treatment_replicates = replicates.filter(plot__treatment=treatment_id)
                treatment_mineralogy = site_mineralogy.filter(time_label=time, replicate__in=treatment_replicates)

                for mineral in minerals:
                    response[time][treatment_name][mineral] = {}
                    
                    if time == 0:
                        response[time]['raw'][mineral] = {}
                        for depth in depths_time0:
                            min_depth = depth[0]
                            max_depth = depth[1]
                            depth_str = '{}-{}'.format(min_depth, max_depth)
                            depth_mineralogy = site_mineralogy.get(min_depth=min_depth, time_label=0)
                            response[time]['raw'][mineral][depth_str] = getattr(depth_mineralogy, mineral)

                    for depth in depths:
                        min_depth = depth[0]
                        max_depth = depth[1]
                        depth_str = '{}-{}'.format(min_depth, max_depth)

                        if time == 0:
                            approx_depths = depths_mapping[depth_str]
                            approx_mins = [item[0] for item in approx_depths]
                            depth_mineralogy = site_mineralogy.filter(time_label=time, min_depth__in=approx_mins)
                            response[time][treatment_name][mineral][depth_str] = depth_mineralogy.aggregate(Avg(mineral))[ mineral + '__avg']
                        else:
                            depth_mineralogy = treatment_mineralogy.filter(min_depth=min_depth)
                            response[time][treatment_name][mineral][depth_str] = depth_mineralogy.aggregate(Avg(mineral))[ mineral + '__avg']

        cache.set('site-mineralogy', response)

        return JsonResponse(response, safe=False)


class SiteExtractions(views.APIView):
    """
    Gets site geochemistry data for all time points, treatments, elements, and depths.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):

        elements = [
            'Al',
            'As',
            'Ca',   
            'Cr',    
            'Fe',
            'K',     
            'Mg',
            'Mn',     
            'Pb',
            'Ti',
            'Zn',
        ]

        solvents = [
            'H20',
            'AmNO3',
            'AAc',
            'PO4',
            'AAO',
            'CDB',
        ]

        depths_time0 = [
            [0, 5],
            [5, 15],
            [15, 25], 
            [25, 35],
            [35, 38],
            [38, 54],
            [180, 183],
        ]

        depths = [
            [0, 20],
            [20, 40], 
            [40, 60],
            [60, 90]
        ]

        depths_mapping = {
            '0-20': [[0, 5], [5, 15], [15, 25]],
            '20-40': [[25, 35], [35, 38]],
            '40-60': [[38, 54]],
            '60-90': [],
        }

        site_id = kwargs['site_id']
        site_extractions = Extraction.objects.filter(site=site_id)
        
        response = {}
        time_labels = list(site_extractions.values_list('time_label', flat=True).distinct())

        # get plots, replicates & treatments for this site
        replicate_ids = site_extractions.exclude(replicate=None).values_list('replicate', flat=True).distinct()
        replicates = Replicate.objects.filter(id__in=replicate_ids)
        plots = Plot.objects.filter(site_id=site_id)
        treatment_ids = plots.values_list('treatment', flat=True).distinct()
        
        response['raw'] = {}
        for time in time_labels:
            response[time] = {}

            for element in elements:
                response[time][element] = {}
                response['raw'][element] = {}

                for solvent in solvents:

                    response[time][element][solvent] = {}

                    if time == 0:
                        
                        response['raw'][element][solvent] = {}

                        for depth in depths_time0:
                            min_depth = depth[0]
                            max_depth = depth[1]
                            depth_str = '{}-{}'.format(min_depth, max_depth)
                            depth_extraction = site_extractions.get(min_depth=min_depth, time_label=0, element=element)
                            response['raw'][element][solvent][depth_str] = getattr(depth_extraction, solvent)
                
                    for depth in depths:
                        min_depth = depth[0]
                        max_depth = depth[1]
                        depth_str = '{}-{}'.format(min_depth, max_depth)

                        if time == 0:
                            approx_depths = depths_mapping[depth_str]
                            approx_mins = [item[0] for item in approx_depths]
                            depth_extractions = site_extractions.filter(time_label=time, min_depth__in=approx_mins, element=element)
                            response[time][element][solvent][depth_str] = depth_extractions.aggregate(Avg(solvent))[ solvent + '__avg']
                        else:
                            depth_extractions = site_extractions.filter(time_label=time, min_depth=min_depth, element=element)
                            response[time][element][treatment_name][depth_str] = depth_extractions.aggregate(Avg(solvent))[ solvent + '__avg']

        cache.set('site-extraction', response)

        return JsonResponse(response, safe=False)