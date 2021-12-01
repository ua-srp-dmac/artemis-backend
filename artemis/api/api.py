import json
import requests
import time
import os
from urllib.parse import urlencode, quote

from latex2sympy2 import latex2sympy, latex2latex
from sympy import *

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
        fields = ['id', 'name', 'latitude', 'longitude']

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


class SiteExtractionsCached(views.APIView):

    def get(self, request, *args, **kwargs):

        json_data = cache.get('site-extractions')
        return JsonResponse(json_data, safe=False)


class SiteReplicates(generics.ListAPIView):

    serializer_class = ReplicateSerializer

    def get_queryset(self):
        
        site_id = self.kwargs.get('site_id', None)

        queryset = Replicate.objects.filter(plot__site_id=site_id)
        return queryset


class SiteGeochemPoints(views.APIView):

    def get(self, request, *args, **kwargs):

        site_id = kwargs['site_id']
        site_geochem = Geochemistry.objects.filter(site=site_id)

        points = []

        for geochem in site_geochem:

            for element in elements:
                point = {}
                point['element'] = element,
                point['element_amount'] = getattr(geochem, element)
                point['depth'] =  str(geochem.min_depth) + '-' + str(geochem.max_depth),
                point['time'] = geochem.time_label
                point['treatment'] = geochem.replicate.plot.treatment.label if geochem.replicate else None
                point['replicate'] = geochem.replicate.id if geochem.replicate else None
                points.append(point)
        
        response = {
            'points': points
        }

        cache.set('site-geochem-points', response)

        return JsonResponse(response, safe=False)

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

        cache.set('site-extractions', response)

        return JsonResponse(response, safe=False)
    

class LatexCalculator(views.APIView):

    def get(self, request, *args, **kwargs):
        
        # vector values for variables
        variable_vector = json.loads(request.query_params['variableVector'])

        # latex string
        latex = request.query_params['latex']
        max_length = request.query_params['maxVectorLength']
        solution_var = request.query_params['solutionVar']

        print(latex)

        # remove spaces from latex string
        latex_clean = latex.replace("\\ ", "")
        latex_clean = latex_clean.replace("=", "==")
        print(latex_clean)
        
        # vector data only
        var_vectors_clean = {}
        # store Sympy indexed bases for each variable
        var_sympy_objects = {}

        for var_name in variable_vector:
            var_sympy_objects[var_name] = IndexedBase(var_name + "_vec")
            vector = variable_vector[var_name]
            vector_array = []

            for element in vector:
                vector_array.append(element['element_amount'])
            
            var_vectors_clean[var_name] = Array(vector_array)

        print(latex_clean)
        sympy = latex2sympy(latex_clean)
        print(sympy)
 
        # search for sums or products within expression
        sums = sympy.find(Sum)
        products = sympy.find(Product)
        
        sum_vars = []
        
        for s in sums:
            
            s_args = s.args
            for i in range(len(s_args)):
                if i > 0:
                    sum_var = s_args[i][0]
                    if sum_var not in sum_vars:
                        sum_vars.append(sum_var)
        
        for s in products:
            s_args = s.args
            for i in range(len(s_args)):
                if i > 0:
                    sum_var = s_args[i][0]
                    if sum_var not in sum_vars:
                        sum_vars.append(sum_var)

        atoms = sympy.atoms(Symbol)

        sum_var_symbols = {}
        for var in sum_vars:
            sum_var_symbols[var] = symbols(str(var))
        

        for atom in atoms:
        
            for var_name in variable_vector:
                atom_str = str(atom)
                if atom_str.startswith(var_name + "_{"):
                    subscript = atom_str[atom_str.find("{")+1:atom_str.find("}")]
                    sympy = sympy.subs(atom_str, var_sympy_objects[var_name][subscript]) 
                elif atom_str.startswith(var_name + "_"):
                    subscript = atom_str[2:]
                    sympy = sympy.subs(atom_str, var_sympy_objects[var_name][subscript]) 

        solutions = []

        for i in range(0, int(max_length)):
            
            result = {}
            subs = {}

            for var_name in variable_vector:
            
                vector = variable_vector[var_name]
                print(vector)

                if len(vector) == 1:
                    result[var_name] = vector[0]
                    subs[var_name] = vector[0]['element_amount']
                else:
                    result[var_name] = vector[i]
                    subs[var_name] = vector[i]['element_amount']
            
                subs[var_name + "_vec"] = var_vectors_clean[var_name]

            result[solution_var] = {}
            sympy_result = sympy.evalf(subs=subs)
            print(sympy_result)
            var_result = solve(sympy_result, solution_var)
            print(var_result)
            result[solution_var]['element_amount'] = str(var_result[0])
            solutions.append(result)
    
        response = {
            'solution': solutions
        }

        return JsonResponse(response, safe=False)


class SimpleCalculator(views.APIView):

    def get(self, request, *args, **kwargs):
        
        # vector values for variables
        variable_vector = json.loads(request.query_params['variableVector'])

        # latex string
        latex = request.query_params['latex']
        max_length = request.query_params['maxVectorLength']
        solution_var = request.query_params['solutionVar']

        print(latex)

        # remove spaces from latex string
        latex_clean = latex.replace("\\ ", "")
        latex_clean = latex_clean.replace("^", "**")
        print(latex_clean)
        
        # vector data only
        var_vectors_clean = {}
        # store Sympy indexed bases for each variable
        var_sympy_objects = {}

        for var_name in variable_vector:
            var_sympy_objects[var_name] = IndexedBase(var_name + "_vec")
            vector = variable_vector[var_name]
            vector_array = []

            for element in vector:
                vector_array.append(element['element_amount'])
            
            var_vectors_clean[var_name] = Array(vector_array)

        print(latex_clean)
        print("HEREEEEEE")
        print(latex_clean.split("="))
        sympy = Eq(*map(parse_expr, latex_clean.split("=")))
        # sympy = latex2sympy(latex_clean)
        print(sympy)
 
        # search for sums or products within expression
        sums = sympy.find(Sum)
        products = sympy.find(Product)
        
        sum_vars = []
        
        for s in sums:
            
            s_args = s.args
            for i in range(len(s_args)):
                if i > 0:
                    sum_var = s_args[i][0]
                    if sum_var not in sum_vars:
                        sum_vars.append(sum_var)
        
        for s in products:
            s_args = s.args
            for i in range(len(s_args)):
                if i > 0:
                    sum_var = s_args[i][0]
                    if sum_var not in sum_vars:
                        sum_vars.append(sum_var)

        atoms = sympy.atoms(Symbol)

        sum_var_symbols = {}
        for var in sum_vars:
            sum_var_symbols[var] = symbols(str(var))
        

        for atom in atoms:
        
            for var_name in variable_vector:
                atom_str = str(atom)
                if atom_str.startswith(var_name + "_{"):
                    subscript = atom_str[atom_str.find("{")+1:atom_str.find("}")]
                    sympy = sympy.subs(atom_str, var_sympy_objects[var_name][subscript]) 
                elif atom_str.startswith(var_name + "_"):
                    subscript = atom_str[2:]
                    sympy = sympy.subs(atom_str, var_sympy_objects[var_name][subscript]) 

        solutions = []

        for i in range(0, int(max_length)):
            
            result = {}
            subs = {}

            for var_name in variable_vector:
            
                vector = variable_vector[var_name]
                print(vector)

                if len(vector) == 1:
                    result[var_name] = vector[0]
                    subs[var_name] = vector[0]['element_amount']
                else:
                    result[var_name] = vector[i]
                    subs[var_name] = vector[i]['element_amount']
            
                subs[var_name + "_vec"] = var_vectors_clean[var_name]

            result[solution_var] = {}
            sympy_result = sympy.evalf(subs=subs)
            print(sympy_result)
            var_result = solve(sympy_result, solution_var)
            print(var_result)
            result[solution_var]['element_amount'] = str(var_result[0])
            solutions.append(result)
    
        response = {
            'solution': solutions
        }

        return JsonResponse(response, safe=False)