import datetime
import glob
import logging
import os
import shutil

from core import helpers
from services.database.exception import DatabaseServiceException


class Database(object):
    """
    The database service class is the PyFynance business logic abstraction over the top of a database client class.
    """

    def __init__(self, client, config):
        self._logger = logging.getLogger(__name__)
        self._client = client
        self._config = config

    def create_db(self, db_name, db_path):
        """
        This public method will create the specified database in the specified path including creating all of the tables
        :param db_name: the name fo the PyFyance database to create
        :param db_path: the path to create the database in.
        :return:
        """

        self._client.start_db(db_name, db_path)
        for table in self._config.database.tables[db_name]:
            col_spec = self._config.database.column_specs[table]
            primary_keys = self._config.database.primary_keys[table]
            self._client.create_table(db_name, table, col_spec, primary_keys)

    def start_db(self, db_name, current=True, create=True):
        """
        This public method will start any PyFynance database specified.
        The database must be within the config.database.db_name list or the service will thrown an error.

        :param db_name: The name of the database to start
        :type db_name: String
        :param current: Signifies if the database service should load the current database (True) or the backup (False).
            The default value for this value is True
        :type current: Boolean
        :return: None
        """

        self._logger.info(
            f"Attempting to start the PyFynance database service for database '{db_name}'"
        )
        self._check_db_name(db_name)
        db_path = self._get_db_path(db_name, current)
        if create and not os.path.exists(db_path):
            self.create_db(db_name, db_path)
        else:
            self._client.start_db(db_name, db_path)
        self._logger.info(
            f"Successfully started the PyFynance database service for database '{db_name}'"
        )

    def stop_db(self, db_name, commit=True):
        """
        This method will stop the PyFynance database specified. This method will also optionally commit changes to the
        database and create a backup of the database if commit value is True

        :param db_name: The name of the database connection to stop and commit/backup
        :type db_name: String
        :param commit: Value used to indicate if the database should be committed and backed up before
            closing the connection
        :type commit: Boolean
        :return: None
        """

        self._logger.info(
            f"Attempting to stop the PyFynance database '{db_name}' with commit set to {commit}"
        )
        self._check_db_name(db_name)
        self._client.stop_db(db_name, commit)
        if commit:
            self._backup_db(db_name)
        self._logger.info(
            f"Successfully stopped PyFynance database '{db_name}' with commit set to {commit}"
        )

    def select(self, db_name, table, columns=None, where=None):
        """
        This public method allows users to submit select statements against the specified database and table.

        This method allows users to specified the columns to be returned and any where conditions they want to apply to
        the select statements

        Example Calls:

        .. code-block:: python

            db.select("database", "table")  # returns all columns for database.table
            db.select("database", "table", columns=["id", "age"])  # returns the ID and age columns of database.table
            db.select("database", "table", where="age > 13")  # returns all columns from database.table where age > 13

        :param db_name: The name of the database to query. This database must have already been started using
            the start_db method
        :type db_name: String
        :param table: The name of the table to query from the database specified
        :type table: String
        :param columns: Optional. List of columns to select from table. Default value is None and will select
            all columns from the table
        :type table: List
        :param where: Optional. Where command to filter the select statement with. Default value is None.
        :type where: String
        :return: List: list of rows returned from the database
        """

        return self._client.select(db_name, table, columns, where)

    def insert(self, db_name, table, data):
        """
        This public method allows users to submit insert queries to the specified database and table to add data.

        Example Calls:

        .. code-block:: python

            db.insert("database", "table", {"ID": 1, "Name": "Billy NoMates McGee"})
            # above code will insert a new row into database.table where the column "ID" is set to 1 and the column
            # name is set to "Billy NoMates McGee" (why would his parents name him that?! so cruel)

        :param db_name: the name of the database to query. This database must have already been started using
            the start_db method
        :type db_name: String
        :param table: the name of the table to insert data into from the database specified
        :type table: String
        :param data: A dictionary of data to insert with key values being the column names and values
            being the data to insert for that column
        :type data: Dictionary
        :return: None
        """

        self._client.insert(db_name, table, data)

    def update(self, db_name, table, data, primary_keys):
        """
        This public method allows users to update a row of a table.

        This method requires the user to specify the columns and values to update, as well as the primary keys
        and their values to select against

        Example Calls:

        .. code-block:: python

            db.update(db_name="database",
                      table="table",
                      data={age: 26, job: "engineer"},
                      primary_keys={name: "Matt Mulligan", id: 007})

            # the above statement will attempt to update rows of database.table
            # it will update the value of "age" to 26 and "job" to engineer for any row where "name" = "Matt Mulligan"
            # and "id" = 007


        :param db_name: The name of the database to query. This database must have already been started using
            the start_db method
        :type db_name: String
        :param table: The name of the table to query from the database specified
        :type table: String
        :param data: Dictionary of columns to update for a row, they the key is the column name and the value is
            the value to update
        :type data: Dictionary
        :param primary_keys: a dictionary used to select which rows to update, where the key is the column name and
            the value is the value of the columns.
        :type primary_keys: Dictionary
        :return: None
        """

        self._client.update(db_name, table, data, primary_keys)

    def _check_db_name(self, db_name):
        """
        This private method will check that the given db name exists within the names list from the config service.

        :param db_name: The name of the database to check
        :type db_name: String
        :return: None
        """

        if db_name not in self._config.database.db_names:
            raise DatabaseServiceException(
                f"Database name specified '{db_name}' is not an acceptable PyFynance database. Acceptable "
                f"PyFynance databases include {self._config.database.db_names}"
            )

    def _get_db_path(self, db_name, current=True):
        """
        this private method will return the correct path to the database based on the database name and if they wish
        to access the current or backup DB

        :param db_name: The name of the database to find the path for.
        :type db_name: String
        :param current: Optional. Signifies if the path to be returned should be to the current or backup database.
        Default value is to return the current DB
        :type current: Boolean
        :return: String: path to the database file
        """

        state = "current" if current else "backup"
        db_name = f"{db_name}.db" if current else self._get_backup_db_name(db_name)
        return os.sep.join([self._config.paths.db_path, state, db_name])

    def _get_backup_db_name(self, db_name):
        """
        This private method will determine the latest backup version of the db_name that is provided

        :param db_name: The name of the database to find
        :type db_name: String
        :return: the name of the latest backup for that database
        """

        search_path = os.sep.join(
            [self._config.paths.db_path, "backup", f"{db_name}*.db"]
        )
        paths = glob.glob(search_path)
        paths.sort(reverse=True)
        return paths[0].split(os.sep)[-1]

    def _backup_db(self, db_name):
        """
        This private method will backup the database instance that has just been stopped.

        :param db_name: The name of the database to backup
        :type db_name: String
        :return: None
        """

        timestamp = helpers.get_current_time_string()
        source_path = os.sep.join(
            [self._config.paths.db_path, "current", f"{db_name}.db"]
        )
        backup_path = os.sep.join(
            [self._config.paths.db_path, "backup", f"{db_name}_{timestamp}.db"]
        )
        shutil.copyfile(source_path, backup_path)
