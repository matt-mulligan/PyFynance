import datetime
import os
from decimal import Decimal

from mock import MagicMock, patch, call
from pytest import fixture, raises

from core.exceptions import TaskLoadTransactionsError
from schemas.ofx_banking_transaction import OFXBankingTransactionSchema
from tasks.task_load_transactions import LoadTransactionsTask


class TestLoadTransactionsTask:

    # ---- Test Fixtures ------------------------------

    @fixture
    def args(self):
        # research if there is a better way to do this
        class Args:
            def __init__(self):
                self.task_type = "load_transactions"
                self.institution = "MyBank"
                self.account = "CreditCard"
                self.runtime = datetime.datetime(2015, 2, 14, 10, 11, 12)

        return Args()

    @fixture
    def task(self, args):
        with patch(
            "os.path.abspath",
            MagicMock(
                return_value=os.sep.join(
                    ["BASE", "REPO", "PATH", "PyFynance", "core", "config.py"]
                )
            ),
        ):
            return LoadTransactionsTask(args)

    # ---- Test Data Objects --------------------------

    @staticmethod
    def pyfynance_tran01_data():
        return {
            "institution": "MyBank",
            "account": "CreditCard",
            "tran_id": "tran0001",
            "tran_type": "CREDIT",
            "amount": Decimal(-69.10),
            "narrative": "xbox.com.au subscription",
            "date_posted": "20190924180000",
            "date_processed": "20150214101112",
            "primary_rule_id": None,
            "supp_rule_ids": None,
        }

    @staticmethod
    def pyfynance_tran02_data():
        return {
            "institution": "MyBank",
            "account": "CreditCard",
            "tran_id": "tran0002",
            "tran_type": "DEBIT",
            "amount": Decimal(150000000.00),
            "narrative": "powerball winnings",
            "date_posted": "20190924180000",
            "date_processed": "20150214101112",
            "primary_rule_id": None,
            "supp_rule_ids": None,
        }

    @staticmethod
    def pyfynance_tran03_data():
        return {
            "institution": "MyBank",
            "account": "CreditCard",
            "tran_id": "tran0003",
            "tran_type": "CREDIT",
            "amount": Decimal(25000.60),
            "narrative": "Company co. - fortnightly pay",
            "date_posted": "20190924180000",
            "date_processed": "20150214101112",
            "primary_rule_id": None,
            "supp_rule_ids": None,
        }

    @staticmethod
    def ofx_tran01():
        data = {
            "fitid": "tran0001",
            "trntype": "CREDIT",
            "trnamt": Decimal(-69.10),
            "name": "xbox.com.au subscription",
            "dtposted": str(datetime.datetime(2019, 9, 24, 18, 0, 0)),
            "dtuser": str(datetime.datetime(2019, 9, 24, 18, 0, 0)),
        }
        return OFXBankingTransactionSchema().load(data)

    @staticmethod
    def ofx_tran02():
        data = {
            "fitid": "tran0002",
            "trntype": "DEBIT",
            "trnamt": Decimal(150000000.00),
            "memo": "powerball winnings",
            "dtposted": str(datetime.datetime(2019, 9, 24, 18, 0, 0)),
            "dtuser": str(datetime.datetime(2019, 9, 24, 18, 0, 0)),
        }
        return OFXBankingTransactionSchema().load(data)

    @staticmethod
    def ofx_tran03():
        data = {
            "fitid": "tran0003",
            "trntype": "CREDIT",
            "trnamt": Decimal(25000.60),
            "name": "Company co.",
            "memo": "fortnightly pay",
            "dtposted": str(datetime.datetime(2019, 9, 24, 18, 0, 0)),
            "dtuser": str(datetime.datetime(2019, 9, 24, 18, 0, 0)),
        }
        return OFXBankingTransactionSchema().load(data)

    @staticmethod
    def tran_no_name_memo():
        data = {
            "fitid": "tran0003",
            "trntype": "CREDIT",
            "trnamt": Decimal(25000.60),
            "dtposted": str(datetime.datetime(2019, 9, 24, 18, 0, 0)),
        }
        return OFXBankingTransactionSchema().load(data)

    def transactions(self):
        return [self.ofx_tran01(), self.ofx_tran02(), self.ofx_tran03()]

    # ---- Test Methods ------------------------------

    def test_when_init_the_correct_object_returned(self, args):
        task = LoadTransactionsTask(args)
        assert isinstance(task, LoadTransactionsTask)
        assert hasattr(task, "_args")
        assert hasattr(task, "_config")
        assert hasattr(task, "_db")
        assert hasattr(task, "_logger")
        assert hasattr(task, "_ofx_parser")
        assert hasattr(task, "_transactions")

    def test_when_repr_then_correct_str_returned(self, task):
        assert (
            task.__repr__()
            == "PyFynance.Tasks.LoadTransactionsTask(task_type=load_transactions, institution=MyBank, "
            "account=CreditCard, runtime=2015-02-14 10:11:12)"
        )

    def test_when_before_task_then_correct_methods_called(self, task):
        with patch.object(task, "_db", return_value=MagicMock()) as db_mock:
            task.before_task()
        db_mock.assert_has_calls([call.start_db("transactions")])

    def test_when_do_task_and_no_trans_in_db_then_load_correct_trans(self, task):
        trans = self.transactions()
        files_to_parse = [os.sep.join(["C:", "fake", "path", "file1.ofx"])]
        with patch("core.helpers.find_all_files", return_value=files_to_parse):
            with patch("services.ofx_parser.OFXParser.parse", return_value=trans):
                with patch("shutil.move", MagicMock()):
                    with patch("services.database.Database.select", return_value=[]):
                        with patch(
                            "services.database.Database.insert", MagicMock()
                        ) as db_insert_mock:
                            task.do_task()
        assert task._transactions == trans
        db_insert_mock.assert_has_calls(
            [
                call("transactions", "transactions", self.pyfynance_tran01_data()),
                call("transactions", "transactions", self.pyfynance_tran02_data()),
                call("transactions", "transactions", self.pyfynance_tran03_data()),
            ]
        )

    def test_when_do_task_and_some_trans_in_db_then_load_correct_trans(self, task):
        trans = self.transactions()
        files_to_parse = [os.sep.join(["C:", "fake", "path", "file1.ofx"])]
        with patch("core.helpers.find_all_files", return_value=files_to_parse):
            with patch("services.ofx_parser.OFXParser.parse", return_value=trans):
                with patch("shutil.move", MagicMock()):
                    with patch(
                        "services.database.Database.select",
                        return_value=[("MyBank", "CreditCard", "tran0002")],
                    ):
                        with patch(
                            "services.database.Database.insert", MagicMock()
                        ) as db_insert_mock:
                            task.do_task()
        assert task._transactions == [trans[0], trans[2]]
        db_insert_mock.assert_has_calls(
            [
                call("transactions", "transactions", self.pyfynance_tran01_data()),
                call("transactions", "transactions", self.pyfynance_tran03_data()),
            ]
        )
        assert (
            call("transactions", "transactions", self.pyfynance_tran02_data())
            not in db_insert_mock.mock_calls
        )

    def test_when_do_task_and_all_trans_in_db_then_load_no_trans(self, task):
        trans = self.transactions()
        files_to_parse = [os.sep.join(["C:", "fake", "path", "file1.ofx"])]
        with patch("core.helpers.find_all_files", return_value=files_to_parse):
            with patch("services.ofx_parser.OFXParser.parse", return_value=trans):
                with patch("shutil.move", MagicMock()):
                    with patch(
                        "services.database.Database.select",
                        return_value=[
                            ("MyBank", "CreditCard", "tran0001"),
                            ("MyBank", "CreditCard", "tran0002"),
                            ("MyBank", "CreditCard", "tran0003"),
                        ],
                    ):
                        with patch(
                            "services.database.Database.insert", MagicMock()
                        ) as db_insert_mock:
                            task.do_task()
        assert task._transactions == []
        assert (
            call("transactions", "transactions", self.pyfynance_tran01_data())
            not in db_insert_mock.mock_calls
        )
        assert (
            call("transactions", "transactions", self.pyfynance_tran02_data())
            not in db_insert_mock.mock_calls
        )
        assert (
            call("transactions", "transactions", self.pyfynance_tran03_data())
            not in db_insert_mock.mock_calls
        )

    def test_when_do_task_and_tran_no_name_memo_then_raise_error(self, task):
        files_to_parse = [os.sep.join(["C:", "fake", "path", "file1.ofx"])]
        error_msg = "Transaction does not have a memo or name attribute."
        with patch("core.helpers.find_all_files", return_value=files_to_parse):
            with patch(
                "services.ofx_parser.OFXParser.parse",
                return_value=[self.tran_no_name_memo()],
            ):
                with patch("shutil.move", MagicMock()):
                    with patch("services.database.Database.select", return_value=[]):
                        with raises(TaskLoadTransactionsError) as raised_error:
                            task.do_task()
        assert error_msg in raised_error.value.args[0]

    def test_when_after_task_then_correct_methods_called(self, task):
        passed = True
        with patch.object(task, "_db", return_value=MagicMock()) as db_mock:
            task.after_task(passed)
        db_mock.assert_has_calls([call.stop_db("transactions", commit=True)])

    def test_when_after_task_and_failed_then_coorect_methods_called(self, task):
        passed = False
        db_mock = MagicMock()
        fs_mock = MagicMock()
        task._db = db_mock
        task._fs = fs_mock
        task._input_files = ["file1.ofx"]

        task.after_task(passed)
        db_mock.assert_has_calls([call.stop_db("transactions", commit=False)])
        fs_mock.assert_has_calls(
            [
                call.move_file(
                    "file1.ofx",
                    os.sep.join(
                        [
                            "BASE",
                            "REPO",
                            "PATH",
                            "input",
                            "banking_transactions",
                            "error",
                            "file1.ofx_20150214101112",
                        ]
                    ),
                )
            ]
        )

    def test_when_do_task_and_no_files_then_raise_error(self, task):
        error_msg = (
            r"An error occurred during the do_task step of the 'PyFynance.Tasks.LoadTransactionsTask("
            r"task_type=load_transactions, institution=MyBank, account=CreditCard, runtime=2015-02-14 10:11:12)'."
            r"  No input ofx/qfx files found in input path "
        )
        with patch("core.helpers.find_all_files", return_value=[]):
            with raises(TaskLoadTransactionsError) as raised_error:
                task.do_task()
        assert error_msg in raised_error.value.args[0]
