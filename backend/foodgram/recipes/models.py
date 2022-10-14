from django.db import models
from ingredients.models import Ingredient
from tags.models import Tag
from users.models import CustomUser


class Recipe(models.Model):
    name = models.CharField()
    text = models.TextField()
    cooking_time = models.IntegerField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="recipes"
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
    )
    image = models.ImageField("Картинка", upload_to="recipes/")

    # class Meta:
    #     ordering = ["-pub_date", "-pk"]

    def __str__(self) -> str:
        return self.text[:15]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'
