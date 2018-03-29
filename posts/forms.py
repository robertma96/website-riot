from django.forms import ModelForm
from .models import Posts

region_abrevations = (
    ('EUNE', 'eun1'),
    ('EUW', 'euw1'),
    ('NA', 'na1'),
)


class PostsForm(ModelForm):
    class Meta:
        model = Posts
        fields = ['summoner_name', 'region']
