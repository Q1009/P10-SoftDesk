from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

MIN_AGE = 15


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "date_of_birth",
            "can_be_contacted",
            "can_data_be_shared",
        ]

    def validate_date_of_birth(self, value):
        today = date.today()
        age = (
            today.year
            - value.year
            - ((today.month, today.day) < (value.month, value.day))
        )
        if age < MIN_AGE:
            raise serializers.ValidationError(
                f"Vous devez avoir au moins {MIN_AGE} ans pour vous inscrire (RGPD)."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "date_of_birth",
            "can_be_contacted",
            "can_data_be_shared",
        ]
        read_only_fields = ["id"]
