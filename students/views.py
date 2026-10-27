from django.shortcuts import render, redirect
from .forms import StudentForm, FeePaymentForm
from .models import (Student, FeePayment, ClassFee, UserProfile, TransportArea, StudentFeeCharge, FeePaymentAllocation, AcademicSession, SessionFeeSetting)
from django.contrib.auth import authenticate, login
from django.contrib import messages 
from django.db import models
from datetime import date
from decimal import Decimal

def home(request):
    return render(request, "students/home.html")


def add_student(request):

    if request.method == "POST":

        form = StudentForm(request.POST)

        if form.is_valid():

            student = form.save(commit=False)

            # Find the fee for the student's class
            class_fee = ClassFee.objects.filter(
                class_name=student.student_class
            ).first()

            if class_fee:
                student.class_fee = class_fee

            # Calculate the monthly fee
            total = 0

            if class_fee:
                total += class_fee.monthly_fee

            # Add transport fee only if transport is selected
            if student.transport and student.transport_area:
                total += student.transport_area.monthly_fee

            student.total_fee = total

            student.save()

        messages.success(request, "Student has been saved successfully!")
        return redirect("add_student")

    else:

        form = StudentForm()

    return render(
        request,
        "students/add_student.html",
        {"form": form}
    )

def student_success(request):
    return render(
        request,
        "students/student_success.html"
        
    )
def student_list(request):
    students = Student.objects.all()

    return render(
        request,
        "students/student_list.html",
        {"students": students}
    )

def add_fee(request, student_id):

    student = Student.objects.get(id=student_id)

    if request.method == "POST":

        form = FeePaymentForm(request.POST)

        if form.is_valid():

            payment = form.save(commit=False)

            payment.student = student

            payment.save()

            return redirect(
                "fee_success",
                payment_id=payment.id
            )

    else:

        form = FeePaymentForm()

    return render(
        request,
        "students/add_fee.html",
        {
            "form": form,
            "student": student
        }
    )

def student_detail(request, student_id):

    student = Student.objects.get(id=student_id)

    payments = student.fee_payments.all().order_by("-payment_date")
    total_paid = sum(payment.amount for payment in payments)
    due_fee = student.total_fee - total_paid
    if due_fee <= 0:
        fee_status = "PAID"
    elif total_paid > 0:
        fee_status = "PARTIALLY PAID"
    else:
        fee_status = "DUE"

    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "payments": payments,
            "total_paid": total_paid,
            "due_fee": due_fee,
            "fee_status": fee_status,
        }
    )

def fee_success(request, payment_id):

    payment = FeePayment.objects.get(id=payment_id)

    return render(
        request,
        "students/fee_success.html",
        {
            "payment": payment
        }
    )
def fee_reminders(request):

    students = Student.objects.all()

    reminder_students = []

    for student in students:

        payments = student.fee_payments.all()

        total_paid = sum(
            payment.amount for payment in payments
        )

        due_fee = student.total_fee - total_paid

        if due_fee > 0:

            reminder_students.append({
                "student": student,
                "total_paid": total_paid,
                "due_fee": due_fee,
            })

    return render(
        request,
        "students/fee_reminders.html",
        {
            "students": reminder_students
        }
    )
def login_choice(request):
    return render(
        request,
        "students/login_choice.html"
    )

def role_login(request, role):
    if role not in ["student", "faculty", "admin"]:
        return redirect("login_choice")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                messages.error(
                    request,
                    "Your account has no user profile. Contact the administrator."
                )
                return redirect("role_login", role=role)

            if profile.role != role:
                messages.error(
                    request,
                    "You are not authorized to log in with this account type."
                )
                return redirect("role_login", role=role)

            if role == "admin" and not user.is_staff:
                messages.error(
                    request,
                    "You do not have admin access."
                )
                return redirect("role_login", role=role)

            login(request, user)

            if role == "admin":
                return redirect("admin_dashboard")

            messages.success(
                request,
                "Login successful. Your role has been verified."
            )
            return redirect("student_list")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "students/role_login.html",
        {"role": role}
    )

from django.contrib.auth.decorators import login_required



@login_required
def admin_dashboard(request):
    total_students = Student.objects.count()

    total_fees_collected = (
        FeePayment.objects.aggregate(
            total=models.Sum("amount")
        )["total"] or 0
    )

    return render(
        request,
        "students/admin_dashboard.html",
        {
            "total_students": total_students,
            "total_fees_collected": total_fees_collected,
        }
    )
@login_required
def admin_student_list(request):
    students = Student.objects.all().order_by("name")

    return render(
        request,
        "students/admin_student_list.html",
        {
            "students": students,
            "total_students": students.count(),
        }
    )