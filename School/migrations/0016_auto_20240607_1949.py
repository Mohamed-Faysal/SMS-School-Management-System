from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('School', '0015_studentteachermessage_delete_studentteachermessages'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StudentTeacherMessage',
        ),
    ]
