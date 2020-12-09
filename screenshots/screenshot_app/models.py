from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.conf import settings
from django.db import models
today = datetime.now()
import time
# Create your models here.

class ImageUploader(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	image = models.ImageField(upload_to='images')
	activity = models.IntegerField(default=0)
	created_at = models.DateField(default=datetime.now)