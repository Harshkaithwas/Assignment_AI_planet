from django.urls import path
from .views import *


urlpatterns = [
    # Host Hackathon URLs
    path('hackathons/', HackathonListView.as_view(), name='host_hackathon_list'),
    # path('hackathons/', HostHackathonListView.as_view(), name='host_hackathon_list'),
    path('host/hackathons/', HostHackathonListView.as_view(), name='host-hackathon-list-create'),
    path('host/hackathons/<int:pk>/', HostHackathonDetailView.as_view(), name='host_hackathon_detail'),


    path('hackathons/<int:hackathon_pk>/join/', HackathonParticipantView.as_view(), name='hackathon-join'),
    path('hackathons/<int:hackathon_pk>/submit/', ParticipantSubmissionView.as_view(), name='hackathon-submit'),  # Add the URL pattern here
    path('hackathons/<int:hackathon_pk>/', HackathonDetailView.as_view(), name='hackathon_detail'),

    # Hackathon Participant URLs
    path('hackathons/<int:hackathon_pk>/join/', HackathonParticipantView.as_view(), name='join_hackathon'),
    path('host/hackathons/<int:hackathon_pk>/participants/', HackathonParticipantsListView.as_view(), name='hackathon_participants'),



    # Hackathon Detail and Update URLs for Participant
    path('host/hackathons/<int:hackathon_pk>/submissions/', HostSubmissionListView.as_view(), name='host_submission_list'),
    path('my_participating_hackathons/', UserHackathonParticipationView.as_view(), name='user_participating_hackathons'),

    path('submissions/', UserSubmissionsListView.as_view(), name='user-submissions-list'),
    
    path('submissions/<str:submission_type>/<int:pk>/', UserSubmissionDetailView.as_view(), name='user-submission-detail'),
    # To view/update a specific submission (Replace `submission_type` with 'image', 'file', or 'link')
]
