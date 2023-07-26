from django.contrib import admin
from .models import Hackathon, ImageSubmission, FileSubmission, LinkSubmission


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_datetime', 'end_datetime']
    list_filter = ['start_datetime', 'end_datetime']
    search_fields = ['title']

# from .models import ImageSubmission, FileSubmission, LinkSubmission


class ImageSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_of_submission', 'image', 'hackathon', 'user']


class FileSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_of_submission', 'file', 'hackathon', 'user']


class LinkSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_of_submission', 'link', 'hackathon', 'user']


admin.site.register(ImageSubmission, ImageSubmissionAdmin)
admin.site.register(FileSubmission, FileSubmissionAdmin)
admin.site.register(LinkSubmission, LinkSubmissionAdmin)
