from rest_framework import serializers
from .models import Hackathon, ImageSubmission, FileSubmission, LinkSubmission

class ImageSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSubmission
        fields = '__all__'

class FileSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileSubmission
        fields = '__all__'

class LinkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkSubmission
        fields = '__all__'

class HackathonSerializers(serializers.ModelSerializer):
    image_submissions = serializers.SerializerMethodField(read_only=True)
    file_submissions = serializers.SerializerMethodField(read_only=True)
    link_submissions = serializers.SerializerMethodField(read_only=True)

    
    def get_image_submissions(self, instance):
        user = self.context['request'].user
        image_submissions = ImageSubmission.objects.filter(hackathon=instance, user=user)
        serializer = ImageSubmissionSerializer(image_submissions, many=True)
        return serializer.data

    def get_file_submissions(self, instance):
        user = self.context['request'].user
        file_submissions = FileSubmission.objects.filter(hackathon=instance, user=user)
        serializer = FileSubmissionSerializer(file_submissions, many=True)
        return serializer.data

    def get_link_submissions(self, instance):
        user = self.context['request'].user
        link_submissions = LinkSubmission.objects.filter(hackathon=instance, user=user)
        serializer = LinkSubmissionSerializer(link_submissions, many=True)
        return serializer.data

    class Meta:
        model = Hackathon
        fields = '__all__'





class HackathonSerializer(serializers.ModelSerializer):
    image_submissions = ImageSubmissionSerializer(many=True, read_only=True)
    file_submissions = FileSubmissionSerializer(many=True, read_only=True)
    link_submissions = LinkSubmissionSerializer(many=True, read_only=True)

    class Meta:
        model = Hackathon
        fields = '__all__'

    

class UserSubmissionsSerializer(serializers.Serializer):
    image_submissions = serializers.SerializerMethodField(read_only=True)
    file_submissions = serializers.SerializerMethodField(read_only=True)
    link_submissions = serializers.SerializerMethodField(read_only=True)

    def get_image_submissions(self, instance):
        user = self.context['request'].user
        image_submissions = ImageSubmission.objects.filter(user=user)
        image_serializer = ImageSubmissionSerializer(image_submissions, many=True)
        return image_serializer.data

    def get_file_submissions(self, instance):
        user = self.context['request'].user
        file_submissions = FileSubmission.objects.filter(user=user)
        file_serializer = FileSubmissionSerializer(file_submissions, many=True)
        return file_serializer.data

    def get_link_submissions(self, instance):
        user = self.context['request'].user
        link_submissions = LinkSubmission.objects.filter(user=user)
        link_serializer = LinkSubmissionSerializer(link_submissions, many=True)
        return link_serializer.data
    


class HackathonDetailSerializer(serializers.ModelSerializer):
    image_submissions = ImageSubmissionSerializer(source='imagesubmission_set', many=True, read_only=True)
    file_submissions = FileSubmissionSerializer(source='filesubmission_set', many=True, read_only=True)
    link_submissions = LinkSubmissionSerializer(source='linksubmission_set', many=True, read_only=True)

    class Meta:
        model = Hackathon
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user

        if user.role == 'participant':
            # Filter the submissions for the current user in this hackathon
            image_submissions = ImageSubmission.objects.filter(user=user, hackathon=instance)
            file_submissions = FileSubmission.objects.filter(user=user, hackathon=instance)
            link_submissions = LinkSubmission.objects.filter(user=user, hackathon=instance)

            # Add the user's submissions to the response
            data['image_submissions'] = ImageSubmissionSerializer(image_submissions, many=True).data
            data['file_submissions'] = FileSubmissionSerializer(file_submissions, many=True).data
            data['link_submissions'] = LinkSubmissionSerializer(link_submissions, many=True).data

        return data