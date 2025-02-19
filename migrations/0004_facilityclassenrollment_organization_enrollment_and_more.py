# Generated by Django 5.0.6 on 2024-08-18 16:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("enrollment", "0003_alter_activeenrollment_options_and_more"),
        ("facility", "0006_alter_facultyprofile_organization"),
    ]

    operations = [
        migrations.AddField(
            model_name="facilityclassenrollment",
            name="organization_enrollment",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="enrollment.organizationenrollment",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="facilityclassenrollment",
            name="department",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="facility.department"
            ),
        ),
        migrations.AlterField(
            model_name="facilityclassenrollment",
            name="facility_class",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="enrollment.facilityclass",
            ),
        ),
        migrations.AlterField(
            model_name="facilityclassenrollment",
            name="period",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="enrollment.period"
            ),
        ),
    ]
