from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# ─────────────────────────────────────────────
#  Skill  (e.g. "Python", "Django", "UI Design")
# ─────────────────────────────────────────────
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
#  Artifact  — proof uploaded by a contributor
# ─────────────────────────────────────────────
class Artifact(models.Model):

    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Who uploaded this proof
    contributor = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='artifacts')

    # Which skill is being proved
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    # A short title like "My Django Portfolio Project"
    title = models.CharField(max_length=200)

    # The actual uploaded file (PDF, image, etc.)
    file = models.FileField(upload_to='artifacts/')

    # Current review status
    status = models.CharField(max_length=10,
                               choices=STATUS_CHOICES,
                               default='pending')

    # When it was submitted
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.contributor.username} [{self.status}]"

    # Convenience — count how many people approved this
    def approve_count(self):
        return self.votes.filter(vote='approve').count()

    # Convenience — count how many people rejected this
    def reject_count(self):
        return self.votes.filter(vote='reject').count()

    def recalculate_status(self):
        """
        Updates the status based on current vote counts. 
        Threshold is 2 votes in either direction.
        """
        old_status = self.status
        if self.approve_count() >= 2:
            self.status = 'approved'
        elif self.reject_count() >= 2:
            self.status = 'rejected'
        else:
            self.status = 'pending'
        
        if self.status != old_status:
            self.save()


# ─────────────────────────────────────────────
#  Vote  — a verifier's decision on an artifact
# ─────────────────────────────────────────────
class Vote(models.Model):

    VOTE_CHOICES = [
        ('approve', 'Approve'),
        ('reject',  'Reject'),
    ]

    artifact = models.ForeignKey(Artifact, on_delete=models.CASCADE,
                                  related_name='votes')
    voter    = models.ForeignKey(User, on_delete=models.CASCADE)
    vote     = models.CharField(max_length=10, choices=VOTE_CHOICES)
    voted_at = models.DateTimeField(auto_now_add=True)

    # One person can only vote once per artifact
    class Meta:
        unique_together = ('artifact', 'voter')

    def __str__(self):
        return f"{self.voter.username} → {self.vote} on '{self.artifact.title}'"


# ─────────────────────────────────────────────
#  SIGNALS  — trigger status recalculation
# ─────────────────────────────────────────────
@receiver(post_save, sender=Vote)
@receiver(post_delete, sender=Vote)
def update_artifact_status(sender, instance, **kwargs):
    """Whenever a vote is cast or changed, re-check the artifact status."""
    instance.artifact.recalculate_status()