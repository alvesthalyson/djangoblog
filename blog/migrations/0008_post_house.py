from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_post_video_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='house',
            field=models.CharField(blank=True, choices=[('g', 'Gryffindor'), ('s', 'Slytherin'), ('h', 'Hufflepuff'), ('r', 'Ravenclaw')], default='', max_length=1),
        ),
    ]
