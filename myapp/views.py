from django.shortcuts import render,redirect

# Create your views here.

from django.views.generic import View

from myapp.forms import CategoryFrom,TransactionForm,TransactionFilterForm,RegistrationForm,LoginForm

from myapp.models import Category,Transactions

from django.utils import timezone

from django.db.models import Sum

from django.contrib.auth import authenticate,login,logout

from django.contrib import messages

from myapp.decorators import signin_requierd

from django.utils.decorators import method_decorator



class CatogeryCreateView(View):

    def get(self,request,*args,**kwargs):

        if not request.user.is_authenticated:  #here without using decorectors

            messages.error(request,"invalid session please login")

            return redirect("signin")

        form_instance=CategoryFrom(user=request.user)

        qs=Category.objects.filter(owner=request.user)

        return render (request,"category_add.html",{"form":form_instance,"categories":qs})
    
    def post(self,request,*args,**kwargs):

        if not request.user.is_authenticated:

            messages.error(request,"invalid session please login")

            return redirect("signin")


        form_instance=CategoryFrom(request.POST,user=request.user,files=request.FILES)
        

        if form_instance.is_valid():

            form_instance.instance.owner=request.user

            cat_name=form_instance.cleaned_data.get("name")

            user_object=request.user

            is_exist=Category.objects.filter(name__iexact=cat_name,owner=user_object).exists()

            if is_exist:

                print("Already exist")

                return render (request,"category_add.html",{"form":form_instance,"message":"Category already exist"})
                
            else:


              form_instance.save()

            # data=form_instance.cleaned_data

            # Category.objects.create(**data)

              return redirect("catogery-add")
        else:

             return render (request,"category_add.html",{"form":form_instance})
        
@method_decorator(signin_requierd,name="dispatch")  #here using decoretors   
class CatergoryUpdateView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        category_object=Category.objects.get(id=id)

        form_instance=CategoryFrom(instance=category_object,user=request.user)

        return render(request,"category_edit.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        cat_obj=Category.objects.get(id=id)

        form_instance=CategoryFrom(request.POST,instance=cat_obj,user=request.user)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("catogery-add")
        
        else:

            return render(request,"category_edit.html",{"form":form_instance})
        

@method_decorator(signin_requierd,name="dispatch")
class TransactionCreateView(View):

    def get(self,request,*args,**kwargs):

        form_instance=TransactionForm()

        curn_month=timezone.now().month

        curn_year=timezone.now().year

        categories=Category.objects.filter(owner=request.user)

        qs=Transactions.objects.filter(created_date__month=curn_month,created_date__year=curn_year,owner=request.user)

        return render(request,"transaction_add.html",{"form":form_instance,"transactions":qs,"categories":categories})
    
    def post(self,request,*args,**kwargs):

        form_instance=TransactionForm(request.POST)

        if form_instance.is_valid():

            form_instance.instance.owner=request.user

            form_instance.save()

            return redirect("transaction-add")
        
        else:

            return render(request,"transaction_add.html",{"form":form_instance})
        
@method_decorator(signin_requierd,name="dispatch")
class TransactionUpdateView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        trans_obj=Transactions.objects.get(id=id)

        form_instance=TransactionForm(instance=trans_obj)

        return render(request,"transactin_edit.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        trans_obj=Transactions.objects.get(id=id)

        form_instance=TransactionForm(request.POST,instance=trans_obj)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("transaction-add")
        
        else:

             return render(request,"transactin_edit.html",{"form":form_instance})

@method_decorator(signin_requierd,name="dispatch")
class TransactionDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        Transactions.objects.get(id=id).delete()

        return redirect("transaction-add")
    
@method_decorator(signin_requierd,name="dispatch")
class ExpenseSummeryView(View):

    def get(self,request,*args,**kwargs):

        curn_month=timezone.now().month

        curn_year=timezone.now().year

        qs=Transactions.objects.filter(
            created_date__month=curn_month,

            created_date__year=curn_year,owner=request.user
        )

        total_expense=qs.values("amount").aggregate(total=Sum("amount")) #{"total":123457}

        category_summary=qs.values("category_object__name").annotate(total=Sum("amount"))

        payment_summary=qs.values("payment_method").annotate(total=Sum("amount"))

        print(payment_summary)

        data={

            "total_expense":total_expense.get("total"),
            "category_summary":category_summary,
            "payment_summary":payment_summary
        }

        return render(request,"expense_summary.html",data)
    
@method_decorator(signin_requierd,name="dispatch")
class TransactionSummaryView(View):

    def get(self,request,*args,**kwargs):

      curn_month=timezone.now().month

      curn_year=timezone.now().year

      form_instance=TransactionFilterForm()

      if "start_date" in request.GET and "end_date" in request.GET:
          
          st_date=request.GET.get("start_date")

          end_date=request.GET.get("end_date")

          qs=Transactions.objects.filter(
                                        
                                        created_date__range=(st_date,end_date)

                                         )
                                         
          
      else:
             curn_month=timezone.now().month
             curn_year=timezone.now().year
             qs=Transactions.objects.filter(
              created_date__month=curn_month,
              created_date__year=curn_year
              )
      total_expense=qs.values("amount").aggregate(total=Sum("amount")) 


      return render(request,"transaction_summary.html",{"transaction":qs,"form":form_instance,"total_expense":total_expense})
    
class ChartView(View):

    def get(self,request,*args,**kwargs):

        return render(request,"chart.html")
    
class SingUpView(View):

    def get(self,request,*args,**kwargs):

        form_instance=RegistrationForm()

        return render(request,"register.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=RegistrationForm(request.POST)

        if form_instance.is_valid():

            form_instance.save()

            messages.success(request,"signup successfull")

            # print("sucess")

            return redirect("signin")
        
        
             
            #  print("fail")
        messages.error(request,"signup failed")

        return render(request,"register.html",{"form":form_instance})
    

class SignInView(View):

    def get(self,request,*args,**kwargs):

        form_instance=LoginForm()

        return render(request,"login.html",{"form":form_instance})
    

    def post(self,request,*args,**kwargs):

        #step1 extract username,passwod from LoginForm

        form_instance=LoginForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data #{"username":"jesin","password":"Jesinn@123"}

            u_name=data.get('username')

            pwd=data.get('password')

            user_obj=authenticate(request,username=u_name,password=pwd)

            if user_obj:

               login(request,user_obj)
  
               messages.success(request,"login successfuly")
  
               return redirect("summary")
        
        messages.error(request,"login failed")

        return render(request,"login.html",{"form":form_instance})
    
    
@method_decorator(signin_requierd,name="dispatch")  
class SignOutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("signin")


class CategoryDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get('pk')

        Category.objects.get(id=id).delete()

        return redirect('catogery-add')


######API Views######


from rest_framework import generics

from myapp.serialisers import UserSerialiser,CategorySerializer

from rest_framework import permissions,authentication

from myapp.models import Category

from myapp.permissions import OwnerOnlyPermission

from rest_framework.views import APIView

from rest_framework.response import Response

from django.db.models import Count

class UserCreationView(generics.CreateAPIView):

    serializer_class=UserSerialiser

class CategoryCreateListView(generics.ListCreateAPIView):

    serializer_class=CategorySerializer

    queryset=Category.objects.all()

    authentication_classes=[authentication.BasicAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    def perform_create(self, serializer):

        return serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)
    


class CategoryRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class=CategorySerializer

    queryset=Category.objects.all()

    authentication_classes=[authentication.BasicAuthentication]

    permission_classes=[OwnerOnlyPermission]


class CategorySummaryView(APIView):

    authentication_classes=[authentication.BasicAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    def get(self,request,*args,**kwargs):

        qs=Category.objects.filter(owner=request.user)

        category_summary=qs.values("name").annotate(count=Count("name"))

        total_category_count=qs.count()

        context={

            "category_summary":category_summary,

            "category_total":total_category_count
        }

        return Response(data=context)
    

class CategoryListView(APIView):

    def get(self,request,*args,**kwargs):

        qs=Category.objects.filter().values("name").distinct()

        return Response(qs)
    

# class 
    

    




        

        

    



    

            

        

        






