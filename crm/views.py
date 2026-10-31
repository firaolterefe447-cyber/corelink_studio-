from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from .models import Company, Opportunity, CommunicationLog


@login_required
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


@login_required
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
    }
    
    return render(request, 'crm/company_list.html', context)


@login_required
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


@login_required
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


@login_required
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
