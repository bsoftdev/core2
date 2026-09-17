from django.contrib import admin
from django.contrib import messages

from .models import (
    Course,
    Subject,
    AcademicYear,
    Group,
    TeacherAssignment,
)

from grades.services import generate_evaluations_for_group


# =========================================================
# COURSE ADMIN
# =========================================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'duration', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active', 'duration')
    ordering = ('name',)
    list_editable = ('is_active',)
    list_per_page = 20


# =========================================================
# SUBJECT ADMIN
# =========================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'course', 'course_year', 'workload', 'is_active')
    search_fields = ('code', 'name', 'course__name')
    list_filter = ('course', 'course_year', 'is_active')
    ordering = ('course', 'course_year', 'name')
    list_editable = ('is_active',)
    autocomplete_fields = ('course',)
    list_per_page = 20


# =========================================================
# ACADEMIC YEAR ADMIN
# =========================================================

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('designation', 'start_date', 'end_date', 'is_active')
    search_fields = ('designation',)
    list_filter = ('is_active',)
    ordering = ('start_date',)
    list_editable = ('is_active',)


# =========================================================
# GROUP ADMIN
# =========================================================

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # CORREÇÃO: 'shit' -> 'shift' em list_display e list_filter.
    list_display = (
        'designation',
        'course',
        'course_year',
        'academic_year',
        'shift',
    )

    list_filter = (
        'course',
        'course_year',
        'academic_year',
        'shift',
    )

    search_fields = (
        'designation',
        'course__name',
        'course__code',
    )

    actions = (
        'generate_first_trimester',
        'generate_second_trimester',
        'generate_third_trimester',
    )



    @admin.action(description='Gerar avaliações - 1º Trimestre')
    def generate_first_trimester(self, request, queryset):
        self._generate_evaluations(request, queryset, 1)

    @admin.action(description='Gerar avaliações - 2º Trimestre')
    def generate_second_trimester(self, request, queryset):
        self._generate_evaluations(request, queryset, 2)

    @admin.action(description='Gerar avaliações - 3º Trimestre')
    def generate_third_trimester(self, request, queryset):
        self._generate_evaluations(request, queryset, 3)

    def _generate_evaluations(self, request, queryset, trimester):
        total_created = 0
        total_existing = 0

        for group in queryset:
            created, existing = generate_evaluations_for_group(group, trimester)
            total_created += created
            total_existing += existing

        self.message_user(
            request,
            (
                f'Processo concluído. '
                f'{total_created} avaliações criadas. '
                f'{total_existing} avaliações já existiam.'
            ),
            messages.SUCCESS
        )


# =========================================================
# TEACHER ASSIGNMENTS ADMIN
# =========================================================

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'group', 'date_assignment', 'is_active')
    search_fields = (
        'teacher__user__first_name',
        'teacher__user__last_name',
        'subject__name',
        'subject__code',
        'group__designation',
    )
    list_filter = ('is_active', 'subject', 'group', 'date_assignment')
    autocomplete_fields = ('teacher', 'subject', 'group')
    readonly_fields = ('date_assignment',)
    list_editable = ('is_active',)