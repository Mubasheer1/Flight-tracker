from django.contrib import admin
from .models import FlightSearchQuery


@admin.register(FlightSearchQuery)
class FlightSearchQueryAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'results_count', 'searched_at')
    search_fields = ('flight_number',)
    list_filter = ('searched_at',)
