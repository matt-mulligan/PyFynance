import logging
import os
import sqlite3
from datetime import datetime
from shutil import copyfile

from core.config import Configuration
from core.exceptions import DatabaseError


class Database:
    """
    The database service is responsible for all interactions with the sqlite3 databases within PyFynance and is written
    as a light-weight API over them
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._config = Configuration()
        self._connections = {}
        self._cursors = {}
        self._set_db_constants()

    def start_db(self, db_name):
        """
        this method will start the sqllite3 database
        :return:
        """

        try:
            self._check_db_name(db_name)
            db_path = self._get_db_path(db_name)
            self._connections[db_name] = sqlite3.connect(db_path)
            self._cursors[db_name] = self._connections[db_name].cursor()
            self._build_tables()
        except sqlite3.Error as e:
            print(e)

    def stop_db(self, commit=True):
        """
        this method will stop the sqlite3 databse
        :param commit: boolean value used to indicate if the database should eb committed before closing the connection
        :return:
        """

        if commit:
            self.commit_db()
        self._connections.close()

    def commit_db(self):
        """
        this method will commit the changes to the database file
        :return:
        """

        self._connections.commit()

    def rollback_db(self):
        """
        this method will rollback the DB
        :return:
        """

        pass

    def _execute(self, sql, data=None):
        """
        this method will execute a database command
        :param cmd:
        :return:
        """

        if data:
            self._cursors.execute(sql, data)
        else:
            self._cursors.execute(sql)

    def _fetchall(self):
        """
        this method will call fetchall on the cursor object and return the value
        :return:
        """

        return self._cursors.fetchall()

    def _check_db_name(self, db_name):
        """
        this private method will check that the given db name exists within the names list from the config service
        :param db_name:
        :return:
        """

        if db_name not in self._config.database.db_names:
            raise DatabaseError("Database name specified is not an acceptable PyFynance database. Acceptable "
                                "PyFynance databases include {}".format(self._config.database.db_names))

    def _get_db_path(self, db_name):
        """
        this private method will return the correct path to the database based on the name
        :param db_name:
        :return:
        """

        return {
            "transactions": self._config.database.transactions_db_path,
            "rules": self._config.database.rules_db_path
        }[db_name]

    def _set_db_constants(self):
        """
        this private method will initialise all of the DB services constants used for table creation and updates
        :return:
        """

        self._CREATE_TABLE_TRANSACTIONS = "CREATE TABLE IF NOT EXISTS transactions (transaction_id integer, " \
                                          "institution text, account text, amount decimal, narrative text " \
                                          "PRIMARY KEY (transaction_id));"
