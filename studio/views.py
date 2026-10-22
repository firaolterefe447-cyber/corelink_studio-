from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Service, Project, Testimonial, TeamMember, StudioPage, HeroSlide, ContactSubmission


HOME_DEFAULT_TITLE = 'Building Digital Excellence'  # value seeded by get_or_create below

def studio_home(request):
    """Main studio landing page"""
    page_content, _ = StudioPage.objects.get_or_create(
        page_type='HOME',
        defaults={
            'hero_title': HOME_DEFAULT_TITLE,
            'hero_subtitle': 'We craft innovative software solutions that transform businesses and drive growth.',
            'hero_cta_text': 'Start Your Project',
            'hero_cta_link': '/studio/contact'
        }
    )

    services = list(Service.objects.filter(is_featured=True)[:6]) or list(Service.objects.all()[:6])
    projects = (list(Project.objects.filter(is_featured=True, status='COMPLETED')[:6])
                or list(Project.objects.filter(status='COMPLETED')[:6]))
    hero_slides = list(HeroSlide.objects.filter(is_active=True)[:6])
    team_members = list(TeamMember.objects.all()[:8])

    # Hero is "custom" only once an admin edits it away from the seeded default.
    hero_custom = (
        page_content.hero_title.strip() != HOME_DEFAULT_TITLE
        or page_content.hero_subtitle.strip() != 'We craft innovative software solutions that transform businesses and drive growth.'
        or page_content.hero_cta_text != 'Start Your Project'
        or page_content.hero_cta_link != '/contact'
    )

    studio_data = {
        'hero': {
            'custom': hero_custom,
            'title': page_content.hero_title,
            'subtitle': page_content.hero_subtitle,
            'cta_text': page_content.hero_cta_text,
            'cta_link': page_content.hero_cta_link,
        },
        'services': [{
            'i': s.icon or 'code', 't': s.title, 'd': s.description,
            'f': s.features, 'star': s.is_featured,
        } for s in services],
        'projects': [{
            't': p.title, 'c': p.client_name or 'Client', 'slug': p.slug,
            's': p.get_status_display(), 'desc': p.short_description,
            'tech': p.technologies,
            'img': p.get_thumbnail_url() or p.get_cover_url(),
            'year': str(p.completion_date.year) if p.completion_date else '',
        } for p in projects],
        'hero_slides': [{
            'img': s.get_image_url(),
            'alt': s.alt_text or s.title,
            'label': s.label
        } for s in hero_slides if s.image],
        'team': [{
            'n': t.name,
            'r': t.title,
            'img': t.get_photo_url(),
        } for t in team_members],
    }

    context = {
        'page': page_content,
        'services': services,
        'projects': projects,
        'studio_data': studio_data,
    }
    return render(request, 'studio/home.html', context)
def service_detail(request, slug):
    """Individual service detail page"""
    service = get_object_or_404(Service, slug=slug)
    related_services = Service.objects.exclude(id=service.id)[:4]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'studio/service_detail.html', context)


def project_detail(request, slug):
    """Individual project detail page"""
    project = get_object_or_404(Project, slug=slug)
    related_projects = Project.objects.exclude(id=project.id).filter(status='COMPLETED')[:4]
    project_testimonials = project.testimonials.all()
    gallery_images = project.gallery_images.all()
    
    context = {
        'project': project,
        'related_projects': related_projects,
        'testimonials': project_testimonials,
        'gallery_images': gallery_images,
    }
    return render(request, 'studio/project_detail.html', context)


def about(request):
    """About page"""
    page_content, _ = StudioPage.objects.get_or_create(
        page_type='ABOUT',
        defaults={
            'hero_title': 'About CoreLink Studio',
            'hero_subtitle': 'Passionate about building exceptional digital experiences.',
            'hero_cta_text': 'Contact Us',
            'hero_cta_link': '/studio/contact'
        }
    )
    
    team_members = TeamMember.objects.all()
    
    context = {
        'page': page_content,
        'team': team_members,
    }
    return render(request, 'studio/about.html', context)


def contact(request):
    """Contact page"""
    page_content, _ = StudioPage.objects.get_or_create(
        page_type='CONTACT',
        defaults={
            'hero_title': 'Get In Touch',
            'hero_subtitle': 'Let\'s discuss how we can help bring your vision to life.',
            'hero_cta_text': 'Send Message',
            'hero_cta_link': '#contact-form'
        }
    )
    
    context = {
        'page': page_content,
    }
    return render(request, 'studio/contact.html', context)


def services(request):
    """All services listing page"""
    services = Service.objects.all()
    
    context = {
        'services': services,
    }
    return render(request, 'studio/services.html', context)


def projects(request):
    """All projects listing page"""
    projects = Project.objects.filter(status='COMPLETED')
    
    context = {
        'projects': projects,
    }
    return render(request, 'studio/projects.html', context)


@require_POST
@csrf_exempt
def contact_submit(request):
    """Handle contact form submission via AJAX"""
    try:
        name = request.POST.get('n', '').strip()
        email = request.POST.get('e', '').strip()
        need = request.POST.get('t', '').strip()
        timeline = request.POST.get('w', '').strip()
        message = request.POST.get('m', '').strip()

        # Validation
        if not name or not email or not message:
            return JsonResponse({'success': False, 'error': 'Please fill in your name, email, and message.'}, status=400)

        if '@' not in email or '.' not in email:
            return JsonResponse({'success': False, 'error': 'Please provide a valid email address.'}, status=400)

        # Save submission
        ContactSubmission.objects.create(
            name=name,
            email=email,
            need=need,
            timeline=timeline,
            message=message
        )

        return JsonResponse({'success': True, 'message': 'Thank you! We will get back to you within 24 hours.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred. Please try again.'}, status=500)
