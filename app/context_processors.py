from app.models import TemporaryResponses

def questionnaire_context(request):
    if request.user.is_authenticated:
        has_saved_responses = TemporaryResponses.objects.filter(user=request.user).exists()
    else:
        has_saved_responses = False

    return {
        'has_saved_responses': has_saved_responses
    }