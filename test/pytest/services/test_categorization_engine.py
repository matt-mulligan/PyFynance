import os
import unittest
from datetime import datetime
from decimal import Decimal

from mock import patch, call, MagicMock, mock_open
from pytest import fixture, raises

from core.exceptions import DatabaseError
from schemas.rules import RulesSchema
from schemas.transactions import TransactionSchema
from services.categorization_engine import CategorizationEngine
from services.database import Database


@fixture
def config():
    config = MagicMock()
    config.categorization_engine.operations.contains = "contains"
    config.categorization_engine.operations.starts_with = "starts_with"
    config.categorization_engine.operations.ends_with = "ends_with"
    config.categorization_engine.operations.regex = "regex"
    config.categorization_engine.operations.multi_contains = "multi_contains"
    return config


@fixture
def rule_contains():
    data = {
        "id": "RT00000001",
        "type": "base",
        "operation": "contains",
        "value": "pizza",
        "description": "rule to check for pizza",
        "confidence": 75,
        "category_id": "CB00000001",
    }
    return RulesSchema().load(data)


@fixture
def rule_contains_more_conf():
    data = {
        "id": "RT00000006",
        "type": "base",
        "operation": "contains",
        "value": "mama-mia",
        "description": "rule to check for my favourite restaurant",
        "confidence": 95,
        "category_id": "CB00000001",
    }
    return RulesSchema().load(data)


@fixture
def rule_starts_with():
    data = {
        "id": "RT00000002",
        "type": "base",
        "operation": "starts_with",
        "value": "sydney",
        "description": "rule to check purchases in sydney",
        "confidence": 80,
        "category_id": "CB00000002",
    }
    return RulesSchema().load(data)


@fixture
def rule_ends_with():
    data = {
        "id": "RT00000003",
        "type": "base",
        "operation": "ends_with",
        "value": "salary",
        "description": "rule to check for salary deposits",
        "confidence": 85,
        "category_id": "CB00000003",
    }
    return RulesSchema().load(data)


@fixture
def rule_regex():
    data = {
        "id": "RT00000004",
        "type": "base",
        "operation": "regex",
        "value": "(UBER|Uber|uber)",
        "description": "rule to check for uber trips",
        "confidence": 90,
        "category_id": "CB00000004",
    }
    return RulesSchema().load(data)


@fixture
def rule_multi_contains():
    data = {
        "id": "RT00000005",
        "type": "base",
        "operation": "multi_contains",
        "value": "pizza-hut",
        "description": "rule to check specifically for pizza hut transactions",
        "confidence": 95,
        "category_id": "CB00000005",
    }
    return RulesSchema().load(data)


@fixture
def tran_contains_matchable():
    data = {
        "institution": "my_bank",
        "tran_id": "tran-0001",
        "tran_type": "DEBIT",
        "amount": Decimal("12.34"),
        "narrative": "mama-mia pizza",
        "date_posted": "20191127000000",
        "date_processed": "20191127000000",
        "primary_rule_id": None,
        "supp_rule_ids": None,
    }
    return TransactionSchema().load(data)


@fixture
def tran_starts_with_matchable():
    data = {
        "institution": "my_bank",
        "tran_id": "tran-0002",
        "tran_type": "DEBIT",
        "amount": Decimal("22.43"),
        "narrative": "sydneys best ice cream",
        "date_posted": "20191127000000",
        "date_processed": "20191127000000",
        "primary_rule_id": None,
        "supp_rule_ids": None,
    }
    return TransactionSchema().load(data)


@fixture
def tran_ends_with_matchable():
    data = {
        "institution": "my_bank",
        "tran_id": "tran-0003",
        "tran_type": "CREDIT",
        "amount": Decimal("123456789.00"),
        "narrative": "boring job Co. - salary",
        "date_posted": "20191127000000",
        "date_processed": "20191127000000",
        "primary_rule_id": None,
        "supp_rule_ids": None,
    }
    return TransactionSchema().load(data)


@fixture
def tran_regex_matchable():
    data = {
        "institution": "my_bank",
        "tran_id": "tran-0004",
        "tran_type": "CREDIT",
        "amount": Decimal("43.32"),
        "narrative": "trip UBER eastwood",
        "date_posted": "20191127000000",
        "date_processed": "20191127000000",
        "primary_rule_id": None,
        "supp_rule_ids": None,
    }
    return TransactionSchema().load(data)


@fixture
def tran_multi_contains_matchable():
    data = {
        "institution": "my_bank",
        "tran_id": "tran-0005",
        "tran_type": "CREDIT",
        "amount": Decimal("43.32"),
        "narrative": "eastwood pizza hut delivery",
        "date_posted": "20191127000000",
        "date_processed": "20191127000000",
        "primary_rule_id": None,
        "supp_rule_ids": None,
    }
    return TransactionSchema().load(data)


def test_when_init_then_correct_instance_returned(rule_contains, config):
    categorization_engine = CategorizationEngine([rule_contains], config)

    assert categorization_engine._config == config
    assert categorization_engine._ruleset == [rule_contains]


def test_when_categorize_transactions_then_rule_contains_acts_correctly(
    config, rule_contains, tran_contains_matchable, tran_ends_with_matchable
):
    rules = [rule_contains]
    trans = [tran_contains_matchable, tran_ends_with_matchable]
    cat_eng = CategorizationEngine(rules, config)
    new_trans = cat_eng.categorize_transactions(trans)

    assert new_trans[0].primary_rule_id == "RT00000001"
    assert new_trans[1].primary_rule_id == "RB99999999"


def test_when_categorize_transactions_then_rule_starts_with_acts_correctly(
    config, rule_starts_with, tran_starts_with_matchable, tran_ends_with_matchable
):
    rules = [rule_starts_with]
    trans = [tran_starts_with_matchable, tran_ends_with_matchable]
    cat_eng = CategorizationEngine(rules, config)
    new_trans = cat_eng.categorize_transactions(trans)

    assert new_trans[0].primary_rule_id == "RT00000002"
    assert new_trans[1].primary_rule_id == "RB99999999"


def test_when_categorize_transactions_then_rule_ends_with_acts_correctly(
    config, rule_ends_with, tran_ends_with_matchable, tran_contains_matchable
):
    rules = [rule_ends_with]
    trans = [tran_ends_with_matchable, tran_contains_matchable]
    cat_eng = CategorizationEngine(rules, config)
    new_trans = cat_eng.categorize_transactions(trans)

    assert new_trans[0].primary_rule_id == "RT00000003"
    assert new_trans[1].primary_rule_id == "RB99999999"


def test_when_categorize_transactions_then_rule_regex_acts_correctly(
    config, rule_regex, tran_regex_matchable, tran_contains_matchable
):
    rules = [rule_regex]
    trans = [tran_regex_matchable, tran_contains_matchable]
    cat_eng = CategorizationEngine(rules, config)
    new_trans = cat_eng.categorize_transactions(trans)

    assert new_trans[0].primary_rule_id == "RT00000004"
    assert new_trans[1].primary_rule_id == "RB99999999"


def test_when_categorize_transactions_then_rule_multi_contains_acts_correctly(
    config, rule_multi_contains, tran_multi_contains_matchable, tran_contains_matchable
):
    rules = [rule_multi_contains]
    trans = [tran_multi_contains_matchable, tran_contains_matchable]
    cat_eng = CategorizationEngine(rules, config)
    new_trans = cat_eng.categorize_transactions(trans)

    assert new_trans[0].primary_rule_id == "RT00000005"
    assert new_trans[1].primary_rule_id == "RB99999999"


def test_when_categorize_transactions_and_multiple_matches_then_correct_rule_ids_returned(
    config, rule_contains, rule_contains_more_conf, tran_contains_matchable
):
    rules = [rule_contains, rule_contains_more_conf]
    trans = [tran_contains_matchable]
    cat_eng = CategorizationEngine(rules, config)
    new_trans = cat_eng.categorize_transactions(trans)

    assert new_trans[0].primary_rule_id == "RT00000006"
    assert new_trans[0].supp_rule_ids == "RT00000001"
