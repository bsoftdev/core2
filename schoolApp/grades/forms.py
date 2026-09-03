from django import forms
from .models import Grade, Evaluation
from enrollments.models import Enrollment

class GradeAdminForm(forms.ModelForm):

    class Meta:
        model = Grade
        fields = [
               'enrollment',
               'avaluation',
               'value',
               'observation',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['avaluation'].queryset = Evaluation.objects.none()

        enrollment = None
        
        # Se a instância já existe no banco de dados
        if self.instance.pk:
            enrollment = self.instance.enrollment
            
        #  Se o formulário foi submetido (POST/GET)
        elif self.data.get('enrollment'):
            
            try:
                enrollment = Enrollment.objects.get(pk=self.data.get('enrollment'))
            except (Enrollment.DoesNotExist, ValueError, TypeError):
                pass
                
        #  Se o formulário recebeu dados iniciais (Ex: URL query params)
        elif self.initial.get('enrollment'):
            try:
                enrollment = Enrollment.objects.get(pk=self.initial.get('enrollment'))
            except (Enrollment.DoesNotExist, ValueError, TypeError):
                pass

        # Aplica o filtro se encontrou a matrícula válida
        if enrollment:
            self.fields['avaluation'].queryset = Evaluation.objects.filter(
                group=enrollment.group,
                is_active=True
            )
