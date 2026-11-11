from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from .models import Company, Opportunity, CommunicationLog, ContactPerson, PhoneNumber, SocialLink, ActivityLog
from .permissions import crm_login_required, marketing_or_manager_required, crm_manager_required

# Ethiopian regions
ETHIOPIAN_REGIONS = [
    ('Addis Ababa', 'Addis Ababa'),
    ('Afar', 'Afar'),
    ('Amhara', 'Amhara'),
    ('Benishangul-Gumuz', 'Benishangul-Gumuz'),
    ('Central Ethiopia', 'Central Ethiopia'),
    ('Dire Dawa', 'Dire Dawa'),
    ('Gambela', 'Gambela'),
    ('Harari', 'Harari'),
    ('Oromia', 'Oromia'),
    ('Sidama', 'Sidama'),
    ('Somali', 'Somali'),
    ('South Ethiopia', 'South Ethiopia'),
    ('South West Ethiopia', 'South West Ethiopia'),
    ('Tigray', 'Tigray'),
]


def crm_login(request):
    """Custom CRM login page."""
    if request.user.is_authenticated:
        return redirect('crm:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is active
            if not user.is_active:
                return render(request, 'crm/login.html', {
                    'error': 'This account is inactive. Please contact an administrator.'
                })
            
            # Check if user has CRM access
            user_groups = [g.name for g in user.groups.all()]
            has_crm_access = user.groups.filter(name__in=['Marketing', 'CRM Manager']).exists() or user.is_superuser
            
            if has_crm_access:
                login(request, user)
                next_url = request.GET.get('next', 'crm:dashboard')
                return redirect(next_url)
            else:
                return render(request, 'crm/login.html', {
                    'error': f'You do not have permission to access the CRM system. Your groups: {user_groups or "None"}'
                })
        else:
            return render(request, 'crm/login.html', {
                'error': 'Invalid username or password.'
            })
    
    return render(request, 'crm/login.html')


def crm_logout(request):
    """Custom CRM logout."""
    logout(request)
    return redirect('crm:login')


@marketing_or_manager_required
def crm_dashboard(request):
    """Main CRM dashboard view."""
    
    # Statistics
    total_companies = Company.objects.count()
    prospects = Company.objects.filter(status='prospect').count()
    contacted = Company.objects.filter(status='contacted').count()
    in_discussion = Company.objects.filter(status='in_discussion').count()
    clients = Company.objects.filter(status='client').count()
    
    # Opportunity stats
    total_opportunities = Opportunity.objects.count()
    active_opportunities = Opportunity.objects.filter(
        status__in=['lead', 'qualified', 'proposal', 'negotiation']
    ).count()
    won_opportunities = Opportunity.objects.filter(status='won').count()
    
    # Pipeline value
    pipeline_value = Opportunity.objects.filter(
        status__in=['lead', 'qualified', 'proposal', 'negotiation'],
        estimated_value__isnull=False
    ).aggregate(total=Sum('estimated_value'))['total'] or 0
    
    # Recent companies
    recent_companies = Company.objects.order_by('-created_at')[:10]
    
    # Recent communications
    recent_communications = CommunicationLog.objects.select_related(
        'company', 'contact_person'
    ).order_by('-date')[:10]
    
    # Upcoming follow-ups
    upcoming_followups = CommunicationLog.objects.filter(
        next_action_date__isnull=False
    ).order_by('next_action_date')[:10]
    
    context = {
        'total_companies': total_companies,
        'prospects': prospects,
        'contacted': contacted,
        'in_discussion': in_discussion,
        'clients': clients,
        'total_opportunities': total_opportunities,
        'active_opportunities': active_opportunities,
        'won_opportunities': won_opportunities,
        'pipeline_value': pipeline_value,
        'recent_companies': recent_companies,
        'recent_communications': recent_communications,
        'upcoming_followups': upcoming_followups,
    }
    
    return render(request, 'crm/dashboard.html', context)


@marketing_or_manager_required
def company_list(request):
    """List all companies with filters."""
    
    companies = Company.objects.all()
    
    # Filters
    status_filter = request.GET.get('status')
    industry_filter = request.GET.get('industry')
    region_filter = request.GET.get('region')
    tech_readiness_filter = request.GET.get('tech_readiness')
    search_query = request.GET.get('search')
    
    if status_filter:
        companies = companies.filter(status=status_filter)
    if industry_filter:
        companies = companies.filter(industry=industry_filter)
    if region_filter:
        companies = companies.filter(region=region_filter)
    if tech_readiness_filter:
        companies = companies.filter(tech_readiness=tech_readiness_filter)
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    companies = companies.select_related().prefetch_related(
        'contacts', 'phonenumbers', 'sociallinks'
    ).order_by('-created_at')
    
    context = {
        'companies': companies,
        'status_filter': status_filter,
        'industry_filter': industry_filter,
        'region_filter': region_filter,
        'tech_readiness_filter': tech_readiness_filter,
        'search_query': search_query,
        'industry_choices': Company.INDUSTRY_CHOICES,
        'ethiopian_regions': ETHIOPIAN_REGIONS,
    }
    
    return render(request, 'crm/company_list.html', context)


@marketing_or_manager_required
def company_detail(request, company_id):
    """Detail view for a single company."""
    
    company = get_object_or_404(
        Company.objects.prefetch_related(
            'contacts', 'phonenumbers', 'sociallinks', 
            'communications', 'opportunities'
        ),
        id=company_id
    )
    
    context = {
        'company': company,
    }
    
    return render(request, 'crm/company_detail.html', context)


@marketing_or_manager_required
def opportunity_pipeline(request):
    """Pipeline view for opportunities."""
    
    opportunities = Opportunity.objects.select_related('company').all()
    
    # Group by status
    pipeline = {
        'lead': opportunities.filter(status='lead'),
        'qualified': opportunities.filter(status='qualified'),
        'proposal': opportunities.filter(status='proposal'),
        'negotiation': opportunities.filter(status='negotiation'),
        'won': opportunities.filter(status='won'),
        'lost': opportunities.filter(status='lost'),
        'on_hold': opportunities.filter(status='on_hold'),
    }
    
    context = {
        'pipeline': pipeline,
    }
    
    return render(request, 'crm/pipeline.html', context)


@marketing_or_manager_required
def communication_timeline(request):
    """Timeline view of all communications."""

    communications = CommunicationLog.objects.select_related(
        'company', 'contact_person'
    ).order_by('-date')

    # Filters
    company_filter = request.GET.get('company')
    method_filter = request.GET.get('method')
    outcome_filter = request.GET.get('outcome')

    if company_filter:
        communications = communications.filter(company_id=company_filter)
    if method_filter:
        communications = communications.filter(method=method_filter)
    if outcome_filter:
        communications = communications.filter(outcome=outcome_filter)

    context = {
        'communications': communications,
        'company_filter': company_filter,
        'method_filter': method_filter,
        'outcome_filter': outcome_filter,
    }

    return render(request, 'crm/communications.html', context)


def log_activity(user, action, company, description, metadata=None):
    """Helper function to log activities."""
    ActivityLog.objects.create(
        user=user,
        action=action,
        company=company,
        description=description,
        metadata=metadata or {}
    )


@marketing_or_manager_required
def company_add(request):
    """Add a new company with all related data."""
    if request.method == 'POST':
        name = request.POST.get('name')

        # Build company data dict, only including non-empty values
        company_data = {
            'name': name,
            'status': request.POST.get('status', 'prospect'),
            'needs_website': request.POST.get('needs_website') == 'on',
            'needs_erp': request.POST.get('needs_erp') == 'on',
            'needs_upgrade': request.POST.get('needs_upgrade') == 'on',
            'needs_custom_system': request.POST.get('needs_custom_system') == 'on',
        }

        # Add optional fields only if they have values
        if request.POST.get('industry'):
            company_data['industry'] = request.POST.get('industry')
        if request.POST.get('business_type'):
            company_data['business_type'] = request.POST.get('business_type')
        if request.POST.get('description'):
            company_data['description'] = request.POST.get('description')
        if request.POST.get('address'):
            company_data['address'] = request.POST.get('address')
        if request.POST.get('city'):
            company_data['city'] = request.POST.get('city')
        if request.POST.get('region'):
            company_data['region'] = request.POST.get('region')
        if request.POST.get('tech_readiness'):
            company_data['tech_readiness'] = request.POST.get('tech_readiness')
        if request.POST.get('last_contacted'):
            company_data['last_contacted'] = request.POST.get('last_contacted')
        if request.POST.get('other_needs'):
            company_data['other_needs'] = request.POST.get('other_needs')
        if request.POST.get('notes'):
            company_data['notes'] = request.POST.get('notes')
        if request.POST.get('source'):
            company_data['source'] = request.POST.get('source')

        company = Company.objects.create(**company_data)

        # Log company creation
        log_activity(
            user=request.user,
            action='company_created',
            company=company,
            description=f'Created company: {name}'
        )

        # Handle contacts
        for key in request.POST:
            if key.startswith('contact_name_'):
                index = key.split('_')[-1]
                contact_name = request.POST.get(f'contact_name_{index}')
                if contact_name:
                    contact = ContactPerson.objects.create(
                        company=company,
                        name=contact_name,
                        role=request.POST.get(f'contact_role_{index}'),
                        telegram_handle=request.POST.get(f'contact_telegram_{index}'),
                        phone=request.POST.get(f'contact_phone_{index}'),
                        is_primary=request.POST.get(f'contact_primary_{index}') == 'on',
                    )
                    log_activity(
                        user=request.user,
                        action='contact_created',
                        company=company,
                        description=f'Added contact: {contact.name}'
                    )

        # Handle phone numbers
        for key in request.POST:
            if key.startswith('phone_number_'):
                index = key.split('_')[-1]
                phone_number = request.POST.get(f'phone_number_{index}')
                if phone_number:
                    phone = PhoneNumber.objects.create(
                        company=company,
                        number=phone_number,
                        phone_type=request.POST.get(f'phone_type_{index}', 'mobile'),
                        is_primary=request.POST.get(f'phone_primary_{index}') == 'on',
                        is_verified=request.POST.get(f'phone_verified_{index}') == 'on',
                    )
                    log_activity(
                        user=request.user,
                        action='phone_created',
                        company=company,
                        description=f'Added phone number: {phone.number}'
                    )

        # Handle social links
        for key in request.POST:
            if key.startswith('social_platform_'):
                index = key.split('_')[-1]
                platform = request.POST.get(f'social_platform_{index}')
                url = request.POST.get(f'social_url_{index}')
                if platform and url:
                    link = SocialLink.objects.create(
                        company=company,
                        platform=platform,
                        url=url,
                        is_primary=request.POST.get(f'social_primary_{index}') == 'on',
                    )
                    log_activity(
                        user=request.user,
                        action='social_created',
                        company=company,
                        description=f'Added social link: {link.get_platform_display()}'
                    )

        # Handle initial communication
        comm_method = request.POST.get('comm_method')
        if comm_method:
            comm_data = {
                'company': company,
                'method': comm_method,
                'outcome': request.POST.get('comm_outcome'),
                'duration_minutes': request.POST.get('comm_duration'),
                'notes': request.POST.get('comm_notes'),
                'next_action': request.POST.get('comm_next_action'),
                'next_action_date': request.POST.get('comm_next_action_date'),
            }
            # Only add date if it's provided
            comm_date = request.POST.get('comm_date')
            if comm_date:
                comm_data['date'] = comm_date

            comm = CommunicationLog.objects.create(**comm_data)
            log_activity(
                user=request.user,
                action='communication_logged',
                company=company,
                description=f'Logged {comm.get_method_display()} communication'
            )

        # Handle initial opportunity
        opp_title = request.POST.get('opp_title')
        if opp_title:
            opp = Opportunity.objects.create(
                company=company,
                title=opp_title,
                opportunity_type=request.POST.get('opp_type'),
                estimated_value=request.POST.get('opp_value'),
                probability=request.POST.get('opp_probability'),
                description=request.POST.get('opp_description'),
                status='lead',
            )
            log_activity(
                user=request.user,
                action='opportunity_created',
                company=company,
                description=f'Created opportunity: {opp.title}'
            )

        return redirect('crm:company_detail', company_id=company.id)

    return render(request, 'crm/company_add.html', {
        'ethiopian_regions': ETHIOPIAN_REGIONS,
    })


@crm_manager_required
def company_edit(request, company_id):
    """Edit an existing company."""
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        # Build company data dict, only including non-empty values
        company_data = {
            'name': request.POST.get('name'),
            'status': request.POST.get('status', 'prospect'),
            'needs_website': request.POST.get('needs_website') == 'on',
            'needs_erp': request.POST.get('needs_erp') == 'on',
            'needs_upgrade': request.POST.get('needs_upgrade') == 'on',
            'needs_custom_system': request.POST.get('needs_custom_system') == 'on',
        }

        # Add optional fields only if they have values
        if request.POST.get('industry'):
            company_data['industry'] = request.POST.get('industry')
        else:
            company_data['industry'] = None
        if request.POST.get('business_type'):
            company_data['business_type'] = request.POST.get('business_type')
        else:
            company_data['business_type'] = None
        if request.POST.get('description'):
            company_data['description'] = request.POST.get('description')
        else:
            company_data['description'] = None
        if request.POST.get('address'):
            company_data['address'] = request.POST.get('address')
        else:
            company_data['address'] = None
        if request.POST.get('city'):
            company_data['city'] = request.POST.get('city')
        else:
            company_data['city'] = None
        if request.POST.get('region'):
            company_data['region'] = request.POST.get('region')
        else:
            company_data['region'] = None
        if request.POST.get('tech_readiness'):
            company_data['tech_readiness'] = request.POST.get('tech_readiness')
        else:
            company_data['tech_readiness'] = None
        if request.POST.get('last_contacted'):
            company_data['last_contacted'] = request.POST.get('last_contacted')
        else:
            company_data['last_contacted'] = None
        if request.POST.get('other_needs'):
            company_data['other_needs'] = request.POST.get('other_needs')
        else:
            company_data['other_needs'] = None
        if request.POST.get('notes'):
            company_data['notes'] = request.POST.get('notes')
        else:
            company_data['notes'] = None
        if request.POST.get('source'):
            company_data['source'] = request.POST.get('source')
        else:
            company_data['source'] = None

        for key, value in company_data.items():
            setattr(company, key, value)
        company.save()

        log_activity(
            user=request.user,
            action='company_updated',
            company=company,
            description=f'Updated company: {company.name}'
        )

        return redirect('crm:company_detail', company_id=company.id)

    return render(request, 'crm/company_edit.html', {
        'company': company,
        'ethiopian_regions': ETHIOPIAN_REGIONS,
    })


@marketing_or_manager_required
def contact_add(request, company_id):
    """Add a new contact person."""
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        contact = ContactPerson.objects.create(
            company=company,
            name=request.POST.get('name'),
            role=request.POST.get('role'),
            telegram_handle=request.POST.get('telegram_handle'),
            phone=request.POST.get('phone'),
            is_primary=request.POST.get('is_primary') == 'on',
            notes=request.POST.get('notes'),
        )
        log_activity(
            user=request.user,
            action='contact_created',
            company=company,
            description=f'Added contact: {contact.name or "Unnamed"}'
        )
        return redirect('crm:company_detail', company_id=company.id)

    return render(request, 'crm/contact_add.html', {'company': company})


@marketing_or_manager_required
def contact_detail(request, contact_id):
    """View contact person details."""
    contact = get_object_or_404(ContactPerson, id=contact_id)

    return render(request, 'crm/contact_detail.html', {
        'contact': contact,
    })


@marketing_or_manager_required
def phone_add(request, company_id):
    """Add a new phone number."""
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        phone = PhoneNumber.objects.create(
            company=company,
            number=request.POST.get('number'),
            phone_type=request.POST.get('phone_type', 'mobile'),
            is_primary=request.POST.get('is_primary') == 'on',
            is_verified=request.POST.get('is_verified') == 'on',
            notes=request.POST.get('notes'),
        )
        log_activity(
            user=request.user,
            action='phone_created',
            company=company,
            description=f'Added phone number: {phone.number}'
        )
        return redirect('crm:company_detail', company_id=company.id)

    return render(request, 'crm/phone_add.html', {'company': company})


@marketing_or_manager_required
def social_add(request, company_id):
    """Add a new social link."""
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        link = SocialLink.objects.create(
            company=company,
            platform=request.POST.get('platform'),
            url=request.POST.get('url'),
            is_primary=request.POST.get('is_primary') == 'on',
            notes=request.POST.get('notes'),
        )
        log_activity(
            user=request.user,
            action='social_created',
            company=company,
            description=f'Added social link: {link.get_platform_display()}'
        )
        return redirect('crm:company_detail', company_id=company.id)

    return render(request, 'crm/social_add.html', {'company': company})


@marketing_or_manager_required
def communication_add(request, company_id):
    """Log a new communication."""
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        contact_person = None
        if request.POST.get('contact_person'):
            contact_person = get_object_or_404(ContactPerson, id=request.POST.get('contact_person'))

        comm = CommunicationLog.objects.create(
            company=company,
            contact_person=contact_person,
            date=request.POST.get('date'),
            method=request.POST.get('method'),
            outcome=request.POST.get('outcome'),
            duration_minutes=request.POST.get('duration_minutes'),
            notes=request.POST.get('notes'),
            next_action=request.POST.get('next_action'),
            next_action_date=request.POST.get('next_action_date'),
        )
        log_activity(
            user=request.user,
            action='communication_logged',
            company=company,
            description=f'Logged {comm.get_method_display()} communication'
        )
        return redirect('crm:company_detail', company_id=company.id)

    return render(request, 'crm/communication_add.html', {'company': company})


@marketing_or_manager_required
def opportunity_add(request, company_id):
    """Add a new opportunity."""
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        opp = Opportunity.objects.create(
            company=company,
            title=request.POST.get('title'),
            opportunity_type=request.POST.get('opportunity_type'),
            status=request.POST.get('status', 'lead'),
            estimated_value=request.POST.get('estimated_value'),
            actual_value=request.POST.get('actual_value'),
            probability=request.POST.get('probability'),
            expected_close_date=request.POST.get('expected_close_date'),
            actual_close_date=request.POST.get('actual_close_date'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            notes=request.POST.get('notes'),
            loss_reason=request.POST.get('loss_reason'),
        )
        log_activity(
            user=request.user,
            action='opportunity_created',
            company=company,
            description=f'Created opportunity: {opp.title}'
        )
        return redirect('crm:company_detail', company_id=company.id)

    return render(request, 'crm/opportunity_add.html', {'company': company})


@marketing_or_manager_required
def activity_timeline(request, company_id):
    """View activity timeline for a company."""
    company = get_object_or_404(
        Company.objects.prefetch_related('activities'),
        id=company_id
    )

    activities = company.activities.all().order_by('-created_at')

    context = {
        'company': company,
        'activities': activities,
    }

    return render(request, 'crm/activity_timeline.html', context)


@crm_manager_required
def user_management(request):
    """User management page for CRM managers."""
    users = User.objects.all().prefetch_related('groups').order_by('username')
    
    marketing_group = Group.objects.get(name='Marketing')
    crm_manager_group = Group.objects.get(name='CRM Manager')
    
    context = {
        'users': users,
        'marketing_group': marketing_group,
        'crm_manager_group': crm_manager_group,
    }
    
    return render(request, 'crm/user_management.html', context)


@crm_manager_required
def user_add(request):
    """Add a new CRM user."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')  # 'marketing' or 'manager'
        
        if User.objects.filter(username=username).exists():
            return render(request, 'crm/user_add.html', {
                'error': 'Username already exists'
            })
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Add to appropriate group
        if role == 'marketing':
            user.groups.add(Group.objects.get(name='Marketing'))
        elif role == 'manager':
            user.groups.add(Group.objects.get(name='CRM Manager'))
        
        return redirect('crm:user_management')
    
    return render(request, 'crm/user_add.html')
