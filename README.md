# ER Diagram
![ER Diagram](https://github.com/joelczk/CS2102-Project/blob/v1.1/ER%20Diagram.jpg)

# Setup

Please download the LumiRandom folder\
Run terminal/cmd and cd into LumiRandom directory\
Run python start.py\
Connect to localhost:5300 in Browser

Default Account ID and Password for LumiRandom\
**Account ID**\
For Students: Choose any from S00001 - S01000\
For Profs: Choose any from P00001 - P00100\
**Password**\
For All: password\
**SQLite Database**\
To view database, please download DB browser for SQL Lite\
Load site.db into DB Browser\
**PSQL Database**\
If you are using psql database for testing, please remember to include the following code into psql:
```
set timezone to 'GMT +8';
```
**Code Requirements**\
Please refer to requirements.txt for the list of dependencies needed\
Please refer to runtime.txt for the python version used\

**Requirements**\
1.The total number of entity sets and relationship sets must be at least 15\
2.There must be at least 1 weak entity set\
3.There must be at least three non-trivial application constraints that cannot be enforced using column/table\
constraints and must be enforced using triggers\
4.There must be at least 3 complex queries on data(Need to use at least 1 Group By clause or 1 join clause that produces a dangling tuple)


