from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_add_dummy_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='dummy_mobile',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='휴대폰(익명화)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='dummy_registered_address',
            field=models.TextField(blank=True, null=True, verbose_name='주민등록주소(익명화)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='dummy_residence_address',
            field=models.TextField(blank=True, null=True, verbose_name='실거주지주소(익명화)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='dummy_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='이메일(익명화)'),
        ),
    ]