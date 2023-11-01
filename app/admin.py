from django.contrib import admin
from .models import RiskTopic, RiskFactor, Response, UserResponse, Recommendation, RiskAssessment, TemporaryResponses, AggregateReport

class RiskTopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class RiskFactorAdmin(admin.ModelAdmin):
    def risk_topic_name(self, obj):
        return obj.risk_topic.name
    risk_topic_name.short_description = 'Risk Topic' # Sets column name in admin panel

    list_display = ('question', 'risk_topic_name', 'weight')

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('text', 'severity')
    
    def risk_factor_display(self, obj):
        return obj.risk_factor.question
    risk_factor_display.short_description = 'Risk Factor Question'

class UserResponseAdmin(admin.ModelAdmin):
    def user_email(self, instance):
        return instance.user.email
    list_display = ('user_email', 'risk_factor', 'response')

class RecommendationAdmin(admin.ModelAdmin):
    def risk_topic_info(self, obj):
        return obj.risk_topic.name
    risk_topic_info.short_description = 'Risk Topic' # or 'Risk Topic Info' if you prefer

    list_display = ('risk_topic_info', 'text')

class RiskAssessmentAdmin(admin.ModelAdmin):
    def user_email(self, instance):
        return instance.user.email
    list_display = ('user_email', 'risk_topic', 'total_score','assesment_date_taken')
    
class TemporaryResponsesAdmin(admin.ModelAdmin):
    def user_email(self, instance):
        return instance.user
    list_display = ('user', 'risk_factor', 'response','timestamp')

class AggregateReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment_count', 'report_date')

    def assessment_count(self, obj):
        return obj.assessments.count()
    assessment_count.short_description = 'Number of Assessments'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('assessments')
        return queryset


admin.site.register(RiskTopic, RiskTopicAdmin)
admin.site.register(RiskFactor, RiskFactorAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(UserResponse, UserResponseAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(RiskAssessment, RiskAssessmentAdmin)
admin.site.register(TemporaryResponses,TemporaryResponsesAdmin)
admin.site.register(AggregateReport,AggregateReportAdmin)

