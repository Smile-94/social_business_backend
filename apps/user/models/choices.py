from django.db import models


# <<------------------------------------Gender Choices---------------------------------------->>
class GenderChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    UNMENTIONED = "unmentioned", "Unmentioned"


# <<------------------------------------Address Type Choices---------------------------------------->>
class AddressTypeChoices(models.TextChoices):
    HOME = "home", "Home"
    WORK = "work", "Work"
    OTHER = "other", "Other"


# <<------------------------------------User Activity Choices---------------------------------------->>
class UserActivityChoices(models.TextChoices):
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
