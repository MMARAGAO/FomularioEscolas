from .models import RiskTopic, RiskFactor, Response, UserResponse, Recommendation, RiskAssessment,TemporaryResponses, AggregateReport


def auto_link_recommendations_to_assessment(assessment):
    # Get all score-based recommendations applicable to this assessment's score
    score_based_recommendations = Recommendation.objects.filter(
        recommendation_type=Recommendation.SCORE_BASED,
        risk_topic=assessment.risk_topic,
        min_score__lte=assessment.total_score,
        max_score__gte=assessment.total_score
    )

    # Get all response-based recommendations for the risk topic of this assessment
    response_based_recommendations_query = Recommendation.objects.filter(
        recommendation_type=Recommendation.RESPONSE_BASED,
        risk_topic=assessment.risk_topic
    ).select_related('expected_response', 'risk_factor')

    # Get the user's responses for the risk factors associated with the response-based recommendations
    user_responses = UserResponse.objects.filter(
        user=assessment.user,
        risk_factor__in=response_based_recommendations_query.values_list('risk_factor', flat=True)
    ).select_related('response')

    applicable_response_based_recommendations = []
    for recommendation in response_based_recommendations_query:
        # Check if the user's response matches the expected response for this recommendation
        user_response = user_responses.filter(risk_factor=recommendation.risk_factor).first()
        if user_response and user_response.response == recommendation.expected_response:
            applicable_response_based_recommendations.append(recommendation)

    # Debug output
    print(f"Debug: Score-Based Recommendations linked: {score_based_recommendations.count()}")
    print(f"Debug: Response-Based Recommendations linked: {len(applicable_response_based_recommendations)}")

    # Link the applicable recommendations to the assessment
    assessment.recommendations.set(
        list(score_based_recommendations) + applicable_response_based_recommendations
    )
    assessment.save()

