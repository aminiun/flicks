from django.db import models

from core.models.query import (
    ActiveQuerySet,
)


class ActiveModelManager(models.Manager):
    """
    ActiveModelManager

    Manager to return instances of ActivatorModel: SomeModel.objects.active() / .inactive()
    """

    def get_queryset(self):
        """ Use ActiveQuerySet for all results """
        return ActiveQuerySet(model=self.model, using=self._db)

    def active(self):
        """
        Return active instances of BaseModel:

        SomeModel.objects.active(), proxy to ActiveQuerySet.active
        """
        return self.get_queryset().active()

    def inactive(self):
        """
        Return inactive instances of BaseModel:

        SomeModel.objects.inactive(), proxy to ActiveQuerySet.inactive
        """
        return self.get_queryset().inactive()
