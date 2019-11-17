class CategorizationEngine:
    """
    The Categorisation Engine service is responsible for all categorisation decisions within PyFynance.

    The class accepts a rules object which it expects to be a list of rule objects that meet thh standards setout in
    the RuleSchema marshmallow class

    This API class provides public methods to allow flexibly categorization of any specific set or subset of rules
    or transactions
    """

    def __init__(self, rules):
        """
        The constructor method for the Categorization Engine class

        :param rules: a list of rules objects that meet the standard setout in the RuleSchema class
        :type rules: List
        """

        self._ruleset = rules

    def categorize_transactions(self, transactions):
        """
        The public interface for the categorization class
        :param transactions:
        :return:
        """

        return None
