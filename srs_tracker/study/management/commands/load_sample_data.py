from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from study.models import Deck, Card, Tag

User = get_user_model()

class Command(BaseCommand):
    help = "Load sample data for testing"

    def handle(self, *args, **options):
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR("No superuser found"))
            return

        deck, created = Deck.objects.get_or_create(
            user=user,
            title="Английский язык",
            defaults={"description": "Базовая лексика и фразы"}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created deck: {deck.title}"))
        else:
            self.stdout.write(f"Deck already exists: {deck.title}")

        cards_data = [
            ("What is the capital of France?", "Paris"),
            ("What is 2 + 2?", "4"),
            ("What is the largest planet in our solar system?", "Jupiter"),
            ("What is the chemical formula for water?", "H2O"),
            ("In what year did World War 2 end?", "1945"),
            ("What is the smallest country in the world?", "Vatican City"),
            ("How many continents are there?", "7"),
            ("What is the speed of light?", "299,792,458 meters per second"),
            ("Who wrote Romeo and Juliet?", "William Shakespeare"),
            ("What is the currency of Japan?", "Yen"),
            ("What is the largest ocean on Earth?", "Pacific Ocean"),
            ("How many bones are in the human body?", "206"),
            ("What is the freezing point of water?", "0°C (32°F)"),
            ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
            ("What is the capital of Japan?", "Tokyo"),
        ]

        created_count = 0
        for front, back in cards_data:
            card, created = Card.objects.get_or_create(
                deck=deck,
                front_text=front,
                defaults={
                    "back_text": back,
                    "is_active": True,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} cards for deck '{deck.title}'"))
