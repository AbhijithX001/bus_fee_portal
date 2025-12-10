from django import forms
from django.contrib.auth import get_user_model
from .models import StudentProfile, Bus

User = get_user_model()


class AdminCreateStudentForm(forms.ModelForm):
    username = forms.CharField(max_length=150)

    class Meta:
        model = StudentProfile
        fields = [
            "username",
            "full_name",
            "student_class",
            "pickup_location",
            "bus_route",
            "monthly_fee",
            "parent_phone_number",
            "address",
        ]

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")

        return username

    def save(self, commit=True):
        username = self.cleaned_data["username"]

        user = User.objects.create_user(
            username=username,
            password="password123",
            role="student"
        )

        student = super().save(commit=False)
        student.user = user

        if commit:
            student.save()
        return student


class AdminEditStudentForm(forms.ModelForm):
    username = forms.CharField(max_length=150)

    class Meta:
        model = StudentProfile
        fields = [
            "full_name",
            "student_class",
            "pickup_location",
            "bus_route",
            "monthly_fee",
            "parent_phone_number",
            "address",
        ]

    def __init__(self, *args, **kwargs):
        student = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        if student:
            self.fields["username"].initial = student.user.username

    def clean_username(self):
        new_username = self.cleaned_data["username"]

        qs = User.objects.filter(username=new_username)
        if qs.exists() and qs.first().id != self.instance.user.id:
            raise forms.ValidationError("This username is already taken.")

        return new_username

    def save(self, commit=True):
        student = super().save(commit=False)
        new_username = self.cleaned_data["username"]

        student.user.username = new_username
        student.user.save()

        if commit:
            student.save()
        return student


class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ["bus_number", "bus_name", "driver_name", "driver_phone"]
