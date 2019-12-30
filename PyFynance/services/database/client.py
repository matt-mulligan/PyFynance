import logging
import os
import sqlite3

from services.database.exception import SqliteClientException

IN_MEMORY_CONNECT = ":memory:"


class SqliteClient(object):
    """
    This class is the client class for interactions with Sqlite databases.
    this class is intended to be passed as an object to a database service class
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._connections = dict()
        self._cursors = dict()
        self._sql = self._set_db_statements()

    # ---- Public API Methods ------------------------------
    def start_db(self, db_name, db_path, in_memory=False):
        """
        This method will start the sqllite3 database specified. This method will create the connection and cursor
        object to allow interaction with the database

        :param db_name: The name of the database to start
        :type db_name: String
        :param db_path: a filesystem path to a sqlite3 database
        :type db_path: String
        :param in_memory: indicates if the database to be started should be in_memory
        :type in_memory: Boolean
        :param create: indicates if the
        :return: None
        """

        try:
            self._logger.info(
                f"Attempting to start sqlite database '{db_name}' with db_path='{db_path}' and in_memory={in_memory}"
            )

            if db_name in self._connections.keys():
                self._logger.warning(
                    f"database connection {db_name} already registered/started.  Skipping."
                )
                return

            connection_string = IN_MEMORY_CONNECT if in_memory else db_path
            self._connections[db_name] = sqlite3.connect(connection_string)
            self._cursors[db_name] = self._connections[db_name].cursor()
            self._logger.info(
                f"Successfully started sqlite database '{db_name}' with db_path='{db_path}' and in_memory={in_memory}"
            )
        except Exception as e:
            raise SqliteClientException(
                f"Exception occurred while starting database '{db_name}' with path '{db_path}' "
                f"and in_memory={in_memory}.  {e}"
            )

    def stop_db(self, db_name, commit=True):
        """
        This method will stop the sqlite3 database specified. This method will also optionally commit changes to the
        database.

        :param db_name: The name of the database connection to stop and commit
        :type db_name: String
        :param commit: Indicates if the database should be commited before closing it
        :type commit: Boolean
        :return: None
        """

        try:
            self._logger.info(
                f"Attempting to stop the database '{db_name}' with commit set to {commit}"
            )
            if db_name not in self._connections.keys():
                self._logger.warning(
                    f"sqlite database connection '{db_name}' is not currently open. "
                    f"skipping remaining execution of stop_db"
                )
                return

            if commit:
                self._logger.info(f"Commiting the database '{db_name}'")
                self._connections[db_name].commit()
            self._connections[db_name].close()
            self._logger.info(
                f"Successfully stopped the database service for database '{db_name}' with commit set to {commit}"
            )
        except Exception as e:
            raise SqliteClientException(
                f"Exception occurred while stopping database '{db_name}' with commit set to {commit}.  {e}"
            )

    def create_table(self, db_name, table, col_spec, primary_keys):
        """
        This public method will create a table for the specified database.
        The database specified should already be started.

        :param db_name: the name of the database to create the table in
        :param table: the name of the table to create
        :param col_spec:
        :param primary_keys:
        :return:
        """

        self._logger.info(
            f"Attempting to create table '{table}' for database '{db_name}'"
        )
        pk_string = ", ".join(primary_keys)
        col_spec_string = self._build_column_spec(col_spec)
        sql = self._sql["create"].format(
            table=table, col_spec=col_spec_string, keys=pk_string
        )
        self.execute(db_name, sql)
        self._logger.info(
            f"Successfully created table '{table}' for database '{db_name}'"
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
            self._logger.info(f"Attempting insert of data into '{db_name}.{table}'")
            column_names = []
            data_vals = []
            data_inserts = []

            for col_name, data_val in data.items():
                column_names.append(col_name)
                data_inserts.append("?")
                data_vals.append(self._cast_data_for_insert(data_val))

            columns = ", ".join(column_names)
            data = tuple(data_vals)
            data_placeholders = ", ".join(data_inserts)

            sql = self._sql["insert"].format(
                table=table, columns=columns, placeholders=data_placeholders
            )
            self.execute(db_name, sql, data)
            self._logger.info(f"Successful insert of data into '{db_name}.{table}'")
        except Exception as e:
            raise SqliteClientException(
                f"Exception occurred while inserting data into '{db_name}.{table}'.  {e}"
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
                f"Attempting select of data from '{db_name}.{table}' for columns "
                f"'{'All' if not columns else columns}' with where clause '{where}'"
            )
            select_sql = self._generate_select_sql_command(columns, table, where)
            data = self.execute(db_name, select_sql).fetchall()
            self._logger.info(
                f"Successful select of data from '{db_name}.{table}' for columns "
                f"'{'All' if not columns else columns}' with where clause '{where}'"
            )
            return data
        except Exception as e:
            raise SqliteClientException(
                f"Exception occurred while selecting data from '{db_name}.{table}' for columns '"
                f"{'All' if not columns else columns}' with where clause '{where}'.  {e}"
            )

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

        try:
            self._logger.info(
                f"Attempting update data from '{db_name}.{table}' for rows matching {primary_keys}"
            )
            self._logger.info(f"Values to update are {data}")
            update_cols = []
            pk_cols = []
            update_vals = []

            for col_name, col_val in data.items():
                update_cols.append(col_name)
                update_vals.append(self._cast_data_for_insert(col_val))

            for pk_name, pk_val in primary_keys.items():
                pk_cols.append(pk_name)
                update_vals.append(self._cast_data_for_insert(pk_val))

            data_str = " = ?, ".join(update_cols)
            data_str += " = ?"

            pk_str = " = ? AND ".join(pk_cols)
            pk_str += " = ?"

            update_vals = tuple(update_vals)
            sql = self._sql["update"].format(
                table=table, data=data_str, primary_keys=pk_str
            )
            self._logger.info(
                f"SQL statement to insert data is '{sql}' with data values of {update_vals}"
            )

            self.execute(db_name, sql, update_vals)
            self._logger.info(
                f"Successful update of data into '{db_name}.{table} for rows matching {primary_keys}'"
            )
        except Exception as e:
            raise SqliteClientException(
                f"Exception occurred while updating data in '{db_name}.{table}'.  {e}"
            )

    def execute(self, db_name, sql, data=None):
        """
        This public method will execute a database command on the specified database.

        :param db_name: The name of the database that the command should be run against
        :type db_name: String
        :param sql: The sql command that should be executed
        :type sql: String
        :param data: the data to be inserted if this is a data command
        :type data: Tuple
        :return: Returns the database return value.
        """

        self._logger.debug(
            f"Attempting to execute sql command '{sql}' with data '{data}' on database '{db_name}'"
        )
        execute_output = (
            self._cursors[db_name].execute(sql, data)
            if data
            else self._cursors[db_name].execute(sql)
        )
        self._logger.debug(
            f"Successful execution of sql command '{sql}' with data '{data}'"
        )
        return execute_output

    # ---- Private Class Methods ------------------------------
    def _generate_select_sql_command(self, columns, table, where):
        """
        This private method will generate an appropriate sqlite3 select command based on the values passed to it
        :param columns:
        :param table:
        :param where:
        :return:
        """

        sql_key = f"{'columns' if columns else 'none'}_{'where' if where else 'none'}"
        sql = {
            "none_none": self._sql["select"]["select_all_from"],
            "columns_none": self._sql["select"]["select_columns_from"],
            "none_where": self._sql["select"]["select_all_from_where"],
            "columns_where": self._sql["select"]["select_columns_from_where"],
        }[sql_key]
        column_names = ", ".join(columns) if columns else None

        return sql.format(table=table, columns=column_names, where=where)

    # ---- Static Class Methods ------------------------------
    @staticmethod
    def _set_db_statements():
        """
        this private static method creates a dictionary of standard sql statements to be used by the Database class.

        :return: Dictionary: sql statements to be used by the database class
        """

        return {
            "create": "CREATE TABLE IF NOT EXISTS {table} ({col_spec}, PRIMARY KEY ({keys}));",
            "insert": "INSERT INTO {table}({columns}) VALUES({placeholders});",
            "update": "UPDATE {table} SET {data} WHERE {primary_keys};",
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

        return str(data) if data is not None else data

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
