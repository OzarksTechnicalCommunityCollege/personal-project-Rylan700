from django.shortcuts import get_object_or_404, render
from .models import SpeedRun
from django.views.generic import ListView
from .forms import SubmitRunForm

# ========================
# Class-Based Views
# ========================

# View to display a list of unique verified games
class GameListView(ListView):
    template_name = 'speedrun/games/game_list.html'  # Template to render
    context_object_name = 'games'                     # Context variable for template
    paginate_by = 20                                   # Show 20 games per page

    def get_queryset(self):
        """
        Returns a queryset of unique game names from verified runs,
        ordered alphabetically.
        """
        return SpeedRun.verified_runs.values_list('game', flat=True).distinct().order_by('game')


# View to display all verified runs for a specific game
class SpeedRunListView(ListView):
    template_name = 'speedrun/runs/run_list.html'  # Template to render
    context_object_name = 'runs'                   # Context variable for template
    paginate_by = 20                               # Show 20 runs per page

    def get_queryset(self):
        """
        Returns all verified runs for a given game.
        Orders runs by time: hours -> minutes -> seconds -> milliseconds.
        """
        game_name = self.kwargs['game']  # Get the game name from URL
        return SpeedRun.verified_runs.filter(game=game_name).order_by(
            'hours', 'minutes', 'seconds', 'milliseconds'
        )

# ========================
# Function-Based Views
# ========================

# View to display details of a specific speed run
def run_detail(request, game, player_username, id):
    """
    Retrieves a verified run by game, player, and ID.
    If not found, returns a 404 page.
    """
    run = get_object_or_404(
        SpeedRun,
        game=game,
        player__username=player_username,
        id=id,
        verified=SpeedRun.Verified.VERIFIED  # Only verified runs
    )

    return render(
        request,
        'speedrun/runs/run_detail.html',  # Template to render
        {'run': run}                        # Pass run to template
    )


# TO DO find a way to get players to sign in to that they dont put in a user name

# View to handle submission of a new speed run
def submit_run(request):

    submitted_run = None

    if request.method == "POST":
        form = SubmitRunForm(request.POST, request.FILES)  # Bind data and files
        if form.is_valid():  # Validate form
            submitted_run = form.save(commit=False)  # Create object but don't save yet
            submitted_run.player = request.user     # Assign current user as player
            submitted_run.save()                     # Save to database

            # Render confirmation template with submitted run
            return render(request, 'speedrun/runs/submit_run.html', {
                'submitted_run': submitted_run
            })
    else:
        form = SubmitRunForm()  # Empty form for GET request

    # Render the form template
    return render(
        request,
        'speedrun/runs/includes/submit_run_form.html',
        {'form': form}
    )
