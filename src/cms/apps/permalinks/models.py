"""Models used by the permalinks service."""

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models


class PermalinkManager(models.Manager):
    
    """Manager for Permalink models."""
    
    def create_for_obj(self, obj):
        """Creates a permalink for the given object."""
        url = obj.get_absolute_url()
        content_type = ContentType.objects.get_for_model(obj)
        # Get the permalink.
        try:
            permalink = Permalink.objects.get(url=url)
        except Permalink.DoesNotExist:
            permalink = Permalink(url=url)
        # Save if it has changed.
        if permalink.object_id != unicode(obj.id) and permalink.content_type_id != content_type.id:
            permalink.object = obj
            permalink.save()


class Permalink(models.Model):
    
    """A permalink to a moved / deleted model."""
    
    objects = PermalinkManager()
    
    url = models.CharField(
        max_length = 255,
        unique = True,
    )
    
    content_type = models.ForeignKey(ContentType)
    
    object_id = models.TextField()
    
    object = GenericForeignKey()
    
    def __unicode__(self):
        """Returns a unicode representation."""
        return self.url