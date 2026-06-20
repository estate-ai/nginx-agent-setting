import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "authentik.root.settings")
os.environ.setdefault("AUTHENTIK_LOG_LEVEL", "warning")
sys.path.insert(0, "/")

import django

django.setup()

from authentik.core.models import Token, TokenIntents, User, UserTypes
from authentik.rbac.models import Role


ROLE_NAME = "msa-user-api-manager"
USERNAME = "svc-msa-user-api"
TOKEN_IDENTIFIER = "msa-user-api-token"
TOKEN_ENV = "AUTHENTIK_MSA_USER_API_TOKEN"
USER_PERMISSIONS = [
    "authentik_core.view_user",
    "authentik_core.change_user",
]


def main() -> None:
    token_key = os.environ.get(TOKEN_ENV)
    if not token_key:
        raise RuntimeError(f"{TOKEN_ENV} is required")

    role, _ = Role.objects.get_or_create(name=ROLE_NAME)
    role.assign_perms(USER_PERMISSIONS)

    user, _ = User.objects.update_or_create(
        username=USERNAME,
        defaults={
            "name": "MSA User API Service Account",
            "email": "svc-msa-user-api@localhost",
            "is_active": True,
            "type": UserTypes.INTERNAL,
            "path": "goauthentik.io/services",
        },
    )
    user.roles.add(role)

    Token.objects.update_or_create(
        identifier=TOKEN_IDENTIFIER,
        defaults={
            "intent": TokenIntents.INTENT_API,
            "user": user,
            "expiring": False,
            "description": "Internal MSA token for authentik user API access",
            "key": token_key,
        },
    )

    print(
        "bootstrapped",
        f"user={user.username}",
        f"user_pk={user.pk}",
        f"role={role.name}",
        f"token={TOKEN_IDENTIFIER}",
    )


if __name__ == "__main__":
    main()
