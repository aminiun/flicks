from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.manager import ActiveModelManager


class BaseModel(models.Model):
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active status"),
        db_index=True,
        help_text=_(
            "Designates whether this item should be treated as active. "
            "Unselected this instead of deleting."
        ),
    )
    # A timestamp representing when this object was created.
    created_time = models.DateTimeField(
        verbose_name=_("Creation On"), auto_now_add=True, db_index=True
    )
    # A timestamp representing when this object was last updated.
    updated_time = models.DateTimeField(
        verbose_name=_("Modified On"), auto_now=True
    )

    active_objects = ActiveModelManager()
    objects = active_objects

    class Meta:
        abstract = True
        ordering = ["-created_time", "-updated_time"]

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()
