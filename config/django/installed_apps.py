from pydantic import computed_field

from config.django._base_config import DjangoConfig
from config.environment import EnvironmentChoices, env_config


class InstalledAppsConfig(DjangoConfig):
    """
    Assembles INSTALLED_APPS in strict loading order.

    Dev-only apps (debug_toolbar) are conditionally injected based on
    environment — they are never loaded in staging or production.
    """

    THIRD_PARTY_APPS: list[str] = [
        "rest_framework_simplejwt",
        "rangefilter",
        "django_filters",
        "rest_framework",
        "drf_spectacular",
        "drf_spectacular_sidecar",
        "corsheaders",
    ]

    SHARED_APPS: list[str] = [
        "django_tenants",
        "apps.tenant.apps.TenantConfig",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "apps.common.apps.CommonConfig",
        "apps.user.apps.UserConfig",
        "apps.authentication.apps.AuthenticationConfig",
        "apps.subscription.apps.SubscriptionConfig",
        "apps.payment.apps.PaymentConfig",
        *THIRD_PARTY_APPS,
    ]

    TENANT_APPS: list[str] = [
        "django.contrib.contenttypes",
        "apps.business.apps.BusinessConfig",
        "apps.product.apps.ProductConfig",
        "apps.order.apps.OrderConfig",
        "apps.purchase.apps.PurchaseConfig",
        "apps.return.apps.ReturnConfig",
        "apps.warehouse.apps.WarehouseConfig",
        "apps.report.apps.ReportConfig",
        "apps.dashboard.apps.DashboardConfig",
        "apps.stock.apps.StockConfig",
        "apps.employee.apps.EmployeeConfig",
        "apps.payroll.apps.PayrollConfig",
        "apps.expense.apps.ExpenseConfig",
        "apps.earning.apps.EarningConfig",
    ]

    @computed_field
    def INSTALLED_APPS(self) -> list[str]:
        """
        Assemble the final INSTALLED_APPS list.

        debug_toolbar is injected only for LOCAL and DEVELOPMENT environments,
        guaranteeing it never appears in STAGING or PRODUCTION.
        """
        apps = list(self.SHARED_APPS) + [app for app in self.TENANT_APPS if app not in self.SHARED_APPS]

        if env_config.ENVIRONMENT in (EnvironmentChoices.LOCAL, EnvironmentChoices.DEVELOPMENT):
            apps.append("debug_toolbar")

        return apps

    def as_django_settings(self) -> dict:
        return {
            "INSTALLED_APPS": self.INSTALLED_APPS,
            "SHARED_APPS": self.SHARED_APPS,
            "TENANT_APPS": self.TENANT_APPS,
        }


installed_apps_config = InstalledAppsConfig()
