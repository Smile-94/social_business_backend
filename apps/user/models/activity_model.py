from django.db import models

from apps.common.models.common_models import BaseModel, TimeStampedModel, UserStampModel
from apps.user.models.choices import UserActivityChoices


# <<--------------------------------- Activity Model ----------------------->>
class UserActivity(BaseModel, UserStampModel, TimeStampedModel):
    activity_type = models.CharField(
        max_length=255, choices=UserActivityChoices.choices, default=UserActivityChoices.CREATE.value
    )
    activity_name = models.CharField(max_length=255, null=True, blank=True)
    action_model = models.CharField(max_length=255, null=True, blank=True)
    action_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = "user"
        db_table = "user_activity"
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"

    def __str__(self):
        return f"{self.activity_type}({self.pk})"

    def __repr__(self):
        return f"{self.activity_type}({self.pk})"
