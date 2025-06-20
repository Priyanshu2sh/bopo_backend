# from django.shortcuts import render

# class Custom404Middleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)

#         if response.status_code == 404:
#             # Render your custom 404 page instead of default Django debug page
#             return render(request, "bopo_admin/Helpdesk/invalid.html", status=404)

#         return response


from django.shortcuts import render

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Show custom 404 only for URLs under /portal/
        if response.status_code == 404 and request.path.startswith('/biggbonuspoints.in/portal/'):
            return render(request, "bopo_admin/Helpdesk/invalid.html", status=404)

        return response
