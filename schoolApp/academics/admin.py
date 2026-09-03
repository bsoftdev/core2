from django.contrib import admin
from .models import(Course, Subject,AcademicYear,Group,TeacherAssignment)

# Register your models here.

#COURSE ADMIN
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code','name','duration','is_active',)
    search_fields = ('code','name')
    list_filter = ('is_active','duration',)
    ordering = ('name',)
    list_editable = ('is_active',)
    list_per_page = 20

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code','name','course','course_year','workload','trimester','is_active',)
    search_fields = ('code','name','course__name',)
    list_filter = ('course','course_year','trimester','is_active')
    ordering =('course','course_year','trimester','name',)
    list_editable =('is_active',)
    autocomplete_fields = ('course',)
    list_per_page = 20

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('designation', 'start_date','end_date','is_active')
    search_fields = ('designation',)
    list_filter = ('is_active',)
    ordering = ('start_date',)
    list_editable = ('is_active',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('designation','course','academic_year','course_year','shit','total_students',)
    search_fields = ('designation','course__name','course__code','academic_year__designation',)
    list_filter = ('course','academic_year','course_year','shit')
    ordering = ('course', 'course_year','designation',)
    autocomplete_fields = ('course','academic_year',)

    #counting total students
    @admin.display(description='Total Estudantes')
    def total_students(self, obj):
        return obj.enrollments.count()

    
#Teacher assignments => Teacher - Group - subject
@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher','subject','group','date_assignment','is_active',)
    search_fields = ('teacher__user__first_name','teacher__user__last_name','subject__name','subject__code','group__designation')
    list_filter = ('is_active','subject','group','date_assignment',)
    autocomplete_fields = ('teacher','subject','group',)
    readonly_fields = ('date_assignment',)
    list_editable = ('is_active',)
