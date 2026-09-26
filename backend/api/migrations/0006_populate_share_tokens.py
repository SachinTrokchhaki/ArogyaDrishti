from django.db import migrations
import uuid


def populate_share_tokens(apps, schema_editor):
    """Give every existing report a unique share token."""
    MedicalReport = apps.get_model('api', 'MedicalReport')
    for report in MedicalReport.objects.filter(share_token__isnull=True):
        report.share_token = uuid.uuid4()
        report.save(update_fields=['share_token'])


def reverse_populate(apps, schema_editor):
    """Reverse operation — clear share tokens."""
    MedicalReport = apps.get_model('api', 'MedicalReport')
    MedicalReport.objects.update(share_token=None)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_medicalreport_share_token'),
    ]

    operations = [
        migrations.RunPython(populate_share_tokens, reverse_populate),
    ]