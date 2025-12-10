from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (("admin", "admin"), ("student", "student"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return self.username

class Bus(models.Model):
    bus_number = models.PositiveIntegerField(unique=True)
    bus_name = models.CharField(max_length=200)
    driver_name = models.CharField(max_length=200)
    driver_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Bus {self.bus_number} - {self.bus_name}"

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    full_name = models.CharField(max_length=200)
    student_class = models.CharField(max_length=50)
    pickup_location = models.CharField(max_length=200, blank=True, null=True)
    bus_route = models.CharField(max_length=200)
    monthly_fee = models.PositiveIntegerField(default=0)
    parent_phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    bus_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.full_name} ({self.student_class})"

    def generate_fee_records(self):
        months = [
            "June", "July", "August", "September", "October",
            "November", "December", "January", "February", "March"
        ]
        for month in months:
            FeeRecord.objects.get_or_create(
                student_profile=self,
                month=month,
                defaults={"amount": self.monthly_fee, "status": "unpaid"}
            )

    def save(self, *args, **kwargs):
        creating = self.pk is None
        if self.bus:
            self.bus_number = self.bus.bus_number
        super().save(*args, **kwargs)
        if creating:
            self.generate_fee_records()

class FeeRecord(models.Model):
    STATUS_CHOICES = (
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("pending", "Pending Verification"),
    )

    student_profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="fee_records")
    month = models.CharField(max_length=50)
    amount = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unpaid")
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    payment_screenshot = models.ImageField(upload_to="payment_proofs/", blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unpaid")

    class Meta:
        unique_together = ("student_profile", "month")
        ordering = ["id"]

    def __str__(self):
        return f"{self.student_profile.full_name} - {self.month}"

class PaymentOrder(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="payment_orders")
    fee_record = models.ForeignKey(FeeRecord, on_delete=models.CASCADE, related_name="payment_orders", null=True, blank=True)
    month = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()
    order_id = models.CharField(max_length=255, unique=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default="created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.month} - {self.status}"
