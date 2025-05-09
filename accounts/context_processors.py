# accounts/context_processors.py

# from .models import Logo

# def logo_context(request):
#     return {'logo': Logo.objects.first()}
# accounts/context_processors.py

from venv import logger
from accounts.models import Corporate, Logo


def logo_context(request):
    logo = None
    corporate = None
    if request.user.is_authenticated:
        logger.debug(f"User: {request.user}, Role: {request.user.role}")
        if request.user.role == 'super_admin':
            logo = Logo.objects.first()
        elif request.user.role == 'corporate_admin':
            try:
                # Ensure that user provides correct corporate_id format like 'CORP00021'
                corporate_id = request.user.corporate_id  # Directly using the full corporate_id
                corporate = Corporate.objects.get(id=corporate_id)
                logger.debug(f"Corporate found: {corporate.project_name}, Logo: {corporate.logo}")
            except Corporate.DoesNotExist:
                logger.warning(f"No corporate found for corporate_id: {request.user.corporate_id} - This could be a missing corporate entry in the database.")
    return {
        'logo': logo,
        'corporate': corporate
    }

# from accounts.models import Corporate, Logo

# def logo_context(request):
#     if request.user.is_authenticated:
#         if request.user.role == 'corporate_admin':
#             try:
#                 corporate = Corporate.objects.get(corporate_id=request.user.corporate_id)
#                 return {'corporate_logo': corporate.logo}
#             except Corporate.DoesNotExist:
#                 return {'corporate_logo': None}
#         elif request.user.role == 'super_admin':
#             return {'super_logo': Logo.objects.first()}
#     return {}
