from django.shortcuts import render
# from django.contrib.auth import authenticate 
# from django.shortcuts import redirect
from .models import BopoAdmin, Project, Merchant
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response 
from .serializers import ProjectSerializer, MerchantSerializer

# Create your views here.
from django.shortcuts import render

def home(request):
   return render(request, 'bopo_admin/home.html')

def about(request):
     return render(request, 'bopo_admin/about.html')

def merchant(request):
    return render(request, 'bopo_admin/Merchant/merchant.html')

def customer(request):
    return render(request, 'bopo_admin/customer.html')

def merchant_list(request):
    return render(request, "bopo_admin/Merchant/merchant_list.html")

def add_merchant(request):
    return render(request, "bopo_admin/Merchant/add_merchant.html")

def project_onboarding(request):
    return render(request, 'bopo_admin/project_onboarding.html')

def project_list(request):
    return render(request, 'bopo_admin/project_list.html')
 
 
 
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = BopoAdmin.objects.get(username=username)
        if user.password != password:
            error_message = "Incorrect password"
            return render(request, 'bopo_admin/login.html', {'error_message': error_message})
        
        return render(request, 'bopo_admin/login.html')
    # return redirect()
    else:
        return render(request, 'bopo_admin/login.html')

# add project
class ProjectCreate(APIView):
    # get API for project
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
    
    #post API for project 
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Project created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# add merchant
class MerchantAPI(APIView):
    # GET API to fetch all merchants
    def get(self, request):
        merchants = Merchant.objects.all()
        serializer = MerchantSerializer(merchants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST API to create a new merchant
    def post(self, request):
        serializer = MerchantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Merchant created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
