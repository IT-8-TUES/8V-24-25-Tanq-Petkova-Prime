from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Firm(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_firms")
    description = models.TextField(null=True)


class FirmMembership(models.Model):
    firm   = models.ForeignKey(Firm, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    joined = models.DateTimeField(auto_now_add=True)

class Tasks(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    contents = models.TextField(null=True)
    
    user_details = models.ForeignKey(FirmMembership, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ("unstarted", "Unstarted"),
        ("pending", "Pending"),
        ("complete", "Complete"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="unstarted",
    )

class Invites(models.Model):
    send_to = models.ForeignKey(User, on_delete=models.CASCADE)
    send_from = models.ForeignKey(User, on_delete=models.CASCADE)