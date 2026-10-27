from django import forms
from .models import Student, FeePayment, StudentFeeCharge, FeePaymentAllocation



class StudentForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            "admission_number",
            "name",
            "father_name",
            "mother_name",
            "student_class",
            "section",
            "roll_number",
            "mobile",
            "address",
            "transport",
            "transport_area",
            "class_fee",
            "admission_date",
            "payment_frequency",
        ]

        widgets = {
            "admission_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        transport = cleaned_data.get("transport")
        transport_area = cleaned_data.get("transport_area")

        if transport and not transport_area:
            self.add_error(
                "transport_area",
                "Select a transport area when transport is enabled."
            )

        if not transport:
            cleaned_data["transport_area"] = None

        return cleaned_data


class FeePaymentForm(forms.ModelForm):

    class Meta:
        model = FeePayment

        fields = [
            "amount",
            "payment_date",
            "month",
            "payment_method",
        ]

        widgets = {
            "payment_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }


class FeeChargeSelectionForm(forms.Form):
    fee_charge = forms.ModelChoiceField(
        queryset=StudentFeeCharge.objects.none(),
        label="Fee charge",
        empty_label="Select a fee charge",
    )

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)

        if student is not None:
            self.fields["fee_charge"].queryset = (
                StudentFeeCharge.objects.filter(student=student)
                .order_by("due_date")
            )
