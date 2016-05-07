from dal import autocomplete
from django import forms

from recipes.models import Month, Note, RecipeUser, Text


class MenuNoteForm(forms.ModelForm):
    title = forms.ModelChoiceField(
        queryset=Note.objects.all(),
        widget=autocomplete.ModelSelect2(url='note-autocomplete')
    )

    class Meta:
        model = Note
        fields = ['title']
