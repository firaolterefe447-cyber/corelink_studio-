# CRM Authentication System Setup Guide

This guide will help you set up the role-based authentication system for the Corelink CRM.

## Overview

The CRM now has two user roles:
- **Marketing Team**: Can view and add companies, contacts, communications, and opportunities. Cannot edit or delete existing data.
- **CRM Manager**: Full access to all CRM features including edit, delete, and user management.

## Setup Steps

### 1. Run the Setup Command

Run this Django management command to create the required groups and permissions:

```bash
python manage.py setup_crm_groups
```

This will create:
- `Marketing` group with view and add permissions
- `CRM Manager` group with full permissions (view, add, edit, delete)

### 2. Create a CRM Manager Account

You need at least one CRM Manager to manage the system. You can create one through:

**Option A: Using the User Management Interface (Recommended)**
1. Log in as a superuser via Django admin
2. Navigate to `/crm/users/`
3. Click "Add New User"
4. Create a user with "CRM Manager" role

**Option B: Using Django Shell**
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model

# Create a CRM Manager user
user = User.objects.create_user(
    username='manager',
    email='manager@corelink.com',
    password='your_secure_password'
)

# Add to CRM Manager group
crm_manager_group = Group.objects.get(name='CRM Manager')
user.groups.add(crm_manager_group)

print('CRM Manager created successfully!')
```

### 3. Create Marketing Team Accounts

After you have a CRM Manager, they can create marketing team accounts:

1. Log in as CRM Manager at `/crm/login/`
2. Navigate to "Users" in the navigation
3. Click "Add New User"
4. Create users with "Marketing Team" role

## Access URLs

- **CRM Login**: `/crm/login/`
- **CRM Dashboard**: `/crm/`
- **User Management**: `/crm/users/` (CRM Managers only)
- **Django Admin**: `/admin/` (Superusers only)

## Permission Matrix

| Feature | Marketing | CRM Manager | Superuser |
|---------|-----------|------------|-----------|
| View Companies | ✅ | ✅ | ✅ |
| Add Companies | ✅ | ✅ | ✅ |
| Edit Companies | ❌ | ✅ | ✅ |
| Delete Companies | ❌ | ✅ | ✅ |
| View Contacts | ✅ | ✅ | ✅ |
| Add Contacts | ✅ | ✅ | ✅ |
| Edit Contacts | ❌ | ✅ | ✅ |
| Delete Contacts | ❌ | ✅ | ✅ |
| View Communications | ✅ | ✅ | ✅ |
| Log Communications | ✅ | ✅ | ✅ |
| View Opportunities | ✅ | ✅ | ✅ |
| Add Opportunities | ✅ | ✅ | ✅ |
| Edit Opportunities | ❌ | ✅ | ✅ |
| Delete Opportunities | ❌ | ✅ | ✅ |
| User Management | ❌ | ✅ | ✅ |
| Django Admin | ❌ | ❌ | ✅ |

## Security Best Practices

1. **Never share admin passwords** - Each team member should have their own account
2. **Use strong passwords** - Enforce password complexity for all users
3. **Regular audits** - Review user access periodically
4. **Revoke access promptly** - Remove users who leave the company
5. **Activity logging** - All actions are logged in the ActivityLog model

## Troubleshooting

### Users can't log in
- Ensure the user is in either `Marketing` or `CRM Manager` group
- Check that the user account is active (`is_active=True`)
- Verify the password is correct

### Permission denied errors
- Check that the user has the correct group membership
- Run `python manage.py setup_crm_groups` to ensure permissions are set correctly
- Clear browser cache and try again

### Can't see User Management link
- Only CRM Managers and Superusers can access user management
- Ensure your user is in the `CRM Manager` group

## Customization

### Adding New Roles

To add a new role (e.g., "Sales Team"), edit `crm/permissions.py` and add a new decorator:

```python
def sales_team_required(view_func):
    @wraps(view_func)
    @crm_login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='Sales Team').exists():
            raise PermissionDenied("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
```

Then update the setup command to create the group and assign permissions.

### Modifying Permissions

Edit `crm/management/commands/setup_crm_groups.py` to adjust which permissions each group receives.

## Support

For issues or questions, refer to the Django documentation:
- [Django Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Django Permissions](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions)
