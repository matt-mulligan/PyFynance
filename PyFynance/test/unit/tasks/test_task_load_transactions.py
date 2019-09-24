import datetime
from decimal import Decimal

from mock import MagicMock, patch, call
from pytest import fixture, raises

from core.exceptions import TaskError
from tasks.task_load_transactions import LoadTransactionsTask


@fixture
def args():
    # research if there is a better way to do this
    class Args:
        def __init__(self):
            self.task_type = "load_transactions"
            self.institution = "MyBank"
            self.account = "CreditCard"
            self.runtime = datetime.datetime(2015, 2, 14, 10, 11, 12)
    return Args()


@fixture
def task(args):
    return LoadTransactionsTask(args)


@fixture
def tran01():
    tran = MagicMock(spec=["fitid", "trn_type", "amount", "name", "date_posted"])
    tran.fitid = "tran0001"
    tran.trn_type = "CREDIT"
    tran.amount = Decimal(-69.10)
    tran.name = "xbox.com.au subscription"
    tran.date_posted = datetime.datetime(2019, 9, 24, 20, 37, 12)
    return tran


@fixture
def tran01_data():
    return {
        "institution": "MyBank", "account": "CreditCard", "tran_id": "tran0001", "tran_type": "CREDIT",
        "amount": Decimal(-69.10), "narrative": "xbox.com.au subscription", "date_posted": "20190924203712"
    }


@fixture
def tran02():
    tran = MagicMock(spec=["fitid", "trn_type", "amount", "memo", "date_posted"])
    tran.fitid = "tran0002"
    tran.trn_type = "DEBIT"
    tran.amount = Decimal(150000000.00)
    tran.memo = "powerball winnings"
    tran.date_posted = datetime.datetime(2019, 9, 13, 21, 42, 55)
    return tran


@fixture
def tran02_data():
    return {
        "institution": "MyBank", "account": "CreditCard", "tran_id": "tran0002", "tran_type": "DEBIT",
        "amount": Decimal(150000000.00), "narrative": "powerball winnings", "date_posted": "20190913214255"
    }


@fixture
def tran03():
    tran = MagicMock(spec=["fitid", "trn_type", "amount", "name", "memo", "date_posted"])
    tran.fitid = "tran0003"
    tran.trn_type = "CREDIT"
    tran.amount = Decimal(25000.60)
    tran.name = "Company co."
    tran.memo = "fortnightly pay"
    tran.date_posted = datetime.datetime(2019, 9, 24, 18, 0, 0)
    return tran


@fixture
def tran03_data():
    return {
        "institution": "MyBank", "account": "CreditCard", "tran_id": "tran0003", "tran_type": "CREDIT",
        "amount": Decimal(25000.60), "narrative": "Company co. - fortnightly pay", "date_posted": "20190924180000"
    }


@fixture
def tran_no_name_memo():
    tran = MagicMock(spec=["fitid", "trn_type", "amount", "date_posted"])
    tran.fitid = "tran0003"
    tran.trn_type = "CREDIT"
    tran.amount = Decimal(25000.60)
    tran.date_posted = datetime.datetime(2019, 9, 24, 18, 0, 0)
    return tran


@fixture
def transactions(tran01, tran02, tran03):
    return [tran01, tran02, tran03]


def test_when_init_the_correct_object_returned(args):
    task = LoadTransactionsTask(args)
    assert isinstance(task, LoadTransactionsTask)
    assert hasattr(task, "_args")
    assert hasattr(task, "_config")
    assert hasattr(task, "_db")
    assert hasattr(task, "_logger")
    assert hasattr(task, "_ofx_parser")
    assert hasattr(task, "_transactions")


def test_when_repr_then_correct_str_returned(task):
    assert task.__repr__() == "PyFynance.Tasks.LoadTransactionsTask(task_type=load_transactions, institution=MyBank, " \
                              "account=CreditCard, runtime=2015-02-14 10:11:12)"


def test_when_before_task_then_correct_methods_called(task):
    with patch.object(task, "_db", return_value=MagicMock()) as db_mock:
        task.before_task()
    db_mock.assert_has_calls([call.start_db("transactions")])


def test_when_do_task_and_no_trans_in_db_then_load_correct_trans(task, transactions, tran01_data,
                                                                 tran02_data, tran03_data):
    files_to_parse = ["C:\\fake\\path\\file1.ofx"]
    with patch("core.helpers.find_all_files", return_value=files_to_parse):
        with patch("services.ofx_parser.OFXParser.parse", return_value=transactions):
            with patch("shutil.move", MagicMock()):
                with patch("services.database.Database.select", return_value=[]):
                    with patch("services.database.Database.insert", MagicMock()) as db_insert_mock:
                        task.do_task()
    assert task._transactions == transactions
    db_insert_mock.assert_has_calls([
        call("transactions", "transactions", tran01_data),
        call("transactions", "transactions", tran02_data),
        call("transactions", "transactions", tran03_data)
    ])


def test_when_do_task_and_some_trans_in_db_then_load_correct_trans(task, transactions, tran01_data,
                                                                   tran02_data, tran03_data):
    files_to_parse = ["C:\\fake\\path\\file1.ofx"]
    with patch("core.helpers.find_all_files", return_value=files_to_parse):
        with patch("services.ofx_parser.OFXParser.parse", return_value=transactions):
            with patch("shutil.move", MagicMock()):
                with patch("services.database.Database.select", return_value=[("MyBank", "CreditCard", "tran0002")]):
                    with patch("services.database.Database.insert", MagicMock()) as db_insert_mock:
                        task.do_task()
    assert task._transactions == [transactions[0], transactions[2]]
    db_insert_mock.assert_has_calls([
        call("transactions", "transactions", tran01_data),
        call("transactions", "transactions", tran03_data)
    ])
    assert call("transactions", "transactions", tran02_data) not in db_insert_mock.mock_calls


def test_when_do_task_and_all_trans_in_db_then_load_no_trans(task, transactions, tran01_data,
                                                                   tran02_data, tran03_data):
    files_to_parse = ["C:\\fake\\path\\file1.ofx"]
    with patch("core.helpers.find_all_files", return_value=files_to_parse):
        with patch("services.ofx_parser.OFXParser.parse", return_value=transactions):
            with patch("shutil.move", MagicMock()):
                with patch("services.database.Database.select", return_value=[("MyBank", "CreditCard", "tran0001"),
                                                                              ("MyBank", "CreditCard", "tran0002"),
                                                                              ("MyBank", "CreditCard", "tran0003")]):
                    with patch("services.database.Database.insert", MagicMock()) as db_insert_mock:
                        task.do_task()
    assert task._transactions == []
    assert call("transactions", "transactions", tran01_data) not in db_insert_mock.mock_calls
    assert call("transactions", "transactions", tran02_data) not in db_insert_mock.mock_calls
    assert call("transactions", "transactions", tran03_data) not in db_insert_mock.mock_calls


def test_when_do_task_and_tran_no_name_memo_then_raise_error(task, tran_no_name_memo):
    files_to_parse = ["C:\\fake\\path\\file1.ofx"]
    error_msg = "Transaction does not have a memo or name attribute.  The transaction has the following attributes " \
                "'dict_keys(['_mock_return_value', '_mock_parent', '_mock_name', '_mock_new_name', " \
                "'_mock_new_parent', '_mock_sealed', '_spec_class', '_spec_set', '_spec_signature', '_mock_methods', " \
                "'_mock_children', '_mock_wraps', '_mock_delegate', '_mock_called', '_mock_call_args', " \
                "'_mock_call_count', '_mock_call_args_list', '_mock_mock_calls', 'method_calls', '_mock_unsafe', " \
                "'_mock_side_effect', 'fitid', 'trn_type', 'amount', 'date_posted'])'"
    with patch("core.helpers.find_all_files", return_value=files_to_parse):
        with patch("services.ofx_parser.OFXParser.parse", return_value=[tran_no_name_memo]):
            with patch("shutil.move", MagicMock()):
                with patch("services.database.Database.select", return_value=[]):
                    with raises(TaskError) as raised_error:
                        task.do_task()
    assert raised_error.value.args[0] == error_msg


def test_when_after_task_then_correct_methods_called(task):
    with patch.object(task, "_db", return_value=MagicMock()) as db_mock:
        task.after_task()
    db_mock.assert_has_calls([call.stop_db("transactions")])


