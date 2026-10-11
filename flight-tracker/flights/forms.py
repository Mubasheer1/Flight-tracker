from django import forms


class FlightSearchForm(forms.Form):
    flight_number = forms.CharField(
        label='Flight Number / Callsign',
        max_length=24,
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter flight number (e.g., BA117, BAW117, UA901, DLH400, AA100)...',
                'class': 'search-input',
                'autocomplete': 'off',
                'autofocus': 'autofocus',
                'id': 'flight-number-input',
            }
        ),
    )

    def clean_flight_number(self) -> str:
        value = (self.cleaned_data.get('flight_number') or '').strip().upper()
        return value
