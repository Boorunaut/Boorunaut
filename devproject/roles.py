from rolepermissions.roles import AbstractUserRole

class Administrator(AbstractUserRole):
    available_permissions = {
        'modify_profile': True,
        'ban_user': True,
        'ban_mod': True,
        'change_configurations': True,
        'change_status': True,
        'mass_rename': True,
        'ban_hashes': True,
        'change_user_group': True,
        'manage_tags': True,
        'manage_comments': True,
    }

class Moderator(AbstractUserRole):
    available_permissions = {
        'modify_profile': True,
        'ban_user': True,
        'ban_mod': False,
        'change_configurations': False,
        'change_status': True,
        'mass_rename': True,
        'ban_hashes': True,
        'change_user_group': False,
        'manage_tags': True,
        'manage_comments': True,
    }
    
class Janitor(AbstractUserRole):
    available_permissions = {
        'modify_profile': False,
        'ban_user': False,
        'ban_mod': False,
        'change_configurations': False,
        'change_status': True,
        'mass_rename': True,
        'ban_hashes': True,
        'change_user_group': False,
        'manage_tags': True,
        'manage_comments': True,
    }

class User(AbstractUserRole):
    available_permissions = {
        'modify_profile': False,
        'ban_user': False,
        'ban_mod': False,
        'change_configurations': False,
        'change_status': False,
        'mass_rename': False,
        'ban_hashes': False,
        'change_user_group': False,
        'manage_tags': False,
        'manage_comments': False,
    }
