#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from django.utils import timezone
#from datetime import timedelta
'''
def create_aggregate_from_recent_assessments(user, current_assessment):
    from .models import RiskAssessment, AggregateReport

    # Define a time window for aggregation (e.g., the last 10 minutes)
    now = timezone.now()
    time_threshold = now - timedelta(minutes=1)
    print(time_threshold)
    
    # Check if there's already an AggregateReport created for this user within the time threshold
    existing_aggregate_report = AggregateReport.objects.filter(user=user, report_date__gte=time_threshold).first()

    if existing_aggregate_report:
        print("Existing aggregate report found!")
        # If the current assessment isn't already part of this report, add it
        if not existing_aggregate_report.assessments.filter(id=current_assessment.id).exists():
            existing_aggregate_report.assessments.add(current_assessment)
        return existing_aggregate_report

    # If no recent AggregateReport exists, create a new one
    aggregate_report = AggregateReport.objects.create(user=user)

    # Get RiskAssessment entries within the time window for the user
    recent_assessments = RiskAssessment.objects.filter(user=user, assesment_date_taken__gte=time_threshold)

    # If there are recent RiskAssessments, add them to the new AggregateReport
    if recent_assessments.exists():
        print("Recent assessments found, adding to new aggregate report!")
        aggregate_report.assessments.set(recent_assessments)
    else:
        # If there aren't any other recent assessments, just add the current one
        print("Only the current assessment found, adding to new aggregate report!")
        aggregate_report.assessments.add(current_assessment)

    return aggregate_report


@receiver(post_save, sender='app.RiskAssessment')
def aggregate_on_riskassessment_save(sender, instance, **kwargs):
    create_aggregate_from_recent_assessments(instance.user, instance)

'''