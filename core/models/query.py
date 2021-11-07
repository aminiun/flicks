from django.db import models


class ActiveQuerySet(models.QuerySet):
    """
    ActivatorQuerySet

    Query set that returns status results
    """

    def active(self):
        """ Return active query set """
        return self.filter(is_active=True)

    def inactive(self):
        """ Return inactive query set """
        return self.filter(is_active=False)
