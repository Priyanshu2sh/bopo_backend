from django.shortcuts import render

def modify_customer_details(request):
    return render(request, 'bopo_customer/Customer/modify_customer_details.html')

def send_customer_notifications(request):
    return render(request, 'bopo_admin/Customer/send_customer_notifications.html')

def customer_uploads(request):
    return render(request, 'bopo_admin/Customer/customer_uploads.html')
