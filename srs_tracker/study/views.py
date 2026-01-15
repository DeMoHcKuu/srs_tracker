from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

import plotly.express as px

from .forms import DeckForm, CardForm, ReviewQualityForm
from .models import Deck, Card, Review
from .services import sm2_calculate


class HomeView(TemplateView):
    template_name = "study/home.html"


class DeckListView(LoginRequiredMixin, ListView):
    template_name = "study/deck_list.html"
    context_object_name = "decks"

    def get_queryset(self):
        return Deck.objects.filter(user=self.request.user)


class DeckCreateView(LoginRequiredMixin, CreateView):
    template_name = "study/deck_form.html"
    form_class = DeckForm
    success_url = reverse_lazy("deck_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DeckUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "study/deck_form.html"
    form_class = DeckForm
    success_url = reverse_lazy("deck_list")

    def get_queryset(self):
        return Deck.objects.filter(user=self.request.user)


class DeckDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "study/deck_confirm_delete.html"
    success_url = reverse_lazy("deck_list")

    def get_queryset(self):
        return Deck.objects.filter(user=self.request.user)


class CardListView(LoginRequiredMixin, ListView):
    template_name = "study/card_list.html"
    context_object_name = "cards"

    def dispatch(self, request, *args, **kwargs):
        self.deck = get_object_or_404(Deck, pk=kwargs["deck_id"], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Card.objects.filter(deck=self.deck).select_related("deck").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["deck"] = self.deck
        return ctx


class CardCreateView(LoginRequiredMixin, CreateView):
    template_name = "study/card_form.html"
    form_class = CardForm

    def dispatch(self, request, *args, **kwargs):
        self.deck = get_object_or_404(Deck, pk=kwargs["deck_id"], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.deck = self.deck
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("card_list", kwargs={"deck_id": self.deck.id})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["deck"] = self.deck
        return ctx


class CardUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "study/card_form.html"
    form_class = CardForm

    def get_queryset(self):
        return Card.objects.filter(deck__user=self.request.user).select_related("deck")

    def get_success_url(self):
        return reverse("card_list", kwargs={"deck_id": self.object.deck_id})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["deck"] = self.object.deck
        return ctx


class CardDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "study/card_confirm_delete.html"

    def get_queryset(self):
        return Card.objects.filter(deck__user=self.request.user).select_related("deck")

    def get_success_url(self):
        return reverse("card_list", kwargs={"deck_id": self.object.deck_id})


class ReviewTodayView(LoginRequiredMixin, TemplateView):
    template_name = "study/review_today.html"

    def get_due_cards_qs(self):
        today = timezone.localdate()
        return (
            Card.objects.filter(deck__user=self.request.user, is_active=True, next_review_at__lte=today)
            .select_related("deck")
            .order_by("next_review_at", "id")
        )

    def get(self, request, *args, **kwargs):
        due_cards = self.get_due_cards_qs()
        card = due_cards.first()
        form = ReviewQualityForm(initial={"card_id": card.id}) if card else None
        return self.render_to_response({"card": card, "form": form, "due_count": due_cards.count()})

    def post(self, request, *args, **kwargs):
        form = ReviewQualityForm(request.POST)
        if not form.is_valid():
            raise Http404("Invalid form data")

        card_id = form.cleaned_data["card_id"]
        quality = form.cleaned_data["quality"]

        card = get_object_or_404(Card, pk=card_id, deck__user=request.user)
        today = timezone.localdate()

        res = sm2_calculate(
            quality=quality,
            repetitions=card.repetitions,
            interval_days=card.interval_days,
            ease_factor=card.ease_factor,
            review_date=today,
        )

        card.repetitions = res.repetitions
        card.interval_days = res.interval_days
        card.ease_factor = res.ease_factor
        card.next_review_at = res.next_review_at
        card.save(update_fields=["repetitions", "interval_days", "ease_factor", "next_review_at"])

        Review.objects.create(
            user=request.user,
            card=card,
            quality=quality,
            repetitions=res.repetitions,
            interval_days=res.interval_days,
            ease_factor=res.ease_factor,
            next_review_at=res.next_review_at,
        )

        return redirect("review_today")


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = "study/analytics.html"

    def get(self, request, *args, **kwargs):
        today = timezone.localdate()
        since = today - timedelta(days=30)

        reviews_qs = Review.objects.filter(user=request.user, reviewed_at__date__gte=since)

        if not reviews_qs.exists():
            return self.render_to_response(
                {
                    "fig_count_html": None,
                    "fig_avg_html": None,
                    "hard_cards": [],
                    "since": since,
                    "today": today,
                    "no_data": True,
                }
            )

        daily = (
            reviews_qs.annotate(day=TruncDate("reviewed_at"))
            .values("day")
            .annotate(reviews_count=Count("id"), avg_quality=Avg("quality"))
            .order_by("day")
        )

        daily_days = [row["day"] for row in daily]
        daily_counts = [row["reviews_count"] for row in daily]
        daily_avgq = [float(row["avg_quality"]) if row["avg_quality"] is not None else 0.0 for row in daily]

        fig_count = px.bar(x=daily_days, y=daily_counts, labels={"x": "День", "y": "Повторений"}, title="Повторения по дням (30 дней)")
        fig_avg = px.line(x=daily_days, y=daily_avgq, markers=True, labels={"x": "День", "y": "Средняя оценка"}, title="Средняя оценка по дням (30 дней)")

        hard_cards = (
            Review.objects.filter(user=request.user)
            .values("card_id", "card__front_text", "card__deck__title")
            .annotate(avg_quality=Avg("quality"), reviews_count=Count("id"))
            .filter(reviews_count__gte=3)
            .order_by("avg_quality", "-reviews_count")[:10]
        )

        return self.render_to_response(
            {
                "fig_count_html": fig_count.to_html(full_html=False, include_plotlyjs="cdn"),
                "fig_avg_html": fig_avg.to_html(full_html=False, include_plotlyjs=False),
                "hard_cards": hard_cards,
                "since": since,
                "today": today,
                "no_data": False,
            }
        )



class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")
    
    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)