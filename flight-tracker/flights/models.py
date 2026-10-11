from django.db import models


class FlightSearchQuery(models.Model):
    """Stores recent flight number lookups made by users."""
    flight_number = models.CharField(max_length=32, db_index=True)
    results_count = models.PositiveIntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
        verbose_name = 'Flight Search Query'
        verbose_name_plural = 'Flight Search Queries'

    def __str__(self) -> str:
        return f"{self.flight_number} ({self.results_count} matches)"
