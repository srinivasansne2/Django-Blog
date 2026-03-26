from typing import Any
from blog.models import Category
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "This commands inserts catagory data"

    def handle(self, *args: Any, **options: Any):
        # Delete existing data 
        Category.objects.all().delete()

        categories = [
            "Technology",
            "Health",
            "Travel",
            "Food",
            "Education",
            "Finance",
            "Lifestyle",
            "Entertainment",
            "Sports",
            "Science",
        ]
        for category in categories:
            Category.objects.create(name=category)
        
        self.stdout.write(self.style.SUCCESS("Completed inserting Data!"))