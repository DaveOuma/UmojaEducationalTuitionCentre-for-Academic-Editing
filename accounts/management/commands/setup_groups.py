from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


# Named groups referenced by the spec (section 17/26). Kept as a plain list
# here rather than hard-coded strings scattered through the codebase — as
# later phases add models (assignments, documents, payments), their
# permissions get attached to these same groups in setup scripts local to
# those apps.
DEFAULT_GROUPS = [
    "Editors",
    "Senior Editors",
    "Administrators",
]


class Command(BaseCommand):
    help = "Creates the default authorization groups. Safe to run repeatedly."

    def handle(self, *args, **options):
        for name in DEFAULT_GROUPS:
            group, created = Group.objects.get_or_create(name=name)
            status = "created" if created else "already exists"
            self.stdout.write(f"Group '{name}': {status}")