from typing import Any

from pydantic import Field, computed_field

from config.django._base_config import DjangoConfig


class DocumentationConfig(DjangoConfig):
    """OpenAPI schema and Swagger/ReDoc UI settings for drf-spectacular."""

    TITLE: str = Field(default="LawHub API")
    DESCRIPTION: str = Field(default="Study Abroad & Consultation Platform API Documentation")
    VERSION: str = Field(default="1.0.0")
    TERMS_OF_SERVICE: str = Field(default="")

    CONTACT_NAME: str = Field(default="Md. Sazzad Hossen")
    CONTACT_URL: str = Field(default="")
    CONTACT_EMAIL: str = Field(default="mshossen75@gmail.com")

    LICENSE_NAME: str = Field(default="MIT")
    LICENSE_URL: str = Field(default="https://opensource.org/licenses/MIT")

    SWAGGER_UI_DIST: str = Field(default="SIDECAR")
    SWAGGER_UI_FAVICON_HREF: str = Field(default="SIDECAR")
    REDOC_DIST: str = Field(default="SIDECAR")

    SCHEMA_PATH_PREFIX: str = Field(default=r"/api/v[0-9]")
    SCHEMA_PATH_PREFIX_INSERT: str = Field(default="")
    SCHEMA_PATH_PREFIX_TRIM: bool = Field(default=True)

    SERVERS: list[dict[str, str]] = Field(default_factory=list)

    @computed_field
    def SPECTACULAR_SETTINGS(self) -> dict[str, Any]:
        """Generate the SPECTACULAR_SETTINGS dict expected by drf-spectacular."""
        return {
            "TITLE": self.TITLE,
            "DESCRIPTION": self.DESCRIPTION,
            "VERSION": self.VERSION,
            "TERMS_OF_SERVICE": self.TERMS_OF_SERVICE,
            "CONTACT": {
                "name": self.CONTACT_NAME,
                "url": self.CONTACT_URL,
                "email": self.CONTACT_EMAIL,
            },
            "LICENSE": {
                "name": self.LICENSE_NAME,
                "url": self.LICENSE_URL,
            },
            "SWAGGER_UI_DIST": self.SWAGGER_UI_DIST,
            "SWAGGER_UI_FAVICON_HREF": self.SWAGGER_UI_FAVICON_HREF,
            "REDOC_DIST": self.REDOC_DIST,
            "SCHEMA_PATH_PREFIX": self.SCHEMA_PATH_PREFIX,
            "SCHEMA_PATH_PREFIX_INSERT": self.SCHEMA_PATH_PREFIX_INSERT,
            "SCHEMA_PATH_PREFIX_TRIM": self.SCHEMA_PATH_PREFIX_TRIM,
            "SERVERS": self.SERVERS,
            "SECURITY_SCHEMES": {"jwt": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
        }

    def as_django_settings(self) -> dict:
        return {"SPECTACULAR_SETTINGS": self.SPECTACULAR_SETTINGS}


documentation_config = DocumentationConfig()
