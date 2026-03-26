from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
    
#Category
class Category(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Create your models here.
class Post(models.Model):
    title=models.CharField(max_length=200)
    content=models.TextField()
    img_url=models.ImageField(blank=True, upload_to="post_images/")
    created_at=models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="posts")
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="posts",null=True)
    is_published=models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def formatted_img_url(self):
        url = self.img_url if self.img_url.__str__().startswith("http") else self.img_url.url
        return url

    def __str__(self):
        return self.title
    
class AboutUs(models.Model):
    content=models.TextField()
