"""
Utility functions for User app
"""
from Admin.models import Member


def get_or_create_member(user, request=None):
    """
    Helper function to get or create a Member profile for a user.
    This handles cases where superusers or existing users don't have Member profiles.
    
    Args:
        user: Django User instance
        request: Optional request object to show messages
    
    Returns:
        Member instance
    """
    try:
        member = Member.objects.get(user=user)
        return member
    except Member.DoesNotExist:
        # Auto-create Member profile if it doesn't exist
        # Use user's information to populate Member fields
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        email = user.email or f"{user.username}@library.local"
        
        # Check if email already exists in Member
        if Member.objects.filter(email=email).exists():
            # If email exists, use a modified email
            email = f"{user.username}_{user.id}@library.local"
        
        member = Member.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            phone="Not provided",
            address=""
        )
        
        # Show message if request is provided
        if request:
            from django.contrib import messages
            messages.info(request, 'A member profile has been created for you. Please update your profile information.')
        
        return member

