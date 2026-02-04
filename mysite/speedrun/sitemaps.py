from django.contrib.sitemaps import Sitemap
from .models import SpeedRun

class SpeedRunsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9
    def items(self):
        return SpeedRun.verified_runs.all()
    def lastmod(self, obj):
        return obj.updated_time
