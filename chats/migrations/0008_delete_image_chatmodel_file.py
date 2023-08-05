# Generated by Django 4.2.1 on 2023-06-08 13:35

from django.db import migrations, models
import storages.backends.s3boto3


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0007_image_delete_attachment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.AddField(
            model_name='chatmodel',
            name='file',
            field=models.FileField(blank=True, null=True, storage=storages.backends.s3boto3.S3Boto3Storage(), upload_to='chat_files/'),
        ),
    ]