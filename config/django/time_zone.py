from pydantic import Field

from config.django._base_config import DjangoConfig


class TimeZoneConfig(DjangoConfig):
    """
    Internationalization (i18n) and Time Zone configuration loaded via Pydantic.
    Ensures consistent temporal data handling across distributed workers.
    """

    LANGUAGE_CODE: str = Field(default="en-us")
    USE_I18N: bool = Field(default=True)

    TIME_ZONE: str = Field(default="UTC")
    USE_TZ: bool = Field(default=True)

    def as_django_settings(self) -> dict:
        return {
            "LANGUAGE_CODE": self.LANGUAGE_CODE,
            "USE_I18N": self.USE_I18N,
            "TIME_ZONE": self.TIME_ZONE,
            "USE_TZ": self.USE_TZ,
        }


time_zone_config = TimeZoneConfig()
