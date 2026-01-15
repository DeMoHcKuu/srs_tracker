from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Deck(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="decks")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "title"]

    def __str__(self) -> str:
        return self.title


class Tag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=40)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="cards")
    front_text = models.TextField()
    back_text = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name="cards")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    next_review_at = models.DateField(default=timezone.localdate)
    interval_days = models.PositiveIntegerField(default=0)
    repetitions = models.PositiveIntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)

    class Meta:
        ordering = ["next_review_at", "-created_at"]

    def __str__(self) -> str:
        return f"Card #{self.pk} ({self.deck.title})"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="reviews")
    reviewed_at = models.DateTimeField(auto_now_add=True)

    quality = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])

    interval_days = models.PositiveIntegerField()
    repetitions = models.PositiveIntegerField()
    ease_factor = models.FloatField()
    next_review_at = models.DateField()

    class Meta:
        ordering = ["-reviewed_at"]

    def __str__(self) -> str:
        return f"Review #{self.pk}: card={self.card_id}, q={self.quality}"
