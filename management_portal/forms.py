from django import forms

class SearchForm(forms.Form):
    search_word = forms.CharField(
        label       = 'Globale Suche',
        min_length  = 3,
        max_length  = 64,
    )
