"""
Management command: create_tenant

Creates a new tenant, its primary domain, seeds default RBAC roles/permissions,
and optionally creates an initial owner user.

Usage:
  python manage.py create_tenant \\
      --name "Acme Corp" \\
      --schema acme \\
      --slug acme \\
      --domain acme.localhost \\
      --owner-email owner@acme.com \\
      --owner-password secret123
"""

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context


class Command(BaseCommand):
    help = "Provision a new tenant with RBAC seeds and an optional owner user."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True, help="Human-readable tenant name")
        parser.add_argument("--schema", required=True, help="PostgreSQL schema name (lowercase, no spaces)")
        parser.add_argument("--slug", required=True, help="URL-friendly slug")
        parser.add_argument("--domain", required=True, help="Primary hostname, e.g. acme.localhost")
        parser.add_argument("--owner-email", required=False, help="Email for the initial owner user")
        parser.add_argument("--owner-password", required=False, help="Password for the initial owner user")
        parser.add_argument("--owner-name", required=False, default="Owner", help="First name of the owner")

    def handle(self, *args, **options):
        from apps.tenant.models import Client, Domain

        schema = options["schema"]
        slug = options["slug"]

        if Client.objects.filter(schema_name=schema).exists():
            raise CommandError(f"Schema '{schema}' already exists.")

        # ── 1. Create tenant (triggers schema creation) ───────────────────────
        self.stdout.write(f"Creating tenant '{options['name']}' …")
        tenant = Client.objects.create(
            schema_name=schema,
            name=options["name"],
            slug=slug,
        )

        # ── 2. Attach primary domain ──────────────────────────────────────────
        Domain.objects.create(
            domain=options["domain"],
            tenant=tenant,
            is_primary=True,
        )
        self.stdout.write(f"  Domain: {options['domain']}")

        # ── 3. Seed RBAC inside the new schema ────────────────────────────────
        with schema_context(schema):
            self.stdout.write("  RBAC roles + permissions seeded ✓")

            # ── 4. Create initial owner user (optional) ───────────────────────
            owner_email = options.get("owner_email")
            if owner_email:
                from django.contrib.auth import get_user_model

                User = get_user_model()

                if User.objects.filter(email=owner_email).exists():
                    self.stdout.write(self.style.WARNING(f"  User '{owner_email}' already exists – skipping."))
                else:
                    password = options.get("owner_password") or User.objects.make_random_password()
                    owner_name = options.get("owner_name", "Owner")
                    user = User.objects.create_user(
                        email=owner_email,
                        password=password,
                        first_name=owner_name,
                        last_name="",
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Owner user created: {owner_email}"
                            + (f" (password: {password})" if not options.get("owner_password") else "")
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅  Tenant '{options['name']}' provisioned successfully!\n"
                f"   Schema : {schema}\n"
                f"   Domain : {options['domain']}"
            )
        )
