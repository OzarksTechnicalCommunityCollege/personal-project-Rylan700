from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from .models import SpeedRun

class LatestRun(Feed):
    title = 'Latest Speed Runs'
    link = reverse_lazy('speedrun:game_list')
    description = 'Newest verified speed runs.'

    def items(self):
        return SpeedRun.verified_runs.all()[:5]

    def item_title(self, item):
        return f'{item.game} — {item.player.username}'

    def item_description(self, item):
        return (
            f'Time: {item.hours:02}:{item.minutes:02}:'
            f'{item.seconds:02}.{item.milliseconds:03}'
        )

    def item_pubdate(self, item):
        return item.submit_time
