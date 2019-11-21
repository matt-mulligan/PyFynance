import re


class CategorizationEngine:
    """
    The Categorisation Engine service is responsible for all categorisation decisions within PyFynance.

    The class accepts a rules object which it expects to be a list of rule objects that meet thh standards setout in
    the RuleSchema marshmallow class

    This API class provides public methods to allow flexibly categorization of any specific set or subset of rules
    or transactions
    """

    def __init__(self, rules, config):
        """
        The constructor method for the Categorization Engine class

        :param rules: a list of rules objects that meet the standard setout in the RuleSchema class
        :type rules: List
        """

        self._ruleset = rules
        self._config = config

    def categorize_transactions(self, transactions):
        """
        The public interface for the categorization class
        :param transactions:
        :return:
        """

        for index, transaction in enumerate(transactions):
            primary_rule_id, supp_rule_ids = self._categorize(transaction)
            transactions[index].primary_rule_id = primary_rule_id
            transactions[index].supp_rule_ids = supp_rule_ids

        return transactions

    def _categorize(self, transaction):
        """
        This private method will run the ruleset across the specified transaction and determine the best categorisation

        :param transaction: a transaction model object
        :return: returns a transaction model object with categorisation information added
        """

        rule_matches = []

        for rule in self._ruleset:
            rule_match = self._test_rule(rule, transaction)
            if rule_match:
                rule_matches.append(rule)

        return self._assess_rule_matches(rule_matches)

    def _test_rule(self, rule, transaction):
        """
        this private method will determine the correct rule testing method to call to assess rule matches for the
        given transaction and rule
        :param rule: a rule model object
        :param transaction: a transaction model object
        :return: boolean indicating if the rule was a match to the transaction
        """

        rule_method = {  # add these in config
            self._config.categorization_engine.operations.contains: self._test_rule_contains,
            self._config.categorization_engine.operations.starts_with: self._test_rule_starts_with,
            self._config.categorization_engine.operations.ends_with: self._test_rule_ends_with,
            self._config.categorization_engine.operations.regex: self._test_rule_regex,
            self._config.categorization_engine.operations.multi_contains: self._test_rule_multi_contains,
        }[rule.operation]

        return rule_method(rule, transaction)

    @staticmethod
    def _assess_rule_matches(matches):
        """
        this private method will sort through the rule matches for a given transaction and select the primary rule
        match as well as providing an ordered list of supplimentary rule matches.

        The categorisation engine performs rule sorting based on the following logic;
            - The rule with the highest confidence is selected as the primary rule
            - if two or more rules share the highest confidence rating then a random rule is selected as the winner
            (no idea how to do this better)
            - all other matched rules will be concatenated into aa string and returned as supplementary_rules_id
            - the supplimentary rule ids will also be ordered based on confidence
            - if no rule matches then None will be returned for primary and supplementary rule ids
            - if only one match then that rule will be the primary rule id and None returned for supplementary rule id

        :param matches: a list of rule objects to sort
        :type matches: List of Rule model objects
        :return: primary_rule_id, supp_rule_ids
        """

        if len(matches) == 0:
            return None, None

        if len(matches) == 1:
            return matches[0].id, None

        matches.sort(key=lambda rule: rule.confidence, reverse=True)
        primary_rule_id = matches[0].id
        supp_rule_ids = ",".join(map(lambda rule: rule.id, matches[1:]))
        return primary_rule_id, supp_rule_ids

    @staticmethod
    def _test_rule_contains(rule, transaction):
        """
        This pirvate method is responsible for testing rules with the operator of "contains"
        this method will check to see if the rule value is contained anywhere within the transaction narrative.\
        this test is case-insensitive. all values will be converted to lowercase before comparison is made
        this test will not attempt to trim any whitespace or excessive spacing

        :param rule: rule model object containing the rule operator, logic and categrisation
        :type rule: Model object

        :param transaction: data object containing transaction data
        :type transaction: Model Object
        """

        return True if rule.value.lower() in transaction.narrative.lower() else False

    @staticmethod
    def _test_rule_starts_with(rule, transaction):
        """
        This private method is responsible for testing rules with the operator of "begins_with"
        this method will check to see if the transaction narrative begins with the rule value
        this test is case-insensitive. all values will be converted to lowercase before comparison is made.
        this test will not attempt to trim any whitespace or excessive spacing

        :param rule: rule model object containing the rule operator, logic and categrisation
        :type rule: Model object

        :param transaction: data object containing transaction data
        :type transaction: Model Object
        """

        return transaction.narrative.lower().startswith(rule.value.lower())

    @staticmethod
    def _test_rule_ends_with(rule, transaction):
        """
        This pirvate method is responsible for testing rules with the operator of "ends_with"
        this method will check to see if the transaction narrative ends with the rule value
        this test is case-insensitive. all values will be converted to lowercase before comparison is made.
        this test will not attempt to trim any whitespace or excessive spacing

        :param rule: rule model object containing the rule operator, logic and categrisation
        :type rule: Model object

        :param transaction: data object containing transaction data
        :type transaction: Model Object
        """

        return transaction.narrative.lower().endswith(rule.value.lower())

    @staticmethod
    def _test_rule_regex(rule, transaction):
        """
        This pirvate method is responsible for testing rules with the operator of "regex"
        this method will run a regex search over the transaction.narrative for the regex provided in the rule_value
        and will return true if any match is found
        this test is case-sensitive. no value conversion is performed as this could affect the regex provided.
        this test will not attempt to trim any whitespace or excessive spacing

        :param rule: rule model object containing the rule operator, logic and categrisation
        :type rule: Model object

        :param transaction: data object containing transaction data
        :type transaction: Model Object
        """

        found = re.search(rule.value, transaction.narrative)
        return False if found is None else True

    @staticmethod
    def _test_rule_multi_contains(rule, transaction):
        """
        This pirvate method is responsible for testing rules with the operator of "multi_contains"
        This method will split the rule.value on the dash character (-) to obtain a list of search values.
        This method will only return true if all search values are found in transaction.narative.
        this test is case-insensitive. all values will be converted to lowercase before comparison is made.
        this test will not attempt to trim any whitespace or excessive spacing

        :param rule: rule model object containing the rule operator, logic and categrisation
        :type rule: Model object

        :param transaction: data object containing transaction data
        :type transaction: Model Object
        """

        search_values = rule.value.split("-")
        rule_passing = True

        for value in search_values:
            if value.lower() not in transaction.narrative.lower():
                rule_passing = False

        return rule_passing
