from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import generics
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from .models import Hackathon, ImageSubmission, FileSubmission, LinkSubmission
from .serializers import *
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, BasePermission
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

class HackathonPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsHost(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.hosted_by == request.user


class IsParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.participants.filter(id=request.user.id).exists()


class HackathonListView(ListAPIView):
    queryset = Hackathon.objects.all()
    serializer_class = HackathonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HackathonPagination


class HostHackathonListView(ListCreateAPIView):
    queryset = Hackathon.objects.all()
    serializer_class = HackathonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.kyc_document_verified and user.is_verified and user.role == 'host':
            return Hackathon.objects.filter(hosted_by=user)

        return None  # Return None instead of an empty queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset is not None:
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            response_data = {
                'error': 'You are not authorized to view hackathons.'
            }
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user

        if user.is_authenticated and user.kyc_document_verified and user.is_verified and user.role == 'host':
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                'error': 'You are not authorized to create a hackathon.'
            }
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        serializer.save(hosted_by=self.request.user)


class HostHackathonDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Hackathon.objects.all()
    serializer_class = HackathonSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class HackathonParticipantView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, hackathon_pk):
        hackathon = get_object_or_404(Hackathon, pk=hackathon_pk)
        user = request.user
        if user.role == 'host':
             return Response({"error": "You don't have permission to join this hackathon."}, status=status.HTTP_403_FORBIDDEN)
        else:
            if user in hackathon.participants.all():
                hackathon.participants.remove(user)
                return Response({"message": "You have left the hackathon."}, status=status.HTTP_200_OK)
            else:
                hackathon.participants.add(user)
                return Response({"message": "You have joined the hackathon."}, status=status.HTTP_200_OK)


class HackathonDetailView(generics.RetrieveAPIView):
    serializer_class = HackathonDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'host':
            raise PermissionDenied("You are not authorized to to see this view.")
        
        return Hackathon.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(queryset, pk=self.kwargs['hackathon_pk'])
        self.check_object_permissions(self.request, obj)
        return obj


class UserHackathonParticipationView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = HackathonSerializers

    def get_queryset(self):
        user = self.request.user
        if user.role == 'host':
            raise PermissionDenied("You are not authorized to to see this view.")
        return Hackathon.objects.filter(participants=user)


class HackathonParticipantsListView(APIView):
    permission_classes = (IsAuthenticated, IsHost)

    def get(self, request, hackathon_pk):
        hackathon = get_object_or_404(Hackathon, pk=hackathon_pk)
        participants = hackathon.participants.all()
        user = self.request.user
        data = [{"id": participant.id, "username": participant.username}
                for participant in participants]
        if user.is_authenticated and user.kyc_document_verified and user.is_verified and user.role == 'host':
            return Response(data, status=status.HTTP_200_OK)
        else:
            response_data = {
                'error': 'You are not authorized to view hackathons.'
            }
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)
        


class HostSubmissionListView(APIView):
    permission_classes = (IsAuthenticated, IsHost)

    def get(self, request, hackathon_pk):
        hackathon = get_object_or_404(Hackathon, pk=hackathon_pk)
        user = self.request.user

        # Check if the request user is the host of the hackathon
        if user.is_authenticated and user.kyc_document_verified and user.is_verified and user.role == 'host':
            if hackathon.hosted_by != request.user:
                return Response({"error": "You don't have permission to view submissions for this hackathon."}, status=status.HTTP_403_FORBIDDEN)
            response_data = {
                "hackathon": HackathonSerializer(hackathon).data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"error": "You don't have permission to view submissions for this hackathon."}, status=status.HTTP_403_FORBIDDEN)


class ParticipantSubmissionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, hackathon_pk):
        hackathon = get_object_or_404(Hackathon, pk=hackathon_pk)
        if hackathon.end_datetime.replace(tzinfo=None) < datetime.now():
            return Response({"error": "This hackathon has already ended, submissions are closed."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is already participating in the hackathon
        user = request.user
        if  user.role == 'host':
            return Response({"error": "You don't have permission for submissions for this hackathon. Only a participant can make submissions"}, status=status.HTTP_403_FORBIDDEN)

        else: 
            if user not in hackathon.participants.all():
                return Response({"error": "You are not participating in this hackathon."}, status=status.HTTP_400_BAD_REQUEST)

            data = request.data.copy()
            data["hackathon"] = hackathon.pk
            # Assign the user ID from the authenticated user
            data["user"] = user.pk

            # Check if the hackathon has a specified submission type
            if hackathon.submission_type:
                # If the hackathon has a submission type, ensure that the user's submission type matches
                submission_type = data.get("type")
                if not submission_type:
                    return Response({"error": "Submission type is required for this hackathon."}, status=status.HTTP_400_BAD_REQUEST)

                if submission_type != hackathon.submission_type:
                    return Response({"error": "Invalid submission type for this hackathon."}, status=status.HTTP_400_BAD_REQUEST)

            # If the hackathon does not have a specified submission type, allow the user to submit in any format
            serializer = None
            if not hackathon.submission_type or hackathon.submission_type == "image":
                serializer = ImageSubmissionSerializer(data=data)
            elif hackathon.submission_type == "file":
                serializer = FileSubmissionSerializer(data=data)
            elif hackathon.submission_type == "link":
                serializer = LinkSubmissionSerializer(data=data)

            if serializer and serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserSubmissionsListView(generics.ListAPIView):
    serializer_class = UserSubmissionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        # Check if the user is a host and deny access
        if user.role == 'host':
            raise PermissionDenied("You are not authorized to to see this view.")

        # Return the data you need for the serializer
        return {'user': user}

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(self.get_queryset())
        return context


class UserSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = None  # This will be set based on the submission_type

    def get_serializer_class(self):
        submission_type = self.kwargs.get('submission_type', None)
        if submission_type == 'image':
            return ImageSubmissionSerializer
        elif submission_type == 'file':
            return FileSubmissionSerializer
        elif submission_type == 'link':
            return LinkSubmissionSerializer
        else:
            return None

    def get_queryset(self):
        user = self.request.user
        submission_type = self.kwargs.get('submission_type', None)
        if submission_type == 'image':
            return ImageSubmission.objects.filter(user=user)
        elif submission_type == 'file':
            return FileSubmission.objects.filter(user=user)
        elif submission_type == 'link':
            return LinkSubmission.objects.filter(user=user)
        else:
            return None

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(queryset, pk=self.kwargs.get('pk'))
        self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Submission deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()



