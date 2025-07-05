# # accounts/context_processors.py

# from venv import logger
# from accounts.models import Corporate, Logo

# def logo_context(request):
#     logo = None
#     corporate = None

#     if request.user.is_authenticated:
#         logger.debug(f"User: {request.user}, Role: {request.user.role}")

#         if request.user.role in ['super_admin', 'employee']:
#             logo = Logo.objects.first()
#             logger.debug(f"Global logo fetched for {request.user.role}: {logo}")
        
#         elif request.user.role == 'corporate_admin':
#             try:
#                 corporate_id = request.user.corporate_id
#                 corporate = Corporate.objects.get(id=corporate_id)
#                 logger.debug(f"Corporate found: {corporate.project_name}, Logo: {corporate.logo}")
#             except Corporate.DoesNotExist:
#                 logger.warning(f"No corporate found for corporate_id: {corporate_id}")

#     return {
#         'logo': logo,
#         'corporate': corporate
#     }


# # from accounts.models import Corporate, Logo

# # def logo_context(request):
# #     if request.user.is_authenticated:
# #         if request.user.role == 'corporate_admin':
# #             try:
# #                 corporate = Corporate.objects.get(corporate_id=request.user.corporate_id)
# #                 return {'corporate_logo': corporate.logo}
# #             except Corporate.DoesNotExist:
# #                 return {'corporate_logo': None}
# #         elif request.user.role == 'super_admin':
# #             return {'super_logo': Logo.objects.first()}
# #     return {}


# accounts/context_processors.py
from accounts.models import Corporate, Logo


def logo_context(request):
    logo = None
    corporate = None

    if request.user.is_authenticated:
        if request.user.role in ['super_admin', 'employee']:
            logo = Logo.objects.first()
        elif request.user.role == 'corporate_admin':
            try:
                corporate_id = request.user.corporate_id
                corporate = Corporate.objects.get(id=corporate_id)
            except Corporate.DoesNotExist:
                pass

    return {
        'logo': logo,
        'corporate': corporate
    }
