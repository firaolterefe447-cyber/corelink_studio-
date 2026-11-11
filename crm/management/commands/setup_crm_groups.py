from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from crm.models import Company, ContactPerson, PhoneNumber, SocialLink, CommunicationLog, Opportunity, ActivityLog


class Command(BaseCommand):
    help = 'Create CRM user groups (Marketing and CRM Manager) with appropriate permissions'

    def handle(self, *args, **options):
        # Get or create groups
        marketing_group, created = Group.objects.get_or_create(name='Marketing')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Marketing group'))
        else:
            self.stdout.write(self.style.WARNING('Marketing group already exists'))

        crm_manager_group, created = Group.objects.get_or_create(name='CRM Manager')
        if created:
            self.stdout.write(self.style.SUCCESS('Created CRM Manager group'))
        else:
            self.stdout.write(self.style.WARNING('CRM Manager group already exists'))

        # Get content types for CRM models
        content_types = {
            'company': ContentType.objects.get_for_model(Company),
            'contact': ContentType.objects.get_for_model(ContactPerson),
            'phone': ContentType.objects.get_for_model(PhoneNumber),
            'social': ContentType.objects.get_for_model(SocialLink),
            'communication': ContentType.objects.get_for_model(CommunicationLog),
            'opportunity': ContentType.objects.get_for_model(Opportunity),
            'activity': ContentType.objects.get_for_model(ActivityLog),
        }

        # Marketing permissions: view and add only (no edit/delete)
        marketing_permissions = []
        for model_name, ct in content_types.items():
            view_perm = Permission.objects.filter(codename=f'view_{model_name}', content_type=ct).first()
            add_perm = Permission.objects.filter(codename=f'add_{model_name}', content_type=ct).first()
            if view_perm:
                marketing_permissions.append(view_perm)
            if add_perm:
                marketing_permissions.append(add_perm)

        marketing_group.permissions.set(marketing_permissions)
        self.stdout.write(self.style.SUCCESS(f'Configured Marketing permissions ({len(marketing_permissions)} permissions)'))

        # CRM Manager permissions: full access
        manager_permissions = []
        for model_name, ct in content_types.items():
            view_perm = Permission.objects.filter(codename=f'view_{model_name}', content_type=ct).first()
            add_perm = Permission.objects.filter(codename=f'add_{model_name}', content_type=ct).first()
            change_perm = Permission.objects.filter(codename=f'change_{model_name}', content_type=ct).first()
            delete_perm = Permission.objects.filter(codename=f'delete_{model_name}', content_type=ct).first()
            
            if view_perm:
                manager_permissions.append(view_perm)
            if add_perm:
                manager_permissions.append(add_perm)
            if change_perm:
                manager_permissions.append(change_perm)
            if delete_perm:
                manager_permissions.append(delete_perm)

        crm_manager_group.permissions.set(manager_permissions)
        self.stdout.write(self.style.SUCCESS(f'Configured CRM Manager permissions ({len(manager_permissions)} permissions)'))

        self.stdout.write(self.style.SUCCESS('\nCRM groups setup complete!'))
        self.stdout.write('\nTo add users to groups:')
        self.stdout.write('  python manage.py shell')
        self.stdout.write('  >>> from django.contrib.auth.models import User')
        self.stdout.write('  >>> user = User.objects.get(username="username")')
        self.stdout.write('  >>> user.groups.add(Group.objects.get(name="Marketing"))')
