# Leetcode-Tracker
This python script tracks the rating of user with given username.
- The usernames must be present in a csv file, the columns should be `Enrolment Number`, `Name`, `Leetcode ID`
- You can set the time period between which you want to track the user by modifying START_DATE and END_DATE variable
- You can also set a threshold for number of contests missed in that period, if number of misses are greater than threshold then name will be included in weak coder list.

`main.py` contains multi-threaded approach while `sequential.py` is a sequential code.

## Steps to execute:
- Clone the repo `git clone https://github.com/thegeek13242/Leetcode-Tracker`
- Create a virtual environment(optional) `python -m venv venv`
- `pip install -r requirements.txt`
- `python main.py`
