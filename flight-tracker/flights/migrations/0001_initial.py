# Generated initial migration for FlightSearchQuery
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FlightSearchQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_number', models.CharField(db_index=True, max_length=32)),
                ('results_count', models.PositiveIntegerField(default=0)),
                ('searched_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Flight Search Query',
                'verbose_name_plural': 'Flight Search Queries',
                'ordering': ['-searched_at'],
            },
        ),
    ]
