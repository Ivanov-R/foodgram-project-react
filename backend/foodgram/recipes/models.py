from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='name')
    measurement_unit = models.CharField(
        max_length=30, verbose_name='measurement unit')

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='name')
    color = ColorField(default='#FF0000', verbose_name='color')
    slug = models.SlugField(unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='name')
    text = models.TextField(verbose_name='text')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='cooking time')
    image = models.ImageField(
        "Картинка", upload_to="recipes/media/", blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient')

    class Meta:
        ordering = ["-pk"]
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients_recipes"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredients"
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='amount')

    class Meta:
        ordering = ["-recipe"]
        verbose_name = 'Recipe ingredient'
        verbose_name_plural = 'Recipe ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique ingredient"
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="tags_recipes"
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="tags")

    class Meta:
        ordering = ["-recipe"]
        verbose_name = 'Recipe tag'
        verbose_name_plural = 'Recipe tags'
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tag"], name="unique tag"
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )
    favorite_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipes'
        ordering = ["-user"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "favorite_recipe"],
                name="unique favorite_recipe")]

    def __str__(self):
        return f'{self.user} {self.favorite_recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_cart")
    shopping_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart_recipes"
    )

    class Meta:
        verbose_name = 'Shopping cart recipe'
        verbose_name_plural = 'Shopping cart recipes'
        ordering = ["-user"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "shopping_recipe"],
                name="unique shopping_recipe")]

    def __str__(self):
        return f'{self.user} {self.shopping_recipe}'
