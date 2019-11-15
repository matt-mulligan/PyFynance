# PyFynance
A personal finance spending analysis tool

## Purpose
This python project is a personal finance tool created to help analyse your spending habits. It will attempt to 
categorise your spending so that it can present to you a view of how your spending has changed over time. Future 
editions will also add goals and user defined categorisations. currently the tool will only be able to read 
transactions from a file


## Current Version and Changelist
**Version 1.0**
* Basic project structure established
* Transaction reading now supported for QIF file format. Most financial organisations provide exports in this format


## How to use this program
**Supported Tasks**

below is the current list of supported/future tasks for PyFynance
* load_transactions
* analyse_transactions (future)
* set_goal (future)
* add_rules (future)


**Load Transactions**

To load transactions into PyFynance, simply download your QIF file from your financial organisation and place in the 
PyFynance/input/transactions folder.
Please note that the account name will be derived from the file name in the input folder. if you have multiple files 
for the same account, please place "--" after the account name in the filename

To run PyFynance load transactions code simply trigger the application with a task type of "load_transactions"
```bash
python -m PyFynance --task_type load_transactions
```

## Technologies Used
* Python 3.7
* Pipenv - virtual environment dependency management
* Marshmallow - object serialisation / deserialisation


## License
[GPL-3](https://choosealicense.com/licenses/gpl-3.0/) 