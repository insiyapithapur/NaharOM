from django.shortcuts import render

# for rest framework
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

import logging

logger = logging.getLogger(__name__)
