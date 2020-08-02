# CS2102 Project - LumiRandom
## Introduction
This project was implement as part of CS2102(Introduction to database) module that I took while in NUS. Our project topic was to emulate a student management system, with a locally deployed database. Our database of choice for this project is `psql`, and the backend language used is `Python Flask`.

## Group Members
1. Joel Chang
2. Clement Cheng
3. Chan Jing Hong
4. Fedrick

## ER Diagram
![ER Diagram](https://github.com/joelczk/CS2102-Project/blob/v1.2/ER%20Diagram.jpg)

## Database Requirements:
1. There are at least 15 entity sets and relationship sets
2. There is at least 1 weak entity set
3. There is at least 3 non-trivial application constraints that cannot be cannot be enforced using column/table\
constraints and must be enforced using triggers
4. There is at least 3 complex queries on data, with at least 1 `Group By` or `join` clause that produces 1 dangling tuple

## Requirements
1. Python 3
2. PSQL (Please refer to [here](https://www.guru99.com/download-install-postgresql.html) on installation process for PSQL)

## Setting Up
Go to the `SQL` directory and run all the SQL queries on your PSQL server to set up the database.
Please remember to set the following into your PSQL server:
```
set timezone to 'GMT +8';
```

```bash
$ git clone https://www.github.com/joelczk/CS2102-Project
$ cd CS2102-Project
$ pip3 install -R requirements.txt
```

## Usage
``` bash
$ cd CS2102-Project
$ python3 start.py
```

## User Accounts
1. Students:

username: Any value from `S00001` to `S01000`

password : `password`

2. Professors:

username: Any value from `P00001` to `P00100`

password : `password`


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

To refer to a more detailed report, please refer to [here](https://github.com/joelczk/CS2102-Project/blob/master/report/CS2102ProjectReport.pdf)
