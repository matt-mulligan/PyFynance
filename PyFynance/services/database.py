import datetime
import glob
import logging
import os
import sqlite3
import shutil

from core.config import Configuration
from core.exceptions import DatabaseError


class Database:
    """
    The database service is responsible for all interactions with the sqlite3 databases within PyFynance and is written
    as a light-weight API over the sqlite3 library.

    This API class implements public methods over the standard database operations and are paramterised so that they
    can be usable for a wide variety of use cases, while still proving option validation on their calls
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._config = Configuration()
        self._connections = {}
        self._cursors = {}
        self._sql = self._set_db_statements()

    def start_db(self, db_name, current=True):
        """
        This method will start the sqllite3 database specified. This method will create the connection and cursor
        object to allow interaction with the database, as well as trigger the table create commands for that database.

        The database must be within the config.database.db_name list or the service will thrown an error.

        :param db_name: The name of the database to start
        :type db_name: String
        :param current: Signifies if the database service should load the current database (True) or the backup (False).
            The default value for this value is True
        :type current: Boolean
        :return: None
        """

        try:
            self._logger.info(
                "Attempting to start the database service for database '{}'".format(
                    db_name
                )
            )
            self._check_db_name(db_name)
            db_path = self._get_db_path(db_name, current)
            self._connections[db_name] = sqlite3.connect(db_path)
            self._cursors[db_name] = self._connections[db_name].cursor()
            if current:
                self._build_tables(db_name)
            self._logger.info(
                "Successfully started the database service for database '{}'".format(
                    db_name
                )
            )
        except Exception as e:
            raise DatabaseError(
                "Exception occurred while starting database '{}'.  {}".format(
                    db_name, e
                )
            )

    def stop_db(self, db_name, commit=True):
        """
        This method will stop the sqlite3 database specified. This method will also optionally commit changes to the
        database and create a backup of the database if commit value is True

        :param db_name: The name of the database connection to stop and commit/backup
        :type db_name: String
        :param commit: Value used to indicate if the database should be committed and backed up before
            closing the connection
        :type commit: Boolean
        :return: None
        """

        try:
            self._logger.info(
                "Attempting to stop the database service for database '{}' with commit "
                "set to {}".format(db_name, commit)
            )
            self._check_db_name(db_name)
            if commit:
                self._commit_db(db_name)
            self._connections[db_name].close()
            if commit:
                self._backup_db(db_name)
            self._logger.info(
                "Successfully stopped the database service for database '{}' with commit "
                "set to {}".format(db_name, commit)
            )
        except Exception as e:
            raise DatabaseError(
                "Exception occurred while stopping database '{}'.  {}".format(
                    db_name, e
                )
            )

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

        try:
            self._logger.info(
                "Attempting insert of data into '{}.{}'".format(db_name, table)
            )
            self._check_db_name(db_name)
            self._check_table_name(db_name, table)
            column_names = []
            data_vals = []

            for col_name, data_val in data.items():
                column_names.append(col_name)
                data_vals.append(self._cast_data_for_insert(data_val))

            columns = ", ".join(column_names)
            data = ", ".join(data_vals)

            sql = self._sql["insert"].format(table=table, columns=columns, data=data)
            self._execute(db_name, sql)
            self._logger.info(
                "Successful insert of data into '{}.{}'".format(db_name, table)
            )
        except Exception as e:
            raise DatabaseError(
                "Exception occurred while inserting data into '{}.{}'.  {}".format(
                    db_name, table, e
                )
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

        try:
            self._logger.info(
                "Attempting select of data from '{}.{}'".format(db_name, table)
            )
            self._check_db_name(db_name)
            self._check_table_name(db_name, table)
            sql_key = "{cols}_{wheres}".format(
                cols="columns" if columns else "none",
                wheres="where" if where else "none",
            )
            sql = {
                "none_none": self._sql["select"]["select_all_from"],
                "columns_none": self._sql["select"]["select_columns_from"],
                "none_where": self._sql["select"]["select_all_from_where"],
                "columns_where": self._sql["select"]["select_columns_from_where"],
            }[sql_key]

            column_names = ", ".join(columns) if columns else None
            data = self._execute(
                db_name, sql.format(table=table, columns=column_names, where=where)
            ).fetchall()
            self._logger.info(
                "Successful select of data from '{}.{}'".format(db_name, table)
            )
            return data
        except Exception as e:
            raise DatabaseError(
                "Exception occurred while selecting data from '{}.{}'.  {}".format(
                    db_name, table, e
                )
            )

    def _build_tables(self, db_name):
        """
        This private method will build all of the table create statements for the database specified

        :param db_name: The name of the database to build the tables for.
        :type db_name: String
        :return: None
        """

        table_creates = {
            "transactions": [
                {
                    "table_name": "transactions",
                    "col_spec": self._config.database.column_specs["transactions"],
                    "primary_keys": self._config.database.primary_keys.transactions,
                }
            ]
        }[db_name]

        for table_info in table_creates:
            column_spec = self._build_column_spec(table_info["col_spec"])
            primary_keys = ", ".join(table_info["primary_keys"])
            sql = self._sql["create"].format(
                table=table_info["table_name"], col_spec=column_spec, keys=primary_keys
            )

            self._execute(db_name, sql)

    def _commit_db(self, db_name):
        """
        This private method will commit the changes to the database file.

        :param db_name: The name of the database to commit
        :type db_name: String
        :return: None
        """

        self._connections[db_name].commit()

    def _backup_db(self, db_name):
        """
        This private method will backup the database instance that has just been stopped.

        :param db_name: The name of the database to backup
        :type db_name: String
        :return: None
        """

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        source_path = os.sep.join(
            [self._config.paths.db_path, "current", "{}.db".format(db_name)]
        )
        backup_path = os.sep.join(
            [
                self._config.paths.db_path,
                "backup",
                "{}_{}.db".format(db_name, timestamp),
            ]
        )
        shutil.copyfile(source_path, backup_path)

    def _execute(self, db_name, sql):
        """
        This private method will execute a database command on the specified database.

        :param db_name: The name of the database that the command should be run against
        :type db_name: String
        :param sql: The sql command that should be executed
        :type sql: String
        :return: None
        """

        self._logger.debug("Attempting to execute sql command '{}'".format(sql))
        execute_output = self._cursors[db_name].execute(sql)
        self._logger.debug("Successful execution of sql command '{}'".format(sql))
        return execute_output

    def _check_db_name(self, db_name):
        """
        This private method will check that the given db name exists within the names list from the config service.

        :param db_name: The name of the database to check
        :type db_name: String
        :return: None
        """

        if db_name not in self._config.database.db_names:
            raise DatabaseError(
                "Database name specified is not an acceptable PyFynance database. Acceptable "
                "PyFynance databases include {}".format(self._config.database.db_names)
            )

    def _check_table_name(self, db_name, table):
        """
        This private method will check that the given table name is a known table within the given database

        :param db_name: The name of the database to check against
        :type db_name: String
        :param table: The name of the table to check
        :type table: String
        :return: None
        """

        tables = {
            "transactions": self._config.database.tables.transactions,
            "rules": self._config.database.tables.rules,
        }[db_name]

        if table not in tables:
            raise DatabaseError(
                "Table name '{}' is not a known table for database '{}'. Known tables are '{}' ".format(
                    table, db_name, tables
                )
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
        db_name = (
            "{}.db".format(db_name) if current else self._get_backup_db_name(db_name)
        )
        return os.sep.join([self._config.paths.db_path, state, db_name])

    def _get_backup_db_name(self, db_name):
        """
        This private method will determine the latest backup version of the db_name that is provided

        :param db_name: The name of the database to find
        :type db_name: String
        :return: the name of the latest backup for that database
        """

        search_path = os.sep.join(
            [self._config.paths.db_path, "backup", "{}*.db".format(db_name)]
        )
        paths = glob.glob(search_path)
        paths.sort(reverse=True)
        return paths[0].split(os.sep)[-1]

    @staticmethod
    def _build_column_spec(col_spec):
        """
        This private method will build the column specification string required to create a table.

        :param col_spec: Contains the column names and data types for the database table
        :type col_spec: Dictionary
        :return: String: formatted column spec string for table create statement
        """

        column_specs = []
        for col_name, col_type in col_spec.items():
            column_specs.append("{} {}".format(col_name, col_type))
        return ", ".join(column_specs)

    @staticmethod
    def _set_db_statements():
        """
        this private static method creates a dictionary of standard sql statements to be used by the Database class.

        :return: Dictionary: sql statements to be used by the database class
        """

        return {
            "create": "CREATE TABLE IF NOT EXISTS {table} ({col_spec}, PRIMARY KEY ({keys}));",
            "insert": "INSERT INTO {table}({columns}) VALUES({data});",
            "select": {
                "select_all_from": "SELECT * FROM {table};",
                "select_columns_from": "SELECT {columns} FROM {table};",
                "select_all_from_where": "SELECT * FROM {table} WHERE {where};",
                "select_columns_from_where": "SELECT {columns} FROM {table} WHERE {where};",
            },
        }

    @staticmethod
    def _cast_data_for_insert(data):
        """
        This private static method will correctly cast data based on its data type for insertion into a table
        using sqlite3

        :param data: ANY: the data that needs to be cast
        :return: ANY: returns the correctly cast data for insertion
        """

        if type(data) is str:
            return '"{}"'.format(data)
        else:
            return str(data)
