"""
The resources.databases module holds all of the database files that PyFynance relies on and updates.

The module holds both the current state and backup states of each of the database and is stored in sqlite3 file format.

Additional databases can be stored here by extending the functionality of the services.database module and by
updating the list of acceptable databases and tables in the configuration object
"""