from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Deck, Card

User = get_user_model()

@receiver(post_save, sender=User)
def create_demo_decks(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        # 3 демо-колоды
        decks_data = [
            {
                "title": "Английский язык",
                "description": "Базовая лексика и фразы",
                "cards": [
                    ("What is the capital of France?", "Paris"),
                    ("What is 2 + 2?", "4"),
                    ("What is the largest planet?", "Jupiter"),
                    ("What is H2O?", "Water"),
                    ("Who wrote Romeo and Juliet?", "Shakespeare"),
                    ("What is the capital of Japan?", "Tokyo"),
                    ("How many continents?", "7"),
                    ("What is the largest ocean?", "Pacific"),
                    ("How many bones in human body?", "206"),
                    ("What is the freezing point of water?", "0°C"),
                    ("Who painted Mona Lisa?", "Leonardo da Vinci"),
                    ("What is the currency of Japan?", "Yen"),
                    ("What year did WW2 end?", "1945"),
                    ("What is the smallest country?", "Vatican City"),
                    ("What is the speed of light?", "299,792,458 m/s"),
                ]
            },
            {
                "title": "История",
                "description": "Исторические события и даты",
                "cards": [
                    ("Когда началась Вторая мировая война?", "1939"),
                    ("Кто был первым президентом США?", "Джордж Вашингтон"),
                    ("В каком году была Французская революция?", "1789"),
                    ("Кто написал Декларацию независимости?", "Томас Джефферсон"),
                    ("Когда произошла Октябрьская революция?", "1917"),
                    ("Кто был Наполеон?", "Французский полководец и император"),
                    ("Когда пал Берлинский стена?", "1989"),
                    ("Когда был основан Рим?", "753 год до н.э."),
                    ("Кто был Юлий Цезарь?", "Римский полководец и политик"),
                    ("Когда началась Холодная война?", "1947"),
                    ("Кто был Авраам Линкольн?", "16-й президент США"),
                    ("Когда произошел взрыв на Чернобыле?", "1986"),
                    ("Кто открыл Америку?", "Христофор Колумб"),
                    ("Когда была Великая депрессия?", "1929"),
                    ("Кто был Владимир Ленин?", "Лидер Октябрьской революции"),
                ]
            },
            {
                "title": "Математика",
                "description": "Базовые математические понятия",
                "cards": [
                    ("Чему равно π?", "≈ 3.14159"),
                    ("Что такое квадратный корень из 16?", "4"),
                    ("Чему равно 2^8?", "256"),
                    ("Что такое производная?", "Скорость изменения функции"),
                    ("Чему равна сумма углов треугольника?", "180°"),
                    ("Что такое логарифм?", "Обратная функция к экспоненте"),
                    ("Чему равно 0.5 + 0.3?", "0.8"),
                    ("Что такое факториал 5?", "120"),
                    ("Чему равен косинус 0?", "1"),
                    ("Что такое пифагорейская тройка?", "3, 4, 5"),
                    ("Чему равна площадь круга?", "π * r²"),
                    ("Что такое бесконечность?", "Понятие без предела"),
                    ("Чему равно 10%?", "0.1 или 1/10"),
                    ("Что такое медиана?", "Средний элемент в упорядоченном списке"),
                    ("Чему равна вероятность?", "Число от 0 до 1"),
                ]
            },
        ]

        for deck_data in decks_data:
            deck = Deck.objects.create(
                user=instance,
                title=deck_data["title"],
                description=deck_data["description"]
            )
            
            for front, back in deck_data["cards"]:
                Card.objects.create(
                    deck=deck,
                    front_text=front,
                    back_text=back,
                    is_active=True
                )
