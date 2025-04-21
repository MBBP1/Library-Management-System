from django import forms
from .models import Book, Member, BorrowRecord

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'
        exclude = ['user']  # Exclude user field to avoid manual entry

class BorrowForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = ['member', 'due_date']  # Only allow member and due date to be entered manually
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),  # Use date input for due date
        }