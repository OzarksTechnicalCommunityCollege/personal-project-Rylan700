from django.shortcuts import get_object_or_404, render
from .models import SpeedRun

# Create your views here.
def speed_run_list(request):
    runs = SpeedRun.verified_runs.all().order_by('-hours', '-minutes', '-seconds', '-milliseconds')
    return render(
        request,
        'speedrun/runs/run_list.html',
        {'runs': runs}
    )

def run_detail(request, id):
    run = get_object_or_404(
        SpeedRun,
        id = id,
        verified=SpeedRun.Verified.VERIFIED
    )
    return render(
        request,
        'speedrun/runs/run_detail.html',
        {'run': run}
    )

 