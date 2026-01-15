from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import Deck, Card


class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ["title", "description"]


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["front_text", "back_text", "tags", "is_active"]


class ReviewQualityForm(forms.Form):
    card_id = forms.IntegerField(min_value=1)
    quality = forms.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
