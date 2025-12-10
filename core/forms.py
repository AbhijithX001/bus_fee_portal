from django import forms
from .models import StudentProfile, User

class AdminCreateStudentForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

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

    def save(self, commit=True, bus_number=None):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            role="student"
        )
        student = super().save(commit=False)
        student.user = user
        if bus_number is not None:
            student.bus_number = bus_number
        if commit:
            student.save()
        return student
