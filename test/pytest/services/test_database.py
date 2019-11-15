import os
import unittest
from datetime import datetime
from decimal import Decimal

from mock import patch, call, MagicMock, mock_open
from pytest import fixture, raises

from core.exceptions import DatabaseError
from services.database import Database


@fixture
def db():
    db = Database()
    db._config.paths.db_path = os.sep.join(["C:", "base", "db", "path"])
    return db


@fixture()
def connection_mock(cursor_mock):
    connection = MagicMock()
    connection.cursor().return_value = cursor_mock
    yield connection


@fixture()
def cursor_mock():
    sqlite_mock = MagicMock()
    yield sqlite_mock


@fixture
def insert_data():
    return {
        "institution": "matts_fully_sick_bank",
        "account": "multi-billion_dollar_savings",
        "tran_id": "42069",
        "tran_type": "CREDIT",
        "amount": Decimal("-135000.00"),
        "narrative": "sweet ass tesla",
        "date_posted": "20600707103000",
    }


def test_when_init_then_database_service_returned():
    db = Database()
    assert hasattr(db, "_logger")
    assert hasattr(db, "_config")
    assert hasattr(db, "_connections")
    assert hasattr(db, "_cursors")
    assert hasattr(db, "_sql")

    assert db._sql == {
        "create": "CREATE TABLE IF NOT EXISTS {table} ({col_spec}, PRIMARY KEY ({keys}));",
        "insert": "INSERT INTO {table}({columns}) VALUES({data});",
        "select": {
            "select_all_from": "SELECT * FROM {table};",
            "select_columns_from": "SELECT {columns} FROM {table};",
            "select_all_from_where": "SELECT * FROM {table} WHERE {where};",
            "select_columns_from_where": "SELECT {columns} FROM {table} WHERE {where};",
        },
    }


def test_when_start_db_and_current_and_good_db_name_then_db_started(
    db, connection_mock
):
    with patch("sqlite3.connect", return_value=connection_mock) as sqlite_mock:
        db.start_db("transactions", current=True)

        assert "transactions" in db._connections.keys()
        assert "transactions" in db._cursors.keys()
        sqlite_mock.assert_has_calls(
            [
                call(
                    os.sep.join(
                        ["C:", "base", "db", "path", "current", "transactions.db"]
                    )
                )
            ]
        )
        connection_mock.cursor.assert_called()
        connection_mock.cursor.assert_has_calls(
            [
                call().execute(
                    "CREATE TABLE IF NOT EXISTS transactions (institution text, account text, tran_id text, "
                    "tran_type text, amount decimal, narrative text, date_posted text, date_processed text, PRIMARY KEY "
                    "(institution, account, tran_id));"
                )
            ]
        )


@patch("glob.glob")
def test_when_start_db_and_backup_and_good_db_name_then_db_started(
    glob_mock, db, connection_mock
):
    with patch("sqlite3.connect", return_value=connection_mock) as sqlite_mock:
        glob_mock.return_value = [
            os.sep.join(
                ["C:", "path", "to", "backup_db", "transactions.db29991231235959"]
            )
        ]
        db.start_db("transactions", current=False)

        assert "transactions" in db._connections.keys()
        assert "transactions" in db._cursors.keys()
        sqlite_mock.assert_has_calls(
            [
                call(
                    os.sep.join(
                        [
                            "C:",
                            "base",
                            "db",
                            "path",
                            "backup",
                            "transactions.db29991231235959",
                        ]
                    )
                )
            ]
        )
        connection_mock.cursor.assert_called()
        create_table_call = call().execute(
            "CREATE TABLE IF NOT EXISTS transactions (institution text, account text, "
            "tran_id text, tran_type text, amount decimal, narrative text, "
            "date_posted text, PRIMARY KEY (institution, account, tran_id));"
        )
        assert create_table_call not in connection_mock.cursor.mock_calls


def test_when_start_db_and_bad_db_name_then_error(db):
    with raises(DatabaseError) as raised_error:
        db.start_db("not_a_real_db")
    assert (
        raised_error.value.args[0]
        == "Exception occurred while starting database 'not_a_real_db'.  Database name "
        "specified is not an acceptable PyFynance database. Acceptable PyFynance "
        "databases include ['transactions']"
    )


@patch("datetime.datetime")
@patch("shutil.copyfile", return_value=MagicMock())
def test_when_stop_db_and_commit_and_good_db_name_then_db_stopped(
    copyfile_mock, datetime_mock, db, connection_mock
):
    datetime_mock.now = MagicMock(return_value=datetime(2999, 12, 31, 23, 59, 59))
    db._connections["transactions"] = connection_mock
    db.stop_db("transactions", commit=True)
    connection_mock.assert_has_calls([call.commit(), call.close()])
    copyfile_mock.assert_has_calls(
        [
            call(
                os.sep.join(["C:", "base", "db", "path", "current", "transactions.db"]),
                os.sep.join(
                    [
                        "C:",
                        "base",
                        "db",
                        "path",
                        "backup",
                        "transactions_29991231235959.db",
                    ]
                ),
            )
        ]
    )


@patch("shutil.copyfile", return_value=MagicMock())
def test_when_stop_db_and_no_commit_and_good_db_name_then_db_stopped(
    copyfile_mock, db, connection_mock
):
    db._connections["transactions"] = connection_mock
    db.stop_db("transactions", commit=False)
    connection_mock.assert_has_calls([call.close()])
    assert call.commit() not in connection_mock.mock_calls
    copyfile_mock.assert_not_called()


def test_when_stop_db_and_bad_db_name_then_error(db):
    with raises(DatabaseError) as raised_error:
        db.stop_db("not_a_real_db")
    assert (
        raised_error.value.args[0]
        == "Exception occurred while stopping database 'not_a_real_db'.  Database name "
        "specified is not an acceptable PyFynance database. Acceptable PyFynance "
        "databases include ['transactions']"
    )


def test_when_insert_and_db_good_and_table_good_then_sql_called(
    db, cursor_mock, insert_data
):
    db._cursors["transactions"] = cursor_mock
    db.insert("transactions", "transactions", insert_data)
    cursor_mock.assert_has_calls(
        [
            call.execute(
                "INSERT INTO transactions(institution, account, tran_id, tran_type, amount, narrative, "
                'date_posted) VALUES("matts_fully_sick_bank", "multi-billion_dollar_savings", "42069", '
                '"CREDIT", -135000.00, "sweet ass tesla", "20600707103000");'
            )
        ]
    )


def test_when_insert_and_bad_db_name_then_error(db, insert_data):
    with raises(DatabaseError) as raised_error:
        db.insert("not_a_real_db", "transactions", insert_data)
    assert (
        raised_error.value.args[0]
        == "Exception occurred while inserting data into 'not_a_real_db.transactions'."
        "  Database name specified is not an acceptable PyFynance database. "
        "Acceptable PyFynance databases include ['transactions']"
    )


def test_when_insert_and_bad_table_name_then_error(db, insert_data):
    with raises(DatabaseError) as raised_error:
        db.insert("transactions", "not_a_real_db", insert_data)
    assert (
        raised_error.value.args[0]
        == "Exception occurred while inserting data into 'transactions.not_a_real_db'"
        ".  Table name 'not_a_real_db' is not a known table for database "
        "'transactions'. Known tables are '['transactions']' "
    )


def test_when_select_and_columns_none_and_where_none_then_sql_executed(db, cursor_mock):
    db._cursors["transactions"] = cursor_mock
    db.select("transactions", "transactions", columns=None, where=None)
    cursor_mock.assert_has_calls(
        [call.execute("SELECT * FROM transactions;"), call.execute().fetchall()]
    )


def test_when_select_and_columns_defined_and_where_none_then_sql_executed(
    db, cursor_mock
):
    db._cursors["transactions"] = cursor_mock
    columns = ["name", "yeet-ness"]
    db.select("transactions", "transactions", columns=columns, where=None)
    cursor_mock.assert_has_calls(
        [
            call.execute("SELECT name, yeet-ness FROM transactions;"),
            call.execute().fetchall(),
        ]
    )


def test_when_select_and_columns_none_and_where_defined_then_sql_executed(
    db, cursor_mock
):
    db._cursors["transactions"] = cursor_mock
    where = "power_level > 9000"
    db.select("transactions", "transactions", columns=None, where=where)
    cursor_mock.assert_has_calls(
        [
            call.execute("SELECT * FROM transactions WHERE power_level > 9000;"),
            call.execute().fetchall(),
        ]
    )


def test_when_select_and_columns_defined_and_where_defined_then_sql_executed(
    db, cursor_mock
):
    db._cursors["transactions"] = cursor_mock
    columns = ["name", "yeet-ness"]
    where = "power_level > 9000"
    db.select("transactions", "transactions", columns=columns, where=where)
    cursor_mock.assert_has_calls(
        [
            call.execute(
                "SELECT name, yeet-ness FROM transactions WHERE power_level > 9000;"
            ),
            call.execute().fetchall(),
        ]
    )


def test_when_select_and_bad_db_name_then_error(db):
    with raises(DatabaseError) as raised_error:
        db.select("not_a_real_db", "transactions")
    assert (
        raised_error.value.args[0]
        == "Exception occurred while selecting data from 'not_a_real_db.transactions'."
        "  Database name specified is not an acceptable PyFynance database. "
        "Acceptable PyFynance databases include ['transactions']"
    )


def test_when_select_and_bad_table_name_then_error(db):
    with raises(DatabaseError) as raised_error:
        db.select("transactions", "not_a_real_db")
    assert (
        raised_error.value.args[0]
        == "Exception occurred while selecting data from 'transactions.not_a_real_db'"
        ".  Table name 'not_a_real_db' is not a known table for database "
        "'transactions'. Known tables are '['transactions']' "
    )
