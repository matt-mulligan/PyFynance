from decimal import Decimal

from mock import MagicMock
from pytest import fixture

from schemas.rules import RulesSchema
from schemas.transactions import TransactionSchema
from services.categorization_engine import CategorizationEngine


class TestCategorizationEngine:

    # ---- Test Fixtures ------------------------------

    @fixture
    def config(self):
        config = MagicMock()
        config.categorization_engine.operations.contains = "contains"
        config.categorization_engine.operations.starts_with = "starts_with"
        config.categorization_engine.operations.ends_with = "ends_with"
        config.categorization_engine.operations.regex = "regex"
        config.categorization_engine.operations.multi_contains = "multi_contains"
        return config

    # ---- Test Data Objects --------------------------

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    # ---- Test Methods ------------------------------

    def test_when_init_then_correct_instance_returned(self, config):
        rules = [self.rule_contains()]
        categorization_engine = CategorizationEngine(rules, config)

        assert categorization_engine._config == config
        assert categorization_engine._ruleset == rules

    def test_when_categorize_transactions_then_rule_contains_acts_correctly(
        self, config
    ):
        rules = [self.rule_contains()]
        trans = [self.tran_contains_matchable(), self.tran_ends_with_matchable()]
        cat_eng = CategorizationEngine(rules, config)
        new_trans = cat_eng.categorize_transactions(trans)

        assert new_trans[0].primary_rule_id == "RT00000001"
        assert new_trans[1].primary_rule_id == "RB99999999"

    def test_when_categorize_transactions_then_rule_starts_with_acts_correctly(
        self, config
    ):
        rules = [self.rule_starts_with()]
        trans = [self.tran_starts_with_matchable(), self.tran_ends_with_matchable()]
        cat_eng = CategorizationEngine(rules, config)
        new_trans = cat_eng.categorize_transactions(trans)

        assert new_trans[0].primary_rule_id == "RT00000002"
        assert new_trans[1].primary_rule_id == "RB99999999"

    def test_when_categorize_transactions_then_rule_ends_with_acts_correctly(
        self, config
    ):
        rules = [self.rule_ends_with()]
        trans = [self.tran_ends_with_matchable(), self.tran_contains_matchable()]
        cat_eng = CategorizationEngine(rules, config)
        new_trans = cat_eng.categorize_transactions(trans)

        assert new_trans[0].primary_rule_id == "RT00000003"
        assert new_trans[1].primary_rule_id == "RB99999999"

    def test_when_categorize_transactions_then_rule_regex_acts_correctly(self, config):
        rules = [self.rule_regex()]
        trans = [self.tran_regex_matchable(), self.tran_contains_matchable()]
        cat_eng = CategorizationEngine(rules, config)
        new_trans = cat_eng.categorize_transactions(trans)

        assert new_trans[0].primary_rule_id == "RT00000004"
        assert new_trans[1].primary_rule_id == "RB99999999"

    def test_when_categorize_transactions_then_rule_multi_contains_acts_correctly(
        self, config
    ):
        rules = [self.rule_multi_contains()]
        trans = [self.tran_multi_contains_matchable(), self.tran_contains_matchable()]
        cat_eng = CategorizationEngine(rules, config)
        new_trans = cat_eng.categorize_transactions(trans)

        assert new_trans[0].primary_rule_id == "RT00000005"
        assert new_trans[1].primary_rule_id == "RB99999999"

    def test_when_categorize_transactions_and_multiple_matches_then_correct_rule_ids_returned(
        self, config
    ):
        rules = [self.rule_contains(), self.rule_contains_more_conf()]
        trans = [self.tran_contains_matchable()]
        cat_eng = CategorizationEngine(rules, config)
        new_trans = cat_eng.categorize_transactions(trans)

        assert new_trans[0].primary_rule_id == "RT00000006"
        assert new_trans[0].supp_rule_ids == "RT00000001"
