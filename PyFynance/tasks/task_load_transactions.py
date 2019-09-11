from tasks.task_base import BaseTask


class LoadTransactionsTask(BaseTask):
    """
    This task manages the ingestion of transactions into the PyFynance database
    """

    def __init__(self):
        super(LoadTransactionsTask, self).__init__()

    def before_task(self):
        """
        this before task manages all setup activities required by this task to perform its action
        :return:
        """

        # setup transaction DB
        pass

    def do_task(self):
        """
        this do task manages all of the actions this task runs
        :return:
        """

        # parse transaction file to python objects
        # get transactions from transactions DB
        # determine which transactions are new
        # categorise new transactions
        # write back new transactions to DB
        pass

    def after_task(self):
        """
        this do task manages all of the teardown tasks that this task performs after its action is done
        :return:
        """

        # commit and close transaction DB
        pass
