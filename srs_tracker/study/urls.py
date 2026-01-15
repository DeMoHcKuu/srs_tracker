from django.urls import path

from .views import (
    HomeView,
    DeckListView, DeckCreateView, DeckUpdateView, DeckDeleteView,
    CardListView, CardCreateView, CardUpdateView, CardDeleteView,
    ReviewTodayView, AnalyticsView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),

    path("decks/", DeckListView.as_view(), name="deck_list"),
    path("decks/create/", DeckCreateView.as_view(), name="deck_create"),
    path("decks/<int:pk>/edit/", DeckUpdateView.as_view(), name="deck_edit"),
    path("decks/<int:pk>/delete/", DeckDeleteView.as_view(), name="deck_delete"),

    path("decks/<int:deck_id>/cards/", CardListView.as_view(), name="card_list"),
    path("decks/<int:deck_id>/cards/create/", CardCreateView.as_view(), name="card_create"),
    path("cards/<int:pk>/edit/", CardUpdateView.as_view(), name="card_edit"),
    path("cards/<int:pk>/delete/", CardDeleteView.as_view(), name="card_delete"),

    path("review/today/", ReviewTodayView.as_view(), name="review_today"),
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
]
