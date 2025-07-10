from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Create Student and Teacher groups with permissions'

    def handle(self, *args, **options):
        # Create Students group
        students_group, created = Group.objects.get_or_create(name='Students')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Students group'))
        
        # Create Teachers group  
        teachers_group, created = Group.objects.get_or_create(name='Teachers')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Teachers group'))
        
        # Add permissions for Teachers (will add specific permissions in later versions)
        # For now, teachers get admin access to questions and tests
        teacher_permissions = Permission.objects.filter(
            content_type__app_label__in=['questions', 'tests'],
            codename__in=['add_', 'change_', 'delete_', 'view_']
        )
        
        if teacher_permissions.exists():
            teachers_group.permissions.set(teacher_permissions)
            self.stdout.write(self.style.SUCCESS('Added permissions to Teachers group'))
        
        self.stdout.write(self.style.SUCCESS('Groups setup completed'))