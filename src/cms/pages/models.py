"""Core models used by the CMS."""


from django import forms
from django.conf import settings
from django.db import models

from cms.pages import lookup
from cms.pages.optimizations import cached_getter, cached_setter
from cms.pages.serializers import serializer


class PublishedManager(models.Manager):
    
    """Manager that only returns published content."""
    
    def get_query_set(self):
        """Returns all content that is published."""
        queryset = super(PublishedManager, self).get_query_set()
        queryset = queryset.filter(is_online=True)
        queryset = queryset.filter(models.Q(publication_date=None) | models.Q(publication_date__lte=now))
        queryset = queryset.filter(models.Q(expiry_date=None) | models.Q(expiry_date__gt=now))
        return queryset


class PageBase(models.Model):
    
    """Base model for models used to generate a HTML page."""
    
    objects = models.Manager()
    
    published_objects = PublishedManager()
    
    # Base fields.
    
    title = models.CharField(max_length=1000)
    
    last_modified = models.DateTimeField(auto_now=True,
                                         help_text="The date and time of when this content was last modified.")
    
    # Publication fields.
    
    is_online = models.BooleanField("online",
                                    default=True)
    
    publication_date = models.DateTimeField(blank=True,
                                            null=True,
                                            help_text="The date that this page will appear on the website.  Leave this blank to immediately publish this page.")

    expiry_date = models.DateTimeField(blank=True,
                                       null=True,
                                       help_text="The date that this page will be removed from the website.  Leave this blank to never expire this page.")
    
    
    # SEO fields.
    
    browser_title = models.CharField(max_length=1024,
                                     blank=True,
                                     null=True,
                                     help_text="The heading to use in the user's web browser.  Leave blank to use the page title.  Search engines page particular attention to this attribute.")
    
    keywords = models.CharField(max_length=1024,
                                blank=True,
                                null=True,
                                help_text="A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.")

    description = models.TextField(blank=True,
                                   null=True,
                                   help_text="A brief description of the contents of this page. Leave blank to use to use the parent page description.")
    
    priority = models.FloatField(choices=settings.SEO_PRIORITIES,
                                 default=settings.SEO_DEFAULT_PRIORITY,
                                 blank=True,
                                 null=True,
                                 help_text="The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.")
    
    change_frequency = models.CharField(max_length=255,
                                        choices=settings.SEO_CHANGE_FREQUENCIES,
                                        default=settings.SEO_DEFAULT_CHANGE_FREQUENCY,
                                        blank=True,
                                        null=True,
                                        help_text="How frequently you expect this content to be updated.  Search engines use this as a hint when scanning your site for updates.")
    
    allow_indexing = models.BooleanField(default=True,
                                         help_text="Uncheck this box to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.")

    allow_archiving = models.BooleanField(default=True,
                                          help_text="Uncheck this box to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis.")

    follow_links = models.BooleanField(default=True,
                                       help_text="Uncheck this box to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.")
    
    # Base model methods.
    
    def __unicode__(self):
        """Returns the title of the content."""
        return self.title
    
    class Meta:
        abstract = True
        ordering = ("title",)
        verbose_name_plural = "content"
        

# Make a fast dict of content types.
PAGE_CONTENT_TYPES = dict([(slug, lookup.get_object(content_type))
                           for slug, content_type in settings.PAGE_CONTENT_TYPES])


def get_page_content_type(type):
    """Returns the names page content type."""
    return PAGE_CONTENT_TYPES[type]


class Page(PageBase):

    """A page within the site."""

    # Base fields.

    url_title = models.SlugField("URL title")

    # Hierarchy fields.

    parent = models.ForeignKey("self",
                               blank=True,
                               null=True)

    order = models.PositiveSmallIntegerField(unique=True,
                                             editable=False,
                                             blank=True,
                                             null=True)

    @cached_getter
    def get_children(self):
        """
        Returns all the children of this page, regardless of their publication
        state.
        """
        return Page.objects.filter(parent=self).order_by("order", "id")

    children = property(get_children,
                        doc="All the children of this page, regardless of their publication state.")

    @cached_getter
    def get_published_children(self):
        """Returns all the published children of this page."""
        return Page.published_objects.filter(parent=self).order_by("order", "id")

    published_children = property(get_published_children,
                                  doc="All the published children of this page.")

    # Navigation fields.

    short_title = models.CharField(max_length=100,
                                   blank=True,
                                   null=True,
                                   help_text="A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.")

    in_navigation = models.BooleanField("add to navigation",
                                        default=True,
                                        help_text="Uncheck this box to remove this content from the site navigation.")

    @cached_getter
    def get_navigation(self):
        """
        Returns all published children of this page in the site navigation.
        """
        return self.get_published_children().filter(in_navigation=True)

    navigation = property(get_navigation,
                          doc="All the published children of this page in the site navigation.")

    # Content fields.

    content_type = models.CharField(max_length=20,
                                    editable=False,
                                    help_text="The type of page content.")

    content_data = models.TextField(editable=False,
                                    help_text="The encoded data of this page.")

    @cached_getter
    def get_content(self):
        """Returns the content object associated with this page."""
        content_cls = get_page_content_type(self.content_type)
        if self.content_data:
            content_data = serializer.deserialize(self.content_data)
        else:
            content_data = {}
        content = content_cls(self.content_type, self, content_data)
        return content

    @cached_setter(get_content)
    def set_content(self, content):
        """Sets the content object for this page."""
        self.content_type = content.type
        self.content_data = serializer.serialize(content.content_data)

    content = property(get_content,
                       set_content,
                       doc="The content object associated with this page.")

    class Meta:
        unique_together = (("parent", "url_title",),)
