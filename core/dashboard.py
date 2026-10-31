from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta


def dashboard_callback(request, context):
    """
    This function injects KPI cards and charts into the admin dashboard.
    Configured in settings.py as 'DASHBOARD_CALLBACK': 'core.dashboard.dashboard_callback'
    """
    from studio.models import Service, Project, TeamMember, ContactSubmission, JobApplication
    from crm.models import Company, Opportunity, CommunicationLog

    # Get statistics
    total_services = Service.objects.count()
    total_projects = Project.objects.count()
    total_team = TeamMember.objects.count()
    featured_projects = Project.objects.filter(is_featured=True).count()
    active_services = Service.objects.filter(is_featured=True).count()
    
    # Contact submissions stats
    unread_contacts = ContactSubmission.objects.filter(is_read=False).count()
    total_contacts = ContactSubmission.objects.count()
    
    # Job applications stats
    pending_jobs = JobApplication.objects.filter(is_reviewed=False).count()
    total_jobs = JobApplication.objects.count()

    # Chart data (last 7 days for contacts)
    last_7_days = timezone.now() - timedelta(days=7)
    recent_contacts = (
        ContactSubmission.objects.filter(created_at__gte=last_7_days)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    contact_chart_data = [
        [day_stat['day'].strftime("%d %b"), day_stat['count']]
        for day_stat in recent_contacts
    ]

    # Project status distribution
    project_status_data = []
    for status, label in Project.STATUS_CHOICES:
        count = Project.objects.filter(status=status).count()
        if count > 0:
            project_status_data.append([label, count])

    # ============================================================================
    # CRM STATISTICS
    # ============================================================================
    
    # Company stats
    total_companies = Company.objects.count()
    prospects_count = Company.objects.filter(status='prospect').count()
    contacted_count = Company.objects.filter(status='contacted').count()
    in_discussion_count = Company.objects.filter(status='in_discussion').count()
    clients_count = Company.objects.filter(status='client').count()
    
    # Opportunity stats
    total_opportunities = Opportunity.objects.count()
    active_opportunities = Opportunity.objects.filter(status__in=['lead', 'qualified', 'proposal', 'negotiation']).count()
    won_opportunities = Opportunity.objects.filter(status='won').count()
    total_pipeline_value = Opportunity.objects.filter(status__in=['lead', 'qualified', 'proposal', 'negotiation']).aggregate(
        total=Count('estimated_value')
    )['total'] or 0
    
    # Calculate total estimated value
    pipeline_value = Opportunity.objects.filter(
        status__in=['lead', 'qualified', 'proposal', 'negotiation']
    ).aggregate(
        total=Count('estimated_value')
    )['total'] or 0
    
    # Get actual sum of estimated values
    from django.db.models import Sum
    pipeline_value_sum = Opportunity.objects.filter(
        status__in=['lead', 'qualified', 'proposal', 'negotiation'],
        estimated_value__isnull=False
    ).aggregate(
        total=Sum('estimated_value')
    )['total'] or 0
    
    # Communication stats
    total_communications = CommunicationLog.objects.count()
    recent_communications = CommunicationLog.objects.filter(
        date__gte=last_7_days
    ).count()
    
    # Company status distribution chart
    company_status_data = [
        ['Prospects', prospects_count],
        ['Contacted', contacted_count],
        ['In Discussion', in_discussion_count],
        ['Clients', clients_count],
    ]
    
    # Opportunity status distribution chart
    opportunity_status_data = []
    for status, label in Opportunity.STATUS_CHOICES:
        count = Opportunity.objects.filter(status=status).count()
        if count > 0:
            opportunity_status_data.append([label, count])
    
    # Tech readiness distribution
    tech_readiness_data = []
    for i in range(1, 6):
        count = Company.objects.filter(tech_readiness=i).count()
        if count > 0:
            tech_readiness_data.append([f'Level {i}', count])
    
    # Recent communications chart (last 7 days)
    recent_comms_chart = (
        CommunicationLog.objects.filter(date__gte=last_7_days)
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    
    communications_chart_data = [
        [day_stat['day'].strftime("%d %b"), day_stat['count']]
        for day_stat in recent_comms_chart
    ]

    # Update context with KPI cards
    context.update({
        "kpi": [
            {
                "title": _("Total Companies"),
                "metric": total_companies,
                "chart": company_status_data,
                "footer": format_html(
                    '<strong class="text-green-600">{}</strong> Clients, <strong class="text-blue-600">{}</strong> Prospects',
                    clients_count,
                    prospects_count
                ),
            },
            {
                "title": _("Opportunities"),
                "metric": total_opportunities,
                "chart": opportunity_status_data,
                "footer": format_html(
                    '<strong class="text-green-600">{}</strong> Won, <strong class="text-blue-600">{}</strong> Active',
                    won_opportunities,
                    active_opportunities
                ),
            },
            {
                "title": _("Pipeline Value"),
                "metric": f"{pipeline_value_sum:,.0f}" if pipeline_value_sum else "0",
                "footer": format_html(
                    '<span class="text-gray-600">Estimated ETB in active pipeline</span>'
                ),
            },
            {
                "title": _("Communications"),
                "metric": total_communications,
                "chart": communications_chart_data,
                "footer": format_html(
                    '<strong class="text-purple-600">{}</strong> This Week',
                    recent_communications
                ),
            },
            {
                "title": _("Tech Readiness"),
                "chart": tech_readiness_data,
                "footer": format_html(
                    '<span class="text-gray-600">Distribution across companies</span>'
                ),
            },
            {
                "title": _("Total Services"),
                "metric": total_services,
                "footer": format_html(
                    '<strong class="text-blue-600">{}</strong> Featured Services',
                    active_services
                ),
            },
            {
                "title": _("Projects"),
                "metric": total_projects,
                "chart": project_status_data,
                "footer": format_html(
                    '<strong class="text-green-600">{}</strong> Featured Projects',
                    featured_projects
                ),
            },
            {
                "title": _("Team Members"),
                "metric": total_team,
                "footer": format_html(
                    '<span class="text-gray-600">Active contributors</span>'
                ),
            },
            {
                "title": _("Contact Submissions"),
                "metric": total_contacts,
                "chart": contact_chart_data,
                "footer": format_html(
                    '<strong class="text-amber-600">{}</strong> Unread Messages',
                    unread_contacts
                ),
            },
            {
                "title": _("Job Applications"),
                "metric": total_jobs,
                "footer": format_html(
                    '<strong class="text-purple-600">{}</strong> Pending Review',
                    pending_jobs
                ),
            },
        ]
    })

    return context
