from django.db import models

# Create your models here.
class Platform(models.Model):
	name = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name

class ProductionType(models.Model):
	name = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name

class Production(models.Model):
	title = models.CharField(max_length=255)
	platforms = models.ManyToManyField('Platform', related_name = 'productions')
	types = models.ManyToManyField('ProductionType', related_name = 'productions')
	
	def __unicode__(self):
		return self.title