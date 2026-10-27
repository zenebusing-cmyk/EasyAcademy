
from django.db import models

class School(models.Model):

    name = models.CharField(max_length=200)

    school_code = models.CharField(
        max_length=50,
        unique=True
    )

    address = models.TextField()

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    school = models.ForeignKey(
    "School",
    on_delete=models.PROTECT,
    related_name="students",
    null=True,
    blank=True
)

    admission_number = models.CharField(
        max_length=50,
        unique=True
    )

    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)

    student_class = models.CharField(max_length=20)
    section = models.CharField(max_length=10)
    roll_number = models.PositiveIntegerField()

    mobile = models.CharField(max_length=15)
    address = models.TextField()

    transport = models.BooleanField(default=False)

    transport_area = models.ForeignKey(
        "TransportArea",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class_fee = models.ForeignKey(
        "ClassFee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    PAYMENT_FREQUENCY_CHOICES = [
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        default="monthly",
    )


    admission_date = models.DateField()

    total_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def save(self, *args, **kwargs):
        total = 0

        if self.class_fee:
            total += self.class_fee.monthly_fee

        if self.transport and self.transport_area:
            total += self.transport_area.monthly_fee

        self.total_fee = total

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FeePayment(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="fee_payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateField()
    month = models.CharField(max_length=20)

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("Cash", "Cash"),
            ("UPI", "UPI"),
            ("Bank", "Bank"),
        ]
    )

    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last_payment = FeePayment.objects.order_by(
                "-id"
            ).first()

            number = last_payment.id + 1 if last_payment else 1

            self.receipt_number = (
                f"REC-{self.payment_date.year}-{number:04d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.receipt_number



class TransportArea(models.Model):

    area_name = models.CharField(
        max_length=100,
        unique=True
    )

    distance_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.area_name



class ClassFee(models.Model):

    class_name = models.CharField(
        max_length=50,
        unique=True
    )

    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.class_name


from django.contrib.auth.models import User


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("faculty", "Faculty"),
        ("student", "Student"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="user_profiles"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class StudentFeeCharge(models.Model):
    FEE_TYPES = [
        ("admission", "Admission Fee"),
        ("registration", "Registration Fee"),
        ("tuition", "Tuition Fee"),
        ("annual", "Annual Fee"),
        ("exam", "Examination Fee"),
        ("transport", "Transport Fee"),
    ]

    BILLING_PERIODS = [
        ("one_time", "One Time"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
        ("installment", "Installment"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="fee_charges",
    )

    fee_type = models.CharField(
        max_length=20,
        choices=FEE_TYPES,
    )

    billing_period = models.CharField(
        max_length=20,
        choices=BILLING_PERIODS,
    )

    description = models.CharField(max_length=200)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    academic_year = models.CharField(
        max_length=9,
        blank=True,
    )

    due_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.description} - {self.amount}"

    
    @property
    def amount_paid(self):
        return self.allocations.aggregate(
            total=models.Sum("amount")
        )["total"] or 0

    @property
    def balance(self):
        return self.amount - self.amount_paid


class FeePaymentAllocation(models.Model):
    payment = models.ForeignKey(
        FeePayment,
        on_delete=models.PROTECT,
        related_name="allocations",
    )

    fee_charge = models.ForeignKey(
        StudentFeeCharge,
        on_delete=models.PROTECT,
        related_name="allocations",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    allocated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.payment.receipt_number} - "
            f"{self.fee_charge.description} - "
            f"{self.amount}"
        )


class AcademicSession(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="academic_sessions",
    )

    name = models.CharField(max_length=9)

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class SessionFeeSetting(models.Model):
   
    FEE_TYPES = [
        ("admission", "Admission Fee"),
        ("registration", "Registration Fee"),
        ("tuition", "Tuition Fee"),
        ("annual", "Annual Fee"),
        ("exam", "Examination Fee"),
        ("transport", "Transport Fee"),
    ]

    BILLING_OPTIONS = [
        ("one_time", "One Time"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
        ("installment", "Installments"),
        ("per_exam", "Per Examination"),
    ]

    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="fee_settings",
    )

    fee_type = models.CharField(
        max_length=20,
        choices=FEE_TYPES,
    )

    class_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Leave blank if this fee applies to every class.",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    billing_option = models.CharField(
        max_length=20,
        choices=BILLING_OPTIONS,
        default="one_time",
    )

    installment_count = models.PositiveSmallIntegerField(
        default=1,
    )

    def __str__(self):
        return (
            f"{self.session.name} - "
            f"{self.get_fee_type_display()} - ₹{self.amount}"
        )

