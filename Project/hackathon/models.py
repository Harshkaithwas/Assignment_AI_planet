from django.db import models
from accounts.models import Account

SUBMISSION_CHOICES = [
    ('image', 'Image'),
    ('file', 'File'),
    ('link', 'Link'),
]


class ImageSubmission(models.Model):
    name_of_submission = models.CharField(max_length=100)
    summary = models.TextField()
    image = models.ImageField(upload_to='hackathon_submissions/images/')
    hackathon = models.ForeignKey(
        'Hackathon', on_delete=models.CASCADE, related_name='image_submissions')
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='image_submissions')


class FileSubmission(models.Model):
    name_of_submission = models.CharField(max_length=100)
    summary = models.TextField()
    file = models.FileField(upload_to='hackathon_submissions/files/')
    hackathon = models.ForeignKey(
        'Hackathon', on_delete=models.CASCADE, related_name='file_submissions')
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='file_submissions')


class LinkSubmission(models.Model):
    name_of_submission = models.CharField(max_length=100)
    summary = models.TextField()
    link = models.URLField()
    hackathon = models.ForeignKey(
        'Hackathon', on_delete=models.CASCADE, related_name='link_submissions')
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='link_submissions')


class Hackathon(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    background_image = models.ImageField(
        upload_to='hackathon_backgrounds/', null=True, blank=True)
    hackathon_image = models.ImageField(
        upload_to='hackathon_images/', null=True, blank=True)
    submission_type = models.CharField(
        max_length=10, choices=SUBMISSION_CHOICES)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reward_prize = models.CharField(max_length=100)
    hosted_by = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='hosted_hackathons')
    participants = models.ManyToManyField(
        Account, related_name='enrolled_hackathons', blank=True)

    def __str__(self):
        return self.title
