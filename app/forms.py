"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _



from .models import RiskTopic, RiskFactor, Response, Recommendation

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))



##################myAPP################


class RiskTopicForm(forms.ModelForm):
    class Meta:
        model = RiskTopic
        fields = ['name', 'description']
        labels = {
            'name': 'Tópico',
            'description': 'Descrição principal',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class RiskFactorForm(forms.ModelForm):
    class Meta:
        model = RiskFactor
        fields = ['risk_topic','description', 'question', 'weight', 'category', 'depends_on', 'trigger_response']
        labels = {
            'risk_topic': 'Tópico da Questão',
            'question': 'Questão',
            'description': 'Tema',
            'weight': 'Peso da questão. (0-1)',
            'category': 'Categoria do Fator de Risco',
            'depends_on': 'Depende de',
            'trigger_response': 'Resposta Trigger',
        }
        widgets = {
            'risk_topic': forms.Select(attrs={'class': 'form-control'}),
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'depends_on': forms.Select(attrs={'class': 'form-control'}),
            'trigger_response': forms.Select(attrs={'class': 'form-control'}),
        }
class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text', 'severity']  # Removed 'risk_factor' from here
        labels = {
            'text': 'Resposta para questão',
            'severity': 'Vível de severidade',
        }
        help_texts = {
            'severity': 'Niveis de segurança: 1 - Nível muito Baixo ; 2 - Nível baixo ; 3 - Nível médio ; 4 - Nível alto ; 5 - Nível Muito Alto   ',
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'severity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RecommendationForm(forms.ModelForm):
    class Meta:
        model = Recommendation
        fields = ['risk_topic', 'min_score', 'max_score', 'text']
        widgets = {
            'risk_topic': forms.Select(attrs={'class': 'form-control'}),
            'min_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
