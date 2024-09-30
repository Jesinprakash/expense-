from django.urls import path

from myapp import views

urlpatterns = [

    path("register/",views.UserCreationView.as_view()),

    path("category/",views.CategoryCreateListView.as_view()),

    path("category/<int:pk>/",views.CategoryRetrieveUpdateDeleteView.as_view()),

    path('category/summary/',views.CategorySummaryView.as_view()),

    path('category/list/',views.CategoryListView.as_view()),



    

    

    
]