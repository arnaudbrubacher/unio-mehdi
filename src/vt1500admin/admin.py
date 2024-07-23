from django.contrib import admin

# Register your models here.
# Register your models here.
from .models import Voter
 
# # admin.site.register(Question)
# # admin.site.register(Choice)
 
# admin.site.site_header = "Election Admin"
# admin.site.site_title = "Election Admin Area"
# admin.site.index_title = "Welcome to the Election Admin Area"
 
 
# class ChoiceInLine(admin.TabularInline):
#     model = Choice
#     extra = 3
 
 
# class QuestionAdmin(admin.ModelAdmin):
#     fieldsets = [(None, {'fields': ['question_text']}), ('Date Information', {
#         'fields': ['pub_date'], 'classes': ['collapse']}), ]
#     inlines = [ChoiceInLine]
 
 
admin.site.register(Voter)
