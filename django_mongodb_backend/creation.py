from django.conf import settings
from django.db.backends.base.creation import BaseDatabaseCreation

from django_mongodb_backend.management.commands.createcachecollection import (
    Command as CreateCacheCollection,
)


class DatabaseCreation(BaseDatabaseCreation):
    def _execute_create_test_db(self, cursor, parameters, keepdb=False):
        if not keepdb:
            self._destroy_test_db(parameters["dbname"], verbosity=0)

    def _destroy_test_db(self, test_database_name, verbosity):
        # At this point, settings still points to the non-test database. For
        # MongoDB, it must use the test database.
        settings.DATABASES[self.connection.alias]["NAME"] = test_database_name
        self.connection.settings_dict["NAME"] = test_database_name

        for collection in self.connection.introspection.table_names():
            if not collection.startswith("system."):
                self.connection.database.drop_collection(collection)

    def create_test_db(self, *args, **kwargs):
        test_database_name = super().create_test_db(*args, **kwargs)
        # Not using call_command() avoids the requirement to put
        # "django_mongodb_backend" in INSTALLED_APPS.
        CreateCacheCollection().handle(
            database=self.connection.alias, verbosity=kwargs["verbosity"]
        )
        return test_database_name
