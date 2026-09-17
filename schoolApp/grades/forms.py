from django import forms
from .models import Grade, AcademicEvaluation
from enrollments.models import Enrollment


class GradeAdminForm(forms.ModelForm):

    class Meta:
        model = Grade
         'avaluation' -> 'academic_evaluation' (nome do campo mudou)
        fields = ['enrollment', 'academic_evaluation', 'value', 'observation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #  o queryset filtrado é de AcademicEvaluation, não
        # Evaluation (Evaluation não tem 'group').
        self.fields['academic_evaluation'].queryset = AcademicEvaluation.objects.none()

        enrollment = None

        if self.instance.pk:
            enrollment = self.instance.enrollment
        elif self.data.get('enrollment'):
            try:
                enrollment = Enrollment.objects.get(pk=self.data.get('enrollment'))
            except (Enrollment.DoesNotExist, ValueError, TypeError):
                pass
        elif self.initial.get('enrollment'):
            try:
                enrollment = Enrollment.objects.get(pk=self.initial.get('enrollment'))
            except (Enrollment.DoesNotExist, ValueError, TypeError):
                pass

        if enrollment:
            self.fields['academic_evaluation'].queryset = AcademicEvaluation.objects.filter(
                group=enrollment.group,
                is_active=True,
            ).select_related('evaluation', 'subject')