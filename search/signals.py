import operator

from django.contrib.postgres.search import SearchVector
from django.db import transaction
from django.db.models import Value
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from taggit.models import Tag


@receiver(post_save)
def on_save(sender, **kwargs):
	if not hasattr(sender, 'index_components'):
		return
	transaction.on_commit(make_updater(kwargs['instance']))


@receiver(m2m_changed)
def on_m2m_changed(sender, **kwargs):
	instance = kwargs['instance']
	model = kwargs['model']
	if model is Tag:
		transaction.on_commit(make_updater(instance))
	elif isinstance(instance, Tag):
		for obj in model.objects.filter(pk__in=kwargs['pk_set']):
			if hasattr(obj, 'index_components'):
				transaction.on_commit(make_updater(obj))


def make_updater(instance):
	components = instance.index_components()
	try:
		admin_components = instance.admin_index_components()
	except AttributeError:
		admin_components = None

	pk = instance.pk

	def on_commit():
		search_vectors = []
		for weight, text in components.items():
			search_vectors.append(
				SearchVector(Value(text), weight=weight)
			)
		if admin_components:
			admin_search_vectors = []
			for weight, text in admin_components.items():
				admin_search_vectors.append(
					SearchVector(Value(text), weight=weight)
				)
			instance.__class__.objects.filter(pk=pk).update(
				search_document=reduce(operator.add, search_vectors),
				admin_search_document=reduce(operator.add, admin_search_vectors),
			)
		else:
			instance.__class__.objects.filter(pk=pk).update(
				search_document=reduce(operator.add, search_vectors)
			)
	return on_commit
