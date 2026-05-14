import os
import django
import random

import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from faker import Faker
from users.models import Author, Reader
from articles.models import Article
from tags.models import Tag
from comments.models import Comment

fake = Faker()

def run():
    print("Seeding database...")
    
    # Create tags
    tags = [Tag.objects.get_or_create(name=t)[0] for t in ['Technology', 'Django', 'Web Dev', 'AI', 'Innovation']]
    
    # Create Authors
    a1 = Author.objects.create_user(username=fake.user_name() + "_author", email=fake.email(), password='password', bio=fake.text(), role='Author')
    a2 = Author.objects.create_user(username=fake.user_name() + "_writer", email=fake.email(), password='password', bio=fake.text(), role='Author')
    authors = [a1, a2]
    print(f"Created Authors: {a1.username}, {a2.username}")
    
    # Create Readers
    r1 = Reader.objects.create_user(username=fake.user_name() + "_reader", email=fake.email(), password='password', bio=fake.text(), role='Reader')
    r2 = Reader.objects.create_user(username=fake.user_name() + "_fan", email=fake.email(), password='password', bio=fake.text(), role='Reader')
    readers = [r1, r2]
    print(f"Created Readers: {r1.username}, {r2.username}")
    
    # Create Articles
    for author in authors:
        for _ in range(2):
            content_paragraphs = fake.paragraphs(nb=5)
            content = "\n\n".join(content_paragraphs)
            
            article = Article.objects.create(
                author=author,
                title=fake.catch_phrase(),
                slug=fake.slug(),
                content=content,
                status='Publié'
            )
            article.tags.add(random.choice(tags))
            article.tags.add(random.choice(tags))
            
            # Create Comments by Readers
            Comment.objects.create(
                article=article,
                user=random.choice(readers),
                content=fake.sentence()
            )
            Comment.objects.create(
                article=article,
                user=random.choice(readers),
                content=fake.sentence()
            )
    print("Finished seeding DB with Faker!")

if __name__ == '__main__':
    run()
