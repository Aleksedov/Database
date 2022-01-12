from rest_framework import serializers
from .models import *

# class VictimSerializer(serializers.Serializer):
#     id = serializers.CharField(max_length=8)
#     name = serializers.CharField(max_length=120)
#     date_of_birth = serializers.CharField(max_length=20)
#     restriction_id = serializers.CharField(max_length=5)
#     def create(self, validated_data):
#         return Victim.objects.create(**validated_data)
#     def update(self, instance, validated_data):
#         instance.id = validated_data.get('id', instance.id)
#         instance.name = validated_data.get('name', instance.name)
#         instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
#         instance.restriction_id = validated_data.get('restriction_id', instance.restriction_id)
#         instance.save()
#         return instance


class PersonSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Person
        # fields = '__all__'
        fields = ('id', 'name', 'date_of_birth', 'biography', 'photo', 'citizenship')


class SrtuctureSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Structure
        fields = '__all__'


class CaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Case
        fields = '__all__'


class OrganisationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Organisation
        fields = '__all__'


class PlaceOfWorkSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = PlaceOfWork
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Article
        fields = '__all__'


class PersecutionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Persecution
        fields = '__all__'


class AiPSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticlesInPersecution
        fields = '__all__'


class RightsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = H_Rights
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = StatusOfVictimInPers
        fields = '__all__'


class ActsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Act
        fields = '__all__'


class ViASerializer(serializers.ModelSerializer):
    class Meta:
        model = ViolationInAct
        fields = '__all__'


class PersonInActSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = PersonInAct
        fields = '__all__'


class DerpivingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Depriving_Liberty
        fields = '__all__'
