
from django.contrib import admin
from .models import (
    School,
    Student,
    FeePayment,
    TransportArea,
    ClassFee,
    UserProfile,
    StudentFeeCharge,
    FeePaymentAllocation,
    AcademicSession,
    SessionFeeSetting,
)

admin.site.register(School)
admin.site.register(Student)
admin.site.register(FeePayment)
admin.site.register(TransportArea)
admin.site.register(ClassFee)
admin.site.register(UserProfile)

admin.site.register(AcademicSession)
admin.site.register(SessionFeeSetting)


@admin.register(StudentFeeCharge)
class StudentFeeChargeAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "fee_type",
        "billing_period",
        "amount",
        "amount_paid",
        "balance",
        "due_date",
        "academic_year",
    )

    list_filter = ("fee_type", "billing_period", "academic_year")
    search_fields = (
        "student__name",
        "student__admission_number",
        "description",
    )
    ordering = ("due_date",)


@admin.register(FeePaymentAllocation)
class FeePaymentAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "payment",
        "fee_charge",
        "amount",
        "allocated_at",
    )

    search_fields = (
        "payment__receipt_number",
        "fee_charge__student__name",
        "fee_charge__description",
    )


