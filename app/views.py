"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpRequest
from .forms import RiskTopicForm, RiskFactorForm, ResponseForm, RecommendationForm
from .models import RiskTopic, RiskFactor, Response, UserResponse, Recommendation, RiskAssessment,TemporaryResponses, AggregateReport
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from collections import defaultdict
from django.views import View
from django.utils import timezone
from rest_framework import viewsets
from .serializers import RiskTopicSerializer, RiskFactorSerializer, ResponseSerializer, UserResponseSerializer, RecommendationSerializer, RiskAssessmentSerializer
from django.http import JsonResponse
import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView

from .utils import auto_link_recommendations_to_assessment

logger = logging.getLogger(__name__)
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

   
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,

        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )


############# Views to my app ##################
def create_risk_topic(request):
    if request.method == 'POST':
        form = RiskTopicForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RiskTopicForm()
    return render(request, 'app/create_risk_topic.html', {'form': form})

def create_risk_factor(request):
    if request.method == 'POST':
        form = RiskFactorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RiskFactorForm()
    return render(request, 'app/create_risk_factor.html', {'form': form})

def create_response(request):
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ResponseForm()
    return render(request, 'app/create_response.html', {'form': form})


def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def create_recommendation(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RecommendationForm()
    return render(request, 'app/create_recommendation.html', {'form': form})

# views.py

##########################################################################


def risk_assessment(request, risk_assessment_id):
    current_assessment = get_object_or_404(RiskAssessment, id=risk_assessment_id)
    
    # Get all assessments for the current user and topic
    all_assessments = RiskAssessment.objects.filter(user=request.user, risk_topic=current_assessment.risk_topic).order_by('-assesment_date_taken')

    assessments_data = []

    for assessment in all_assessments:
        # Find related user responses based on the date of the assessment
        user_responses = UserResponse.objects.filter(
            user=request.user, 
            response_date=assessment.assesment_date_taken
        )
        
        total_score = assessment.total_score
        
        # Compute the max_score for the current assessment
        risk_factors = RiskFactor.objects.filter(risk_topic=assessment.risk_topic)
        max_score_for_current_assessment = 0
        for risk_factor in risk_factors:
            max_severity = risk_factor.responses.all().order_by('-severity').first()
            if max_severity:
                max_score_for_current_assessment += max_severity.severity * risk_factor.weight
        
        # Fetch recommendations based on risk_topic and total_score
        recommendations = Recommendation.objects.filter(
            risk_topic=assessment.risk_topic,
            min_score__lte=total_score,
            max_score__gte=total_score
        )
        
        assessments_data.append({
            'assessment_date': assessment.assesment_date_taken,
            'total_score': total_score,
            'max_score': max_score_for_current_assessment, # Add this line to pass max_score for each assessment
            'recommendations': recommendations
        })

    return render(request, 'app/risk_assessment.html', {
        'assessments_data': assessments_data,
    })





@login_required
def questionnaire(request):
    topic_id = request.GET.get('topic_id')
    topic = get_object_or_404(RiskTopic, id=topic_id)
    questions = topic.risk_factors.all()

    # Check if the user has already responded to any question in this topic
    has_answered = UserResponse.objects.filter(user=request.user, risk_factor__in=questions).exists()

    if request.method == 'POST':
        total_score = 0
        user_responses = []
        missing_response = False  # Flag to check if a response is missing

        # Process the answers and calculate the total score
        for question in questions:
            response_id = request.POST.get('response_' + str(question.id))

            if not response_id:
                messages.warning(request, 'You did not choose a response for one of the questions.')
                missing_response = True  # Set flag to True
                break

            try:
                response = Response.objects.get(id=response_id)
                user_response = UserResponse(user=request.user, risk_factor=question, response=response)
                user_responses.append(user_response)

                # Calculate the score for the risk assessment
                total_score += response.severity * question.weight

            except Response.DoesNotExist:
                messages.error(request, 'An error occurred. Please try again.')

        # If there's a missing response, redirect without saving anything
        if missing_response:
            return render(request, 'app/questionnaire.html', {'topic': topic, 'questions': questions})

        with transaction.atomic():
            # Create UserResponse objects in a batch
            UserResponse.objects.bulk_create(user_responses)

            # Create RiskAssessment object
            RiskAssessment.objects.create(user=request.user, risk_topic=topic, total_score=total_score)

        messages.success(request, 'Your responses have been recorded. Thank you!')
        return redirect('aggregate_reports_list')  # Redirect to topics_page after successful submission

    return render(request, 'app/questionnaire.html', {'topic': topic, 'questions': questions})




@login_required
def topics_page(request):
    all_topics = RiskTopic.objects.all()

    # Get all the RiskAssessments that this user has done
    answered_risk_assessments = RiskAssessment.objects.filter(user=request.user).order_by('risk_topic', '-assesment_date_taken')

    # Extract distinct topics answered by the user
    answered_topics = set(assessment.risk_topic_id for assessment in answered_risk_assessments)

    return render(request, 'app/topics_page.html', {
        'all_topics': all_topics,
        'answered_topics': answered_topics,
        'answered_risk_assessments': answered_risk_assessments
    })




@login_required
def user_dashboard(request):
    user_responses = UserResponse.objects.filter(user=request.user).select_related('risk_factor', 'response')
    context = {
        'user_responses': user_responses,
    }
    return render(request, 'app/user_dashboard.html', context)


def get_ordered_risk_factors(risk_factors):
    ordered_risk_factors = []

    def add_risk_factor(risk_factor):
        if risk_factor.depends_on:
            add_risk_factor(risk_factor.depends_on)
        if risk_factor not in ordered_risk_factors:
            ordered_risk_factors.append(risk_factor)

    for risk_factor in risk_factors:
        add_risk_factor(risk_factor)

    return ordered_risk_factors

@login_required
def questionnaire2(request):
    risk_topics = RiskTopic.objects.all()
    risk_factors = RiskFactor.objects.all()
    ordered_risk_factors = get_ordered_risk_factors(risk_factors)
    response_id_to_text = {
        response.id: response.text for risk_factor in risk_factors for response in risk_factor.responses.all()
    }

    # Retrieve any saved responses for the current user
    saved_responses = TemporaryResponses.objects.filter(user=request.user)
    saved_data = {f'response_{response.risk_factor.id}': response.response.id for response in saved_responses}

    user_answers = saved_data if request.method != 'POST' else {
        k: v for k, v in request.POST.items() if k.startswith('response_')
    }

    if request.method == 'POST':
        total_score = 0
        max_score_per_topic = defaultdict(int)  # Dicionário para armazenar a pontuação máxima por tópico
        user_responses = []
        topic_scores = defaultdict(int)  # Dicionário para armazenar a pontuação por tópico
        
        for risk_factor in ordered_risk_factors:
            response_id = request.POST.get(f'response_{risk_factor.id}')
            user_answers.update({f'response_{risk_factor.id}': response_id})
            
            severity = 0
            if response_id:
                try:
                    # Se uma resposta foi fornecida, adicione a pontuação máxima possível para esse fator
                    max_score_per_topic[risk_factor.risk_topic.id] += risk_factor.weight * 5  # Assumindo que a severidade máxima é 5
                    response = Response.objects.get(id=response_id)
                    user_response = UserResponse(user=request.user, risk_factor=risk_factor, response=response)
                    user_responses.append(user_response)
                    severity = response.severity
                except Response.DoesNotExist:
                    messages.error(request, 'Ocorreu um erro. Por favor, tente novamente.')
            
            score = severity * risk_factor.weight
            total_score += score
            topic_scores[risk_factor.risk_topic.id] += score
        
        with transaction.atomic():
            # Create a new AggregateReport for this batch of assessments
            new_aggregate_report = AggregateReport.objects.create(user=request.user)
            
            UserResponse.objects.bulk_create(user_responses)
            new_assessments = []  # List to hold newly created RiskAssessment objects

            for topic_id, score in topic_scores.items():
                topic = get_object_or_404(RiskTopic, id=topic_id)
                max_score = max_score_per_topic[topic_id]
                percentage_score = (score / max_score) * 100 if max_score > 0 else 0
                
                # Create RiskAssessment and link it to the new AggregateReport
                assessment = RiskAssessment.objects.create(
                    user=request.user,
                    risk_topic=topic,
                    total_score=percentage_score,
                    aggregate_report=new_aggregate_report
                )
                auto_link_recommendations_to_assessment(assessment)
                new_assessments.append(assessment)
            
            # Optionally, if you want to set the assessments for the aggregate report explicitly:
            new_aggregate_report.assessments.set(new_assessments)
                
        TemporaryResponses.objects.filter(user=request.user).delete()
        messages.success(request, 'Suas respostas foram registradas. Obrigado!')
        return redirect('aggregate_reports_list')


    return render(request, 'app/questionnaire2.html', {
        'risk_topics': risk_topics,
        'risk_factors': ordered_risk_factors,
        'response_id_to_text': response_id_to_text,
        'user_answers': user_answers
    })



class SaveTemporaryResponsesView(View):
    def post(self, request, *args, **kwargs):
        logger.info(request.POST)
        logging.info('SaveTemporaryResponsesView post method called')
        # Delete any existing temporary responses for this user
        TemporaryResponses.objects.filter(user=request.user).delete()
        
        # Save new temporary responses
        for key, value in request.POST.items():
            print(key)
            if key.startswith('response_'):
                risk_factor_id = int(key.split('_')[1])
                risk_factor = RiskFactor.objects.get(id=risk_factor_id)
                response = Response.objects.get(id=value)
                TemporaryResponses.objects.create(
                    user=request.user,
                    risk_factor=risk_factor,
                    response=response,
                )
        
        return JsonResponse({'message': 'Responses saved temporarily'})



@login_required
def reports_list_view(request):
    user = request.user
    assessments = RiskAssessment.objects.filter(user=user).order_by('-assesment_date_taken')
    context = {
        'assessments': assessments,
    }
    return render(request, 'app/reports_list.html', context)

@login_required
def report_detail_view(request, assessment_id):
    assessment = RiskAssessment.objects.get(id=assessment_id, user=request.user)
    recommendations = Recommendation.objects.filter(
        risk_topic=assessment.risk_topic,
        min_score__lte=assessment.total_score,
        max_score__gte=assessment.total_score
    )
    context = {
        'assessment': assessment,
        'recommendations': recommendations,
    }
    return render(request, 'app/report_detail.html', context)


def display_aggregate_report(request, report_id):
    report = get_object_or_404(AggregateReport, id=report_id)

    # Access the linked assessments directly through the related_name
    linked_assessments = report.linked_assessments.all()

    context = {
        'report': report,
        'linked_assessments': linked_assessments,
    }

    return render(request, 'app/aggregate_report.html', context)






@method_decorator(login_required, name='dispatch')
class AggregateReportListView(ListView):
    model = AggregateReport
    template_name = "app/aggregate_reports_list.html"
    context_object_name = "reports"

    def get_queryset(self):
        # Filter the aggregate reports to only show the ones for the currently logged in user.
        return AggregateReport.objects.filter(user=self.request.user).order_by('-report_date')

def generate_recommendations(user, total_score):
    all_recommendations = Recommendation.objects.all()
    applicable_recommendations = []

    # Fetch score-based recommendations
    for recommendation in all_recommendations:
        if recommendation.is_applicable(score=total_score):
            applicable_recommendations.append(recommendation)

    # Fetch response-based recommendations
    important_responses = UserResponse.objects.filter(user=user, risk_factor__is_important=True)
    for user_response in important_responses:
        for recommendation in all_recommendations:
            if recommendation.is_applicable(response=user_response.response):
                applicable_recommendations.append(recommendation)

    # Link recommendations to the RiskAssessment (or another model if needed)
    assessment = RiskAssessment.objects.get(user=user)
    for recommendation in applicable_recommendations:
        assessment.recommendations.add(recommendation)
    assessment.save()

    return applicable_recommendations


                                               #### Report NEW 17/10/2023 ####

########################################################## RESTAPI ###################################################################

from rest_framework import viewsets
from .serializers import RiskTopicSerializer, RiskFactorSerializer, ResponseSerializer, UserResponseSerializer, RecommendationSerializer, RiskAssessmentSerializer

class RiskTopicViewSet(viewsets.ModelViewSet):
    queryset = RiskTopic.objects.all()
    serializer_class = RiskTopicSerializer

class RiskFactorViewSet(viewsets.ModelViewSet):
    queryset = RiskFactor.objects.all()
    serializer_class = RiskFactorSerializer

class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

class UserResponseViewSet(viewsets.ModelViewSet):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer

class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer

class RiskAssessmentViewSet(viewsets.ModelViewSet):
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
