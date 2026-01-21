from django.shortcuts import get_object_or_404, render
from .models import SpeedRun

# View to display a list of verified speed runs
def speed_run_list(request):
    # Get all verified runs, ordered by hours, minutes, seconds, then milliseconds
    runs = SpeedRun.verified_runs.all().order_by('-hours', '-minutes', '-seconds', '-milliseconds')
    
    # Render the list in the template with the runs info
    return render(
        request,
        'speedrun/runs/run_list.html',
        {'runs': runs}
    )

# View to display the details of a speed run
def run_detail(request, id):
    # Retrieve a single verified run by id or return 404 if not found
    run = get_object_or_404(
        SpeedRun,
        id=id,
        verified=SpeedRun.Verified.VERIFIED
    )
    
    # Render the detail in 'run_detail.html' with the run context
    return render(
        request,
        'speedrun/runs/run_detail.html',
        {'run': run}
    )
