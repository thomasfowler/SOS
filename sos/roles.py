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

    }


class SalesDirector(AbstractUserRole):
    available_permissions = {}
