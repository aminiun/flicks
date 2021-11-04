from django.core.management.base import BaseCommand, CommandError

from apps.film.models import Film


class Command(BaseCommand):
    help = 'Downloading posters and banners of films'

    def handle(self, *args, **options):
        import pdb;pdb.set_trace()
        for film in Film.active_objects.filter(photo__isnull=True):
            film.save()

            self.stdout.write(self.style.SUCCESS('Successfully downloaded "%s"' % film.name))
