from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import Artifact, Skill, Vote
from .forms import RegisterForm, ArtifactForm


# ─────────────────────────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────────────────────────
def home(request):
    return render(request, 'core/home.html')


# ─────────────────────────────────────────────────────────────
#  REGISTER
# ─────────────────────────────────────────────────────────────
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created! Welcome to VerifyHub.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


# ─────────────────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


# ─────────────────────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('home')


# ─────────────────────────────────────────────────────────────
#  DASHBOARD  — shows the logged-in user's own artifacts
# ─────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    # My uploaded artifacts
    my_artifacts = Artifact.objects.filter(contributor=request.user).order_by('-submitted_at')

    # Skills where I have at least one APPROVED artifact  → I can verify others
    my_verified_skills = Skill.objects.filter(
        artifact__contributor=request.user,
        artifact__status='approved'
    ).distinct()

    return render(request, 'core/dashboard.html', {
        'my_artifacts':       my_artifacts,
        'my_verified_skills': my_verified_skills,
    })


# ─────────────────────────────────────────────────────────────
#  UPLOAD ARTIFACT
# ─────────────────────────────────────────────────────────────
@login_required
def upload_artifact(request):
    if request.method == 'POST':
        form = ArtifactForm(request.POST, request.FILES)
        if form.is_valid():
            artifact = form.save(commit=False)
            artifact.contributor = request.user
            artifact.status = 'pending'
            artifact.save()
            messages.success(request, 'Artifact submitted! It is now in the review queue.')
            return redirect('dashboard')
    else:
        form = ArtifactForm()
    return render(request, 'core/upload_artifact.html', {'form': form})


# ─────────────────────────────────────────────────────────────
#  REVIEW QUEUE
#  Shows pending artifacts for skills where the current user
#  is already verified (has an approved artifact for that skill)
# ─────────────────────────────────────────────────────────────
@login_required
def review_queue(request):
    # Skills where the logged-in user is verified
    verified_skill_ids = Artifact.objects.filter(
        contributor=request.user,
        status='approved'
    ).values_list('skill_id', flat=True)

    # Pending artifacts in those skills, submitted by OTHERS
    # Also exclude artifacts the current user already voted on
    already_voted = Vote.objects.filter(voter=request.user).values_list('artifact_id', flat=True)

    pending_artifacts = Artifact.objects.filter(
        skill_id__in=verified_skill_ids,
        status='pending'
    ).exclude(
        contributor=request.user
    ).exclude(
        id__in=already_voted
    ).order_by('submitted_at')

    return render(request, 'core/review_queue.html', {
        'pending_artifacts': pending_artifacts,
    })


# ─────────────────────────────────────────────────────────────
#  VOTE  (called via AJAX from the review queue page)
#  Expects:  POST  { artifact_id, vote: 'approve'|'reject' }
#  Returns:  JSON  { success, approve_count, reject_count, new_status }
# ─────────────────────────────────────────────────────────────
@login_required
def vote(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})

    artifact_id = request.POST.get('artifact_id')
    vote_value  = request.POST.get('vote')           # 'approve' or 'reject'

    if vote_value not in ('approve', 'reject'):
        return JsonResponse({'success': False, 'error': 'Invalid vote'})

    artifact = get_object_or_404(Artifact, id=artifact_id)

    # Prevent self-voting
    if artifact.contributor == request.user:
        return JsonResponse({'success': False, 'error': 'Cannot vote on your own artifact'})

    # Create or update the vote (one vote per user per artifact)
    vote_obj, created = Vote.objects.update_or_create(
        artifact=artifact,
        voter=request.user,
        defaults={'vote': vote_value}
    )

    # The status is now automatically updated via signals in models.py
    artifact.refresh_from_db()

    return JsonResponse({
        'success':       True,
        'approve_count': artifact.approve_count(),
        'reject_count':  artifact.reject_count(),
        'new_status':    artifact.status,
    })


# ─────────────────────────────────────────────────────────────
#  PUBLIC PROFILE  — anyone can view a user's verified skills
# ─────────────────────────────────────────────────────────────
def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Only show APPROVED artifacts
    approved_artifacts = Artifact.objects.filter(
        contributor=profile_user,
        status='approved'
    ).select_related('skill')

    # Build data for Chart.js Skill Radar
    # Count how many approved artifacts per skill
    skill_counts = {}
    for artifact in approved_artifacts:
        skill_name = artifact.skill.name
        skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1

    chart_labels = list(skill_counts.keys())
    chart_data   = list(skill_counts.values())

    return render(request, 'core/public_profile.html', {
        'profile_user':       profile_user,
        'approved_artifacts': approved_artifacts,
        'chart_labels':       chart_labels,
        'chart_data':         chart_data,
    })

def create_super(request):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'changeme123')
        return HttpResponse('Superuser created')
    return HttpResponse('Already exists')