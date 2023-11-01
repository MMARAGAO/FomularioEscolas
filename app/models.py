from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class RiskTopic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
      return self.name

class RiskFactor(models.Model):
    HISTORICAL = 'HI'
    FACILITY = 'FA'
    RISK_FACTOR_CATEGORIES = [
        (HISTORICAL, 'Historical'),
        (FACILITY, 'Facility'),
    ]

    risk_topic = models.ForeignKey(RiskTopic, related_name="risk_factors", on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    description = models.TextField()
    weight = models.FloatField(default=1.0)
    category = models.CharField(
        max_length=2,
        choices=RISK_FACTOR_CATEGORIES,
        default=FACILITY,
    )
    depends_on = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name="dependent_risk_factors") 
    trigger_response = models.ManyToManyField('Response', blank=True, null=True, related_name="trigger_risk_factors") 
    responses = models.ManyToManyField('Response', related_name="risk_factors")  # ManyToManyField added here
    is_important = models.BooleanField(default=False)

    def __str__(self):
      return self.question

class Response(models.Model):
    text = models.CharField(max_length=200)
    severity = models.IntegerField()

    def __str__(self):
      return self.text



class UserResponse(models.Model):
    risk_factor = models.ForeignKey(RiskFactor, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.response.text

class Recommendation(models.Model):
    SCORE_BASED = 'SB'
    RESPONSE_BASED = 'RB'
    RECOMMENDATION_TYPES = [
        (SCORE_BASED, 'Score Based'),
        (RESPONSE_BASED, 'Response Based'),
    ]

    recommendation_type = models.CharField(
        max_length=2,
        choices=RECOMMENDATION_TYPES,
        default=SCORE_BASED,
    )
    risk_topic = models.ForeignKey(RiskTopic, on_delete=models.CASCADE)
    risk_factor = models.ForeignKey(RiskFactor, on_delete=models.SET_NULL, blank=True, null=True) # For specific response-based recommendations
    expected_response = models.ForeignKey(Response, on_delete=models.SET_NULL, blank=True, null=True)  # The expected response that triggers the recommendation
    min_score = models.IntegerField(blank=True, null=True)  # Score range for score-based recommendations
    max_score = models.IntegerField(blank=True, null=True)  # Score range for score-based recommendations
    text = models.TextField()

    def is_applicable(self, score=None, response=None):
        if self.recommendation_type == self.SCORE_BASED:
            return self.min_score <= score <= self.max_score
        elif self.recommendation_type == self.RESPONSE_BASED and response:
            return self.expected_response == response
        return False


class RiskAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Assuming you have a User model
    risk_topic = models.ForeignKey(RiskTopic, on_delete=models.CASCADE)
    total_score = models.IntegerField()
    recommendations = models.ManyToManyField(Recommendation)
    assesment_date_taken = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    aggregate_report = models.ForeignKey('AggregateReport', on_delete=models.SET_NULL, null=True, related_name="linked_assessments")
    @property
    def score_based_recommendations(self):
        return self.recommendations.filter(recommendation_type=Recommendation.SCORE_BASED)

    @property
    def response_based_recommendations(self):
        return self.recommendations.filter(recommendation_type=Recommendation.RESPONSE_BASED)


class AggregateReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessments = models.ManyToManyField(RiskAssessment)
    report_date = models.DateField(auto_now_add=True)

    def get_recommendations(self):
        recommendations = []
        for assessment in self.assessments.all():
            recommendations.extend(list(assessment.recommendations.all()))
        return recommendations

    @property
    def total_score(self):
        return sum(assessment.total_score for assessment in self.assessments.all())


class TemporaryResponses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    risk_factor = models.ForeignKey(RiskFactor, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

