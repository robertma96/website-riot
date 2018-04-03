from django.db import models
from datetime import datetime

# Create your models here.


class Posts(models.Model):
    region_abrevations = (
        ('eun1', 'EUNE'),
        ('euw1', 'EUW'),
        ('na1', 'NA'),
    )

    summoner_name = models.CharField(max_length=16, blank=False)
    region = models.CharField(max_length=4, choices=region_abrevations)
    accountID = models.IntegerField(default=0)
    summonerID = models.IntegerField(default=0)
    gamesPlayed = models.TextField()
    championsPlayed = models.TextField()
    created_at = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.summoner_name

    class Meta:
        verbose_name_plural = "Posts"
