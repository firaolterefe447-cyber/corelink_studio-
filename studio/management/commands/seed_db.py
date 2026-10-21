from django.core.management.base import BaseCommand
from studio.models import Service, Project, TeamMember, HeroSlide, StudioPage


class Command(BaseCommand):
    help = 'Seed the database with sample data for the studio home page'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')

        # Create Services
        services_data = [
            {
                'title': 'Web Platforms',
                'slug': 'web-platforms',
                'service_type': 'WEB',
                'description': 'Fast, secure web apps, portals and marketplaces built to grow with you.',
                'icon': 'globe',
                'features': ['React', 'Django', 'SaaS'],
                'is_featured': True,
                'order': 1
            },
            {
                'title': 'Mobile Apps',
                'slug': 'mobile-apps',
                'service_type': 'MOBILE',
                'description': 'iOS and Android apps that feel native and work offline.',
                'icon': 'smartphone',
                'features': ['Flutter', 'iOS', 'Android'],
                'is_featured': True,
                'order': 2
            },
            {
                'title': 'Custom Software',
                'slug': 'custom-software',
                'service_type': 'OTHER',
                'description': 'Systems shaped around your workflows, not the other way round.',
                'icon': 'code-2',
                'features': ['Tailored', 'Scalable'],
                'is_featured': True,
                'order': 3
            },
            {
                'title': 'ERP & Business Systems',
                'slug': 'erp-business-systems',
                'service_type': 'ERP',
                'description': 'Finance, HR, inventory and sales in one connected platform.',
                'icon': 'layers',
                'features': ['ERP', 'CRM', 'HRM'],
                'is_featured': True,
                'order': 4
            },
            {
                'title': 'UI/UX Design',
                'slug': 'ui-ux-design',
                'service_type': 'DESIGN',
                'description': 'Interfaces and design systems people enjoy using.',
                'icon': 'pen-tool',
                'features': ['Figma', 'Branding'],
                'is_featured': True,
                'order': 5
            },
            {
                'title': 'Integrations & APIs',
                'slug': 'integrations-apis',
                'service_type': 'CLOUD',
                'description': 'Payments, SMS, banking and government services that just work.',
                'icon': 'plug',
                'features': ['REST', 'Payments'],
                'is_featured': True,
                'order': 6
            }
        ]

        for service_data in services_data:
            Service.objects.get_or_create(
                slug=service_data['slug'],
                defaults=service_data
            )
        self.stdout.write(f'Created {len(services_data)} services')

        # Create Projects
        projects_data = [
            {
                'title': 'Selam ERP',
                'slug': 'selam-erp',
                'client_name': 'Selam Manufacturing',
                'short_description': 'A complete custom build covering design, engineering and launch support.',
                'full_description': 'Full ERP system for manufacturing company with inventory, HR, and finance modules.',
                'technologies': ['Django', 'React', 'PostgreSQL'],
                'status': 'COMPLETED',
                'is_featured': True,
                'order': 1
            },
            {
                'title': 'Hakim Care',
                'slug': 'hakim-care',
                'client_name': 'Hakim Health',
                'short_description': 'A complete custom build covering design, engineering and launch support.',
                'full_description': 'Healthcare management platform for clinics and hospitals.',
                'technologies': ['Flutter', 'Django', 'AWS'],
                'status': 'COMPLETED',
                'is_featured': True,
                'order': 2
            },
            {
                'title': 'Zemen Fleet',
                'slug': 'zemen-fleet',
                'client_name': 'Zemen Transport',
                'short_description': 'A complete custom build covering design, engineering and launch support.',
                'full_description': 'Fleet management system with GPS tracking and maintenance scheduling.',
                'technologies': ['React Native', 'Node.js', 'MongoDB'],
                'status': 'COMPLETED',
                'is_featured': True,
                'order': 3
            }
        ]

        for project_data in projects_data:
            Project.objects.get_or_create(
                slug=project_data['slug'],
                defaults=project_data
            )
        self.stdout.write(f'Created {len(projects_data)} projects')

        # Create Team Members
        team_data = [
            {
                'name': 'Elias T.',
                'slug': 'elias-t',
                'title': 'Lead Engineer',
                'order': 1
            },
            {
                'name': 'Niyat A.',
                'slug': 'niyat-a',
                'title': 'UI/UX Designer',
                'order': 2
            },
            {
                'name': 'Yared G.',
                'slug': 'yared-g',
                'title': 'Backend Expert',
                'order': 3
            },
            {
                'name': 'Samrawit K.',
                'slug': 'samrawit-k',
                'title': 'Mobile Developer',
                'order': 4
            }
        ]

        for member_data in team_data:
            TeamMember.objects.get_or_create(
                slug=member_data['slug'],
                defaults=member_data
            )
        self.stdout.write(f'Created {len(team_data)} team members')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
