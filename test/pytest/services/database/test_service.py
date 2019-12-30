import datetime
import os

from mock import MagicMock, patch, call
from pytest import fixture, raises

from services.database.service import Database
from services.database.exception import DatabaseServiceException


class TestDatabaseService:

    # ---- Test Fixtures ------------------------------
    @fixture
    def database(self, client_mock, config_mock):
        return Database(client_mock, config_mock)

    @fixture
    def client_mock(self):
        client_mock = MagicMock()
        return client_mock

    @fixture
    def config_mock(self):
        config_mock = MagicMock()
        config_mock.paths.db_path = os.path.sep.join(["base", "db", "path"])
        config_mock.database.db_names = ["my_db"]
        config_mock.database.tables = {"my_db": ["table_a", "table_b", "table_c"]}
        config_mock.database.column_specs = {
            "table_a": {"col_a": "text", "col_b": "integer"},
            "table_b": {"col_c": "decimal", "col_d": "text"},
            "table_c": {"col_e": "integer", "col_f": "decimal"},
        }
        config_mock.database.primary_keys = {
            "table_a": ["col_a"],
            "table_b": ["col_c", "col_d"],
            "table_c": ["col_f"],
        }
        return config_mock

    # ---- Test Data Objects --------------------------

    # ---- Test Methods ------------------------------
    def test_when_create_db_then_correct_calls_made_to_client(
        self, database, client_mock
    ):
        database.create_db("my_db", "/path/to/db")
        client_mock.assert_has_calls(
            [
                call.start_db("my_db", "/path/to/db"),
                call.create_table(
                    "my_db", "table_a", {"col_a": "text", "col_b": "integer"}, ["col_a"]
                ),
                call.create_table(
                    "my_db",
                    "table_b",
                    {"col_c": "decimal", "col_d": "text"},
                    ["col_c", "col_d"],
                ),
                call.create_table(
                    "my_db",
                    "table_c",
                    {"col_e": "integer", "col_f": "decimal"},
                    ["col_f"],
                ),
            ]
        )

    def test_when_start_db_and_current_true_then_correct_calls_made_to_client(
        self, database, client_mock
    ):
        database.start_db("my_db", current=True, create=False)
        client_mock.assert_has_calls(
            [
                call.start_db(
                    "my_db", os.sep.join(["base", "db", "path", "current", "my_db.db"])
                )
            ]
        )

    def test_when_start_db_and_current_false_then_correct_calls_made_to_client(
        self, database, client_mock
    ):
        with patch(
            "glob.glob", return_value=[os.sep.join(["path", "backup_db_name.db"])]
        ):
            database.start_db("my_db", current=False, create=False)
        client_mock.assert_has_calls(
            [
                call.start_db(
                    "my_db",
                    os.sep.join(["base", "db", "path", "backup", "backup_db_name.db"]),
                )
            ]
        )

    def test_when_start_db_and_create_true_then_correct_calls_made_to_client(
        self, database, client_mock
    ):
        database.start_db("my_db", current=True, create=True)
        client_mock.assert_has_calls(
            [
                call.start_db(
                    "my_db", os.sep.join(["base", "db", "path", "current", "my_db.db"])
                ),
                call.create_table(
                    "my_db", "table_a", {"col_a": "text", "col_b": "integer"}, ["col_a"]
                ),
                call.create_table(
                    "my_db",
                    "table_b",
                    {"col_c": "decimal", "col_d": "text"},
                    ["col_c", "col_d"],
                ),
                call.create_table(
                    "my_db",
                    "table_c",
                    {"col_e": "integer", "col_f": "decimal"},
                    ["col_f"],
                ),
            ]
        )

    def test_when_start_db_and_bad_db_name_then_error_raised(self, database):
        with raises(DatabaseServiceException) as raised_error:
            database.start_db("DERPY_DB")
        assert (
            raised_error.value.args[0]
            == "Database name specified 'DERPY_DB' is not an acceptable PyFynance "
            "database. Acceptable PyFynance databases include ['my_db']"
        )

    def test_when_stop_db_and_commit_false_then_correct_calls_made_to_client(
        self, database, client_mock
    ):
        database.stop_db("my_db", commit=False)
        client_mock.assert_has_calls([call.stop_db("my_db", False)])

    def test_when_stop_db_and_commit_true_then_correct_calls_made_to_client(
        self, database, client_mock
    ):
        with patch(
            "core.helpers.get_current_time_string", return_value="20191230194218"
        ):
            with patch("shutil.copyfile", return_value=MagicMock()) as copyfile_mock:
                database.stop_db("my_db", commit=True)
        client_mock.assert_has_calls([call.stop_db("my_db", True)])
        copyfile_mock.assert_has_calls(
            [
                call(
                    os.sep.join(["base", "db", "path", "current", "my_db.db"]),
                    os.sep.join(
                        ["base", "db", "path", "backup", "my_db_20191230194218.db"]
                    ),
                )
            ]
        )

    def test_when_select_then_correct_calls_made_to_client(self, database, client_mock):
        database.select("my_db", "table_a", None, None)
        client_mock.assert_has_calls([call.select("my_db", "table_a", None, None)])

    def test_when_insert_then_correct_calls_made_to_client(self, database, client_mock):
        database.insert("my_db", "table_a", {"name": "Matt"})
        client_mock.assert_has_calls(
            [call.insert("my_db", "table_a", {"name": "Matt"})]
        )

    def test_when_update_then_correct_calls_made_to_client(self, database, client_mock):
        database.update("my_db", "table_a", {"name": "Matt"}, {"age": 26})
        client_mock.assert_has_calls(
            [call.update("my_db", "table_a", {"name": "Matt"}, {"age": 26})]
        )
