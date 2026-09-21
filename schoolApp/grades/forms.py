from django import forms
from unfold.widgets import UnfoldAdminTextareaWidget, UnfoldAdminSelectWidget
from .models import Grade, AcademicEvaluation
from enrollments.models import Enrollment


class GradeAdminForm(forms.ModelForm):

    class Meta:
        model = Grade
        fields = ['enrollment', 'academic_evaluation', 'value', 'observation']
        widgets = {
            # 'enrollment' continua com autocomplete_fields no GradeAdmin.
            # 'academic_evaluation' passou a <select> normal (ver nota no
            # admin.py) — precisa do widget do Unfold explicitamente,
            # já que sai de fora do mecanismo automático do autocomplete.
            'academic_evaluation': UnfoldAdminSelectWidget(),
            'observation': UnfoldAdminTextareaWidget(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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