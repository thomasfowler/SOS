from rolepermissions.roles import AbstractUserRole


class AccountManager(AbstractUserRole):
    available_permissions = {
        'create_opportunity': True,
        'view_own_opportunity': True,
        'change_own_opportunity': True,
        'delete_own_opportunity': True,
    }


class BusinessUnitHead(AbstractUserRole):
    available_permissions = {
        **AccountManager.available_permissions,  # Inherits from AccountManager
        'approve_bu_opportunity': True,
        'view_bu_opportunity': True,
    }


class SalesDirector(AbstractUserRole):
    available_permissions = {
        **BusinessUnitHead.available_permissions,  # Inherits from BusinessUnitHead
        'approve_agency_opportunity': True,
        'view_all_opportunity': True,
    }
