# Generated by Django 5.0.6 on 2024-12-06 01:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("enrollment", "0007_alter_facilityclassenrollment_facility_class_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="facilityenrollment",
            name="end",
            field=models.DateField(verbose_name="End Date"),
        ),
        migrations.AlterField(
            model_name="facilityenrollment",
            name="start",
            field=models.DateField(verbose_name="Start Date"),
        ),
        migrations.AlterField(
            model_name="factionenrollment",
            name="end",
            field=models.DateField(verbose_name="End Date"),
        ),
        migrations.AlterField(
            model_name="factionenrollment",
            name="start",
            field=models.DateField(verbose_name="Start Date"),
        ),
        migrations.AlterField(
            model_name="leaderenrollment",
            name="end",
            field=models.DateField(verbose_name="End Date"),
        ),
        migrations.AlterField(
            model_name="leaderenrollment",
            name="start",
            field=models.DateField(verbose_name="Start Date"),
        ),
        migrations.AlterField(
            model_name="organizationenrollment",
            name="end",
            field=models.DateField(verbose_name="End Date"),
        ),
        migrations.AlterField(
            model_name="organizationenrollment",
            name="start",
            field=models.DateField(verbose_name="Start Date"),
        ),
        migrations.AlterField(
            model_name="period",
            name="end",
            field=models.TimeField(verbose_name="End Time"),
        ),
        migrations.AlterField(
            model_name="period",
            name="start",
            field=models.TimeField(verbose_name="Start Time"),
        ),
        migrations.AlterField(
            model_name="week",
            name="end",
            field=models.DateField(verbose_name="End Date"),
        ),
        migrations.AlterField(
            model_name="week",
            name="start",
            field=models.DateField(verbose_name="Start Date"),
        ),
    ]
