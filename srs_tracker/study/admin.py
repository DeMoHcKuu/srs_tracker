from django.contrib import admin
from .models import Deck, Card, Review, Tag


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at")
    search_fields = ("title", "description", "user__username")
    list_filter = ("created_at",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user")
    search_fields = ("name", "user__username")


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("id", "deck", "is_active", "next_review_at", "interval_days", "repetitions", "ease_factor", "created_at")
    search_fields = ("front_text", "back_text", "deck__title", "deck__user__username")
    list_filter = ("is_active", "next_review_at", "created_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "card", "quality", "reviewed_at", "next_review_at", "interval_days", "repetitions", "ease_factor")
    search_fields = ("user__username", "card__deck__title", "card__front_text")
    list_filter = ("quality", "reviewed_at", "next_review_at")
