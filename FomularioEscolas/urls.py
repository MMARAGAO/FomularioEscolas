"""
Definition of urls for FomularioEscolas.
"""

from datetime import datetime
from django.urls import path,include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from app.views import SaveTemporaryResponsesView



router = DefaultRouter()
router.register(r'risktopics', views.RiskTopicViewSet)
router.register(r'riskfactors', views.RiskFactorViewSet)
router.register(r'responses', views.ResponseViewSet)
router.register(r'userresponses', views.UserResponseViewSet)
router.register(r'recommendations', views.RecommendationViewSet)
router.register(r'riskassessments', views.RiskAssessmentViewSet)




urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),

    path('create_risk_topic/', views.create_risk_topic, name='create_risk_topic'),
    path('create_risk_factor/', views.create_risk_factor, name='create_risk_factor'),
    path('create_response/', views.create_response, name='create_response'),
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    path('questionnaire2/', views.questionnaire2, name='questionnaire2'),

    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('create_recommendation/', views.create_recommendation, name='create_recommendation'),
    path('topics/', views.topics_page, name='topics_page'),
    path('risk_assessment/<int:risk_assessment_id>/', views.risk_assessment, name='risk_assessment'),
    path('save-temporary-responses/', SaveTemporaryResponsesView.as_view(), name='save-temporary-responses'),
    path('api/', include(router.urls)),
    path('reports/', views.reports_list_view, name='reports_list'),
    path('report/<int:assessment_id>/', views.report_detail_view, name='report_detail'),
    path('aggregate-report/<int:report_id>/', views.display_aggregate_report, name='aggregate_report'),
    path('aggregate_reports/', views.AggregateReportListView.as_view(), name='aggregate_reports_list'),
]




