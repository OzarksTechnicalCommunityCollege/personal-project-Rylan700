from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import SpeedRun, Profile, Category
from .forms import (
    SubmitRunForm, LoginForm, UserEditForm,
    ProfileEditForm, UserRegistrationForm, CategoryForm
)

# ========================
# Class-Based Views
# ========================

# View to display a list of unique verified games
class GameListView(ListView):
    template_name = 'speedrun/games/game_list.html'
    context_object_name = 'games'
    paginate_by = 5

    def get_queryset(self):
        """
        Returns a queryset of unique game names from verified runs,
        ordered alphabetically.
        """
        return (
            SpeedRun.verified_runs
            .values_list('game', flat=True)
            .distinct()
            .order_by('game')
        )


# View to display all verified runs for a specific game
class SpeedRunListView(ListView):
    template_name = 'speedrun/runs/run_list.html'
    context_object_name = 'runs'
    paginate_by = 5

    def get_queryset(self):
        game_name = self.kwargs['game']

        # Uses manager method instead of repeating filter logic
        return SpeedRun.verified_runs.for_game(game_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add empty category form to context
        context['category_form'] = CategoryForm()

        # Pass game name for template reference
        context['game_name'] = self.kwargs['game']

        return context


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
        verified=SpeedRun.Verified.VERIFIED
    )

    return render(
        request,
        'speedrun/runs/run_detail.html',
        {'run': run}
    )


@login_required
def create_category(request):
    """
    Allows logged-in users to create a new category.
    """
    new_category = None

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            new_category = form.save()
            return render(request, 'speedrun/categories/category_created.html', {
                'new_category': new_category
            })
    else:
        form = CategoryForm()

    return render(request, 'speedrun/categories/create_category.html', {'form': form})


# View to handle submission of a new speed run
@login_required
def submit_run(request):

    submitted_run = None

    if request.method == "POST":
        form = SubmitRunForm(request.POST, request.FILES)

        if form.is_valid():
            submitted_run = form.save(commit=False)

            # Assign current user as player (model enforces this too)
            submitted_run.player = request.user

            submitted_run.save()

            return render(request, 'speedrun/runs/submit_run.html', {
                'submitted_run': submitted_run
            })
    else:
        form = SubmitRunForm()

    return render(
        request,
        'speedrun/runs/includes/submit_run_form.html',
        {'form': form}
    )


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()

    return render(request, 'speedrun/registration/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)

            new_user.set_password(
                user_form.cleaned_data['password']
            )

            new_user.save()

            Profile.objects.create(user=new_user)

            return render(
                request,
                'speedrun/register/register_done.html',
                {'new_user': new_user}
            )
    else:
        user_form = UserRegistrationForm()

    return render(
        request,
        'speedrun/register/register.html',
        {'user_form': user_form}
    )


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )

        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(
        request,
        'speedrun/registration/edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        }
    )


@login_required
def my_runs_dashboard(request):
    runs = SpeedRun.objects.filter(
        player=request.user
    ).order_by('-submit_time')

    return render(
        request,
        'speedrun/runs/my_runs_dashboard.html',
        {'runs': runs}
    )


@require_POST
@login_required
def add_category(request):
    """
    Add a new category via POST and return JSON like user_follow.
    """
    name = request.POST.get('name', '').strip()
    slug = request.POST.get('slug', '').strip()

    if not name:
        return JsonResponse({'status': 'error', 'message': 'Category name is required.'})

    try:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'slug': slug or name.replace(' ', '-').lower()}
        )

        if created:
            return JsonResponse({
                'status': 'ok',
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Category already exists.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})