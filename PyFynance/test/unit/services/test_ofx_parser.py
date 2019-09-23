import datetime
from decimal import Decimal

from mock import patch, call, MagicMock, mock_open
from pytest import fixture, raises

from core.exceptions import OFXParserError
from services.ofx_parser import OFXParser
from core.config import Configuration


@fixture
def config():
    return Configuration()


@fixture
def ofx_parser(config):
    return OFXParser(config)


@fixture
def raw_ofx():
    return """<OFX>
<BANKMSGSRSV1>
<STMTTRNRS>
<STMTRS>
<BANKTRANLIST>
<STMTTRN>
<TRNTYPE>DEBIT
<DTPOSTED>20190913000000
<TRNAMT>-19.66
<FITID>118896
<MEMO>memo_txt
</STMTTRN>
<STMTTRN>
<TRNTYPE>CREDIT
<DTPOSTED>20190912000000
<TRNAMT>200.00
<FITID>717166
<NAME>name_txt
</STMTTRN>
</BANKTRANLIST>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""


def test_when_init_then_ofx_parser_returned():
    fake_config = MagicMock()
    ofx_parser = OFXParser(fake_config)
    assert isinstance(ofx_parser, OFXParser)
    assert ofx_parser._config == fake_config


@patch("os.path.isfile", return_value=True)
def test_when_parse_and_banking_transactions_then_return_transations(isfile, ofx_parser, raw_ofx):
    mock_open_obj = mock_open(read_data=raw_ofx)
    with patch("builtins.open", mock_open_obj):
        transacions = ofx_parser.parse("banking_transactions", "fake/path/to/file.ofx")

    assert transacions[0].amount == Decimal("-19.66")
    assert transacions[0].date_posted == datetime.datetime(2019, 9, 13, 0, 0, 0)
    assert transacions[0].fitid == "118896"
    assert transacions[0].memo == "memo_txt"
    assert transacions[0].trn_type == "DEBIT"
    assert transacions[1].amount == Decimal("200.00")
    assert transacions[1].date_posted == datetime.datetime(2019, 9, 12, 0, 0, 0)
    assert transacions[1].fitid == "717166"
    assert transacions[1].name == "name_txt"
    assert transacions[1].trn_type == "CREDIT"


def test_when_parse_and_bad_object_type_then_raise_error(ofx_parser):
    with raises(OFXParserError) as error_msg:
        ofx_parser.parse("bad_object_type", "fake/path/to/file.ofx")
        assert "Object_type value bad_object_type is unknown. " in error_msg


@patch("os.path.isfile", return_value=False)
def test_when_parse_and_file_path_not_a_file_then_raise_error(isfile, ofx_parser):
    with raises(OFXParserError) as error_msg:
        ofx_parser.parse("banking_transactions", "fake/path/to/folder")
        assert "Path provided 'fake/path/to/folder' either does not exist or isnt a file" in error_msg


@patch("os.path.isfile", return_value=True)
def test_when_parse_and_file_not_ofx_or_qfx_then_raise_error(isfile, ofx_parser):
    with raises(OFXParserError) as error_msg:
        ofx_parser.parse("banking_transactions", "fake/path/to/bad/file.txt")
        assert "Path provided 'fake/path/to/bad/file.txt' is not an OFX/QFX file." in error_msg
