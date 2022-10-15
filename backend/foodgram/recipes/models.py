from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=30, unique=True)
    measurement_unit = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    color = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=150)
    text = models.TextField()
    cooking_time = models.IntegerField()
    image = models.ImageField("Картинка", upload_to="recipes/media/")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient')

    class Meta:
        ordering = ["-pk"]

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients_recipes",
        null=True, blank=True,)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredients",
        null=True, blank=True,)
    amount = models.IntegerField()

    class Meta:
        ordering = ["-recipe"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique ingredient"
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="tags_recipes",
        null=True, blank=True,)
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="tags", null=True,
        blank=True,)

    class Meta:
        ordering = ["-recipe"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tag"], name="unique tag"
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_favorite",
        null=True, blank=True,)
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-user"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "favorite"], name="unique favorite"
            )
        ]

    def __str__(self):
        return f'{self.user} {self.favorite}'


class Shopping_cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_shopping_cart",
        null=True, blank=True,)
    shopping_cart = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-user"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "shopping_cart"], name="unique shopping_cart"
            )
        ]

    def __str__(self):
        return f'{self.user} {self.shopping_cart}'
