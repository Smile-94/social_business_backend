from django.db import models


# <<------------------------------------Active Status Choices---------------------------------------->>
class ActiveStatusChoices(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
