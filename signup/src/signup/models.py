from django.db import models


class User(models.Model):
    """ ユーザ情報を表現することを責務に持つ """
    username = models.CharField(max_length=255)

    def __eq__(self, other: 'User'):
        return self.username == other.username
