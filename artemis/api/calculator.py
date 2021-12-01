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

from latex2sympy2 import latex2sympy, latex2latex
from sympy import *

from rest_framework import serializers, viewsets, generics, views
from rest_framework.response import Response


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

