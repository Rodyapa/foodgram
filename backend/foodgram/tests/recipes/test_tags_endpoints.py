import requests
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import Recipe, Ingredient, Tag
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tests.base_test import BaseTestCase
from rest_framework.authtoken.models import Token

UserModel = get_user_model()
