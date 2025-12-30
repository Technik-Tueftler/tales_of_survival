from discord import Interaction
from .configuration import Configuration, DcRole


async def check_permissions(
    config: Configuration, dc_roles: list[DcRole], user_roles: list[int]
) -> bool:
    config.logger.trace(
        f"Check permissions for roles: {dc_roles} and user roles: {user_roles}"
    )
    for dc_role in dc_roles:
        if dc_role == DcRole.EVERYONE:
            if config.env.dc.everyone_role_id in user_roles:
                return True
        elif dc_role == DcRole.HISTORIAN:
            if config.env.dc.historian_role_id in user_roles:
                return True
        elif dc_role == DcRole.STORYTELLER:
            if config.env.dc.storyteller_role_id in user_roles:
                return True
    return False


async def check_permissions_historian(
    config: Configuration, interaction: Interaction
) -> bool:
    user_roles_ids = [role.id for role in interaction.user.roles]
    config.logger.trace(f"Check historian permissions for user roles: {user_roles_ids}")
    if config.env.dc.historian_role_id in user_roles_ids:
        return True
    interaction.response.send_message(
        "Your role does not have the permission to execute this 'historian' command.",
        ephemeral=True,
    )
    return False
