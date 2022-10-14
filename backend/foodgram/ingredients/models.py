from django.db import models


class Ingredient(models.Model):
    name = models.CharField(unique=True)
    measurement_unit = models.CharField(unique=True)
