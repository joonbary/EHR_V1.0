from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='dummy_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='이름(익명화)'),
        ),
    ]