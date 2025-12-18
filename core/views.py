import json
import hmac
import hashlib
import razorpay

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import StudentProfile, FeeRecord, PaymentOrder, Bus
from .forms import AdminCreateStudentForm, AdminEditStudentForm, BusForm
from .decorators import role_required


def landing_view(request):
    return render(request, "core/index.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if hasattr(user, "student_profile"):
                return redirect("student_dashboard")
            return redirect("admin_dashboard")

        return render(request, "core/login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
@role_required("student")
def student_dashboard(request):
    profile = request.user.student_profile
    records = profile.fee_records.all().order_by("id")
    return render(request, "core/student_dashboard.html", {
        "profile": profile,
        "fee_records": records,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    })


@login_required
@role_required("admin")
def admin_dashboard(request):
    buses = Bus.objects.all().order_by("bus_number")
    return render(request, "core/admin_dashboard.html", {"buses": buses})


@login_required
@role_required("admin")
def admin_bus_list(request):
    buses = Bus.objects.all().order_by("bus_number")
    return render(request, "core/admin_bus_list.html", {"buses": buses})


@login_required
@role_required("admin")
def admin_add_bus(request):
    if request.method == "POST":
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_bus_list")
    else:
        form = BusForm()
    return render(request, "core/admin_add_bus.html", {"form": form})


@login_required
@role_required("admin")
def admin_bus_students(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    students = StudentProfile.objects.filter(bus=bus).order_by("full_name")
    return render(request, "core/admin_bus_students.html", {
        "bus": bus,
        "students": students
    })


@login_required
@role_required("admin")
def admin_add_student(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    if request.method == "POST":
        form = AdminCreateStudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.bus = bus
            student.bus_number = bus.bus_number
            student.save()
            return redirect("admin_bus_students", bus_id=bus.id)
    else:
        form = AdminCreateStudentForm()

    return render(request, "core/admin_add_student.html", {
        "form": form,
        "bus": bus
    })


@login_required
@role_required("admin")
def admin_edit_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)

    if request.method == "POST":
        form = AdminEditStudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect("admin_bus_students", bus_id=student.bus.id)
    else:
        form = AdminEditStudentForm(instance=student)

    return render(request, "core/admin_edit_student.html", {
        "form": form,
        "student": student
    })


@login_required
@role_required("admin")
def admin_delete_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    bus_id = student.bus.id

    if request.method == "POST":
        student.user.delete()
        return redirect("admin_bus_students", bus_id=bus_id)

    return render(request, "core/admin_delete_confirm.html", {
        "student": student,
        "bus_id": bus_id
    })


@login_required
@role_required("admin")
def admin_view_student_fees(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    fees = student.fee_records.all().order_by("id")
    return render(request, "core/admin_student_fees.html", {
        "student": student,
        "fee_records": fees
    })


@login_required
@role_required("admin")
def admin_fee_update(request, student_id, record_id):
    record = get_object_or_404(FeeRecord, id=record_id)

    if request.method == "POST":
        status = request.POST.get("status")
        record.status = status

        if status == "paid":
            record.payment_date = timezone.now()
            record.verification_status = "paid"
        else:
            record.payment_date = None
            record.verification_status = "unpaid"

        record.save()
        return redirect("admin_view_student_fees", student_id=student_id)

    return render(request, "core/admin_fee_update.html", {
        "record": record
    })


@login_required
@role_required("student")
def create_razorpay_order(request):
    data = json.loads(request.body.decode("utf-8"))
    amount = data.get("amount")
    month = data.get("month")

    profile = request.user.student_profile
    record = FeeRecord.objects.filter(student_profile=profile, month=month).first()

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    order = client.order.create({
        "amount": int(amount) * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    PaymentOrder.objects.create(
        student=profile,
        fee_record=record,
        month=month,
        amount=amount,
        order_id=order["id"],
        status="created"
    )

    return JsonResponse({
        "order_id": order["id"],
        "key": settings.RAZORPAY_KEY_ID
    })


@login_required
@role_required("student")
def verify_payment(request):
    data = json.loads(request.body.decode("utf-8"))
    order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")

    order = PaymentOrder.objects.get(order_id=order_id)

    order.payment_id = payment_id
    order.signature = signature
    order.status = "paid"
    order.save()

    record = order.fee_record
    record.status = "paid"
    record.payment_date = timezone.now()
    record.transaction_id = payment_id
    record.verification_status = "paid"
    record.save()

    return JsonResponse({"status": "success"})


@csrf_exempt
def razorpay_webhook(request):
    body = request.body
    received = request.META.get("HTTP_X_RAZORPAY_SIGNATURE", "")
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(received, expected):
        return HttpResponseForbidden()

    return HttpResponse(status=200)
