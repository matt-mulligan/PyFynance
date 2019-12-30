from mock import MagicMock, patch, call
from pytest import fixture, raises

from services.database.client import SqliteClient
from services.database.exception import SqliteClientException


class TestSqliteClient:

    # ---- Test Fixtures ------------------------------
    @fixture
    def client(self):
        return SqliteClient()

    @fixture()
    def connection_mock(self, cursor_mock):
        connection = MagicMock()
        connection.cursor().return_value = cursor_mock
        yield connection

    @fixture()
    def cursor_mock(self):
        sqlite_mock = MagicMock()
        return sqlite_mock

    # ---- Test Data Objects --------------------------
    @staticmethod
    def col_spec():
        return {"col_a": "string", "col_b": "int", "col_c": "string"}

    @staticmethod
    def primary_keys():
        return ["col_b", "col_c"]

    @staticmethod
    def insert_data():
        return {"col_a": "my_string", "col_b": 27, "col_c": "Sydney"}

    # ---- Test Methods ------------------------------
    def test_when_init_then_client_correctly_configured(self):
        client = SqliteClient()
        assert hasattr(client, "_logger")
        assert hasattr(client, "_connections")
        assert hasattr(client, "_cursors")
        assert hasattr(client, "_sql")

        assert type(client._connections) == dict
        assert type(client._connections) == dict
        assert client._sql == {
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

    def test_when_start_db_then_connection_cursor_created(
        self, client, connection_mock
    ):
        with patch("sqlite3.connect", return_value=connection_mock) as sqlite_mock:
            client.start_db("transactions", "transactions_db_path", in_memory=False)
            sqlite_mock.assert_has_calls([call("transactions_db_path")])
            assert client._connections == {"transactions": connection_mock}
            assert client._cursors == {"transactions": connection_mock.cursor()}

    def test_when_start_db_and_connection_already_exists_then_sqlite_not_called(
        self, client, connection_mock
    ):
        with patch("sqlite3.connect", return_value=connection_mock) as sqlite_mock:
            client._connections["transactions"] = "already_opened_connection"
            client.start_db("transactions", "transactions_db_path", in_memory=False)
            sqlite_mock.assert_not_called()

    def test_when_start_db_and_in_memory_then_in_memory_db_started(
        self, client, connection_mock
    ):
        with patch("sqlite3.connect", return_value=connection_mock) as sqlite_mock:
            client.start_db("transactions", "transactions_db_path", in_memory=True)
            sqlite_mock.assert_has_calls([call(":memory:")])

    def test_when_start_db_and_error_then_exception_raised(self, client):
        with patch(
            "sqlite3.connect", side_effect=Exception("BOO! - no DB for you!")
        ) as sqlite_mock:
            with raises(SqliteClientException) as raised_error:
                client.start_db("transactions", "transactions_db_path", in_memory=False)

            assert (
                raised_error.value.args[0]
                == "Exception occurred while starting database 'transactions' with path"
                " 'transactions_db_path' and in_memory=False.  BOO! - no DB for you!"
            )

    def test_when_stop_db_and_connection_open_and_commit_then_connection_committed_and_closed(
        self, client, connection_mock
    ):
        client._connections["transactions"] = connection_mock
        client.stop_db("transactions", commit=True)
        assert connection_mock.method_calls == [
            call.cursor(),
            call.commit(),
            call.close(),
        ]

    def test_when_stop_db_and_connection_open_and_not_commit_then_connection_closed(
        self, client, connection_mock
    ):
        client._connections["transactions"] = connection_mock
        client.stop_db("transactions", commit=False)
        assert connection_mock.method_calls == [call.cursor(), call.close()]

    def test_when_stop_db_and_connection_not_open_then_connection_not_closed(
        self, client, connection_mock
    ):
        log_mock = MagicMock()
        client._logger = log_mock
        client.stop_db("transactions", commit=True)
        warning_call = call.warning(
            "sqlite database connection 'transactions' is not currently open. "
            "skipping remaining execution of stop_db"
        )
        assert warning_call in log_mock.method_calls

    def test_when_stop_db_and_error_then_exception_raised(
        self, client, connection_mock
    ):
        connection_mock.close = MagicMock(
            side_effect=Exception("BAM! - client go bye-bye!")
        )
        client._connections["transactions"] = connection_mock

        with raises(SqliteClientException) as raised_error:
            client.stop_db("transactions", commit=True)

        assert (
            raised_error.value.args[0]
            == "Exception occurred while stopping database 'transactions' with commit "
            "set to True.  BAM! - client go bye-bye!"
        )

    def test_when_create_table_then_correct_sql_executed(self, client):
        with patch.object(client, "execute", return_value=MagicMock()) as execute_mock:
            client.create_table(
                "transactions", "transactions", self.col_spec(), self.primary_keys()
            )
        execute_mock.assert_has_calls(
            [
                call(
                    "transactions",
                    "CREATE TABLE IF NOT EXISTS transactions (col_a string, col_b int, col_c string, "
                    "PRIMARY KEY (col_b, col_c));",
                )
            ]
        )

    def test_when_insert_then_execute_called_with_correct_arguments(self, client):
        with patch.object(client, "execute", return_value=MagicMock()) as execute_mock:
            client.insert("transactions", "transactions", self.insert_data())
        execute_mock.assert_has_calls(
            [
                call(
                    "transactions",
                    "INSERT INTO transactions(col_a, col_b, col_c) VALUES(?, ?, ?);",
                    ("my_string", "27", "Sydney"),
                )
            ]
        )

    def test_when_insert_and_error_then_exception_raised(self, client):
        with patch.object(
            client, "execute", side_effect=Exception("WHACK! - error time")
        ):
            with raises(SqliteClientException) as raised_error:
                client.insert("transactions", "transactions", self.insert_data())
        assert (
            raised_error.value.args[0]
            == "Exception occurred while inserting data into "
            "'transactions.transactions'.  WHACK! - error time"
        )

    def test_when_select_and_columns_none_and_where_none_then_correct_sql_executed(
        self, client
    ):
        with patch.object(client, "execute", return_value=MagicMock()) as execute_mock:
            client.select("my_db_yo", "sick_table_brah", None, None)
        execute_mock.assert_has_calls(
            [call("my_db_yo", "SELECT * FROM sick_table_brah;")]
        )

    def test_when_select_and_columns_given_and_where_none_then_correct_sql_executed(
        self, client
    ):
        with patch.object(client, "execute", return_value=MagicMock()) as execute_mock:
            client.select("my_db_yo", "sick_table_brah", ["name", "age"], None)
        execute_mock.assert_has_calls(
            [call("my_db_yo", "SELECT name, age FROM sick_table_brah;")]
        )

    def test_when_select_and_columns_none_and_where_given_then_correct_sql_executed(
        self, client
    ):
        with patch.object(client, "execute", return_value=MagicMock()) as execute_mock:
            client.select("my_db_yo", "sick_table_brah", None, "age > 13")
        execute_mock.assert_has_calls(
            [call("my_db_yo", "SELECT * FROM sick_table_brah WHERE age > 13;")]
        )

    def test_when_select_and_columns_given_and_where_given_then_correct_sql_executed(
        self, client
    ):
        with patch.object(client, "execute", return_value=MagicMock()) as execute_mock:
            client.select("my_db_yo", "sick_table_brah", ["name", "age"], "age > 13")
        execute_mock.assert_has_calls(
            [call("my_db_yo", "SELECT name, age FROM sick_table_brah WHERE age > 13;")]
        )

    def test_when_select_and_exception_then_error_raised(self, client):
        with patch.object(
            client, "execute", side_effect=Exception("WHACK! - error time")
        ):
            with raises(SqliteClientException) as raised_error:
                client.select("my_db", "sick_table_brah", None, None)
        expected_error = (
            "Exception occurred while selecting data from 'my_db.sick_table_brah' for columns 'All' "
            "with where clause 'None'.  WHACK! - error time"
        )
        assert raised_error.value.args[0] == expected_error

    def test_when_update_then_correct_sql_executed(self, client):
        with patch.object(client, "execute", return_value=MagicMock()) as execute_mock:
            data = {"pet_name": "lucky", "pet_age": 4}
            primary_keys = {"name": "Matt", "age": 27}
            client.update("my_db_yo", "sick_table_brah", data, primary_keys)
        expected_sql = "UPDATE sick_table_brah SET pet_name = ?, pet_age = ? WHERE name = ? AND age = ?;"
        expected_data = ("lucky", "4", "Matt", "27")
        execute_mock.assert_has_calls([call("my_db_yo", expected_sql, expected_data)])

    def test_when_update_and_exception_then_error_raised(self, client):
        with patch.object(
            client, "execute", side_effect=Exception("WHACK! - error time")
        ):
            with raises(SqliteClientException) as raised_error:
                data = {"pet_name": "lucky", "pet_age": 4}
                primary_keys = {"name": "Matt", "age": 27}
                client.update("my_db_yo", "sick_table_brah", data, primary_keys)
        expected_error = "Exception occurred while updating data in 'my_db_yo.sick_table_brah'.  WHACK! - error time"
        assert raised_error.value.args[0] == expected_error

    def test_when_execute_and_no_data_then_correct_calls_to_cursor_made(
        self, client, cursor_mock
    ):
        client._cursors["my_db"] = cursor_mock
        client.execute("my_db", "sql to execute")
        cursor_mock.asser_has_calls([call.execute("sql to execute")])

    def test_when_execute_and_data_then_correct_calls_to_cursor_made(
        self, client, cursor_mock
    ):
        client._cursors["my_db"] = cursor_mock
        client.execute("my_db", "sql to execute", ("my", "data"))
        cursor_mock.asser_has_calls([call.execute("sql to execute", ("my", "data"))])
