"""
The services package aims to provide API interfaces for all external entities that PyFynance interacts with.

It is a specific design aim for this project that all modules produced for this package are built as standalone APIs
so that they may be easily extened and reused in other projects as standard code. This means that all service
modules should be devoid of business logic for PyFynance and should aim to only interact with the external service
in a generic but structured way.

Current services being maintained within this package are the database module (API interface for sqlite3) and the
ofx_parser module (logical parser for files meeting the ofx specification)
"""