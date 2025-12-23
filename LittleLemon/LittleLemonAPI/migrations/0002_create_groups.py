from django.db import migrations

def create_user_groups(apps):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='managers')
    Group.objects.get_or_create(name='delivery')
    Group.objects.get_or_create(name='customers')

class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_user_groups),
    ]
