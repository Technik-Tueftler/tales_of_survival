"""
This module contains functions to check Discord user permissions for specific roles.
"""

from discord import Interaction
from .configuration import Configuration


async def check_permissions_historian(
    config: Configuration, interaction: Interaction
) -> bool:
    """
    Check if the user has historian permission role in Discord.

    Args:
        config (Configuration): App configuration
        interaction (Interaction): Discord interaction object

    Returns:
        bool: User has the historian permission
    """
    user_roles_ids = [role.id for role in interaction.user.roles]
    config.logger.trace(f"Check historian permissions for user roles: {user_roles_ids}")
    if config.env.dc.historian_role_id in user_roles_ids:
        config.logger.trace(
            f"User: {interaction.user.id} has permission to execute historian command."
        )
        return True
    await interaction.response.send_message(
        "Your role does not have the permission to execute this 'historian' command.",
        ephemeral=True,
    )
    config.logger.trace(
        f"User: {interaction.user.id} has no permission to execute historian command."
    )
    return False
