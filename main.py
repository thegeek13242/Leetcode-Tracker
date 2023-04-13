import requests
import pandas as pd
from pprint import pprint
import datetime
import concurrent.futures


LEETCODE_URL = "https://leetcode.com/graphql/"
START_DATE = "01/03/2023"
END_DATE = "31/03/2023"
THRESHOLD_CONTESTS = 3
DATA_FILE = "usernames.csv"

# convert the start date to timestamp
start_date = datetime.datetime.strptime(START_DATE, "%d/%m/%Y").timestamp()
end_date = datetime.datetime.strptime(END_DATE, "%d/%m/%Y").timestamp()
# read data from csv
df = pd.read_csv(DATA_FILE)
# get the list of usernames
usernames = df["Leetcode ID"].tolist()
df.set_index("Leetcode ID", inplace=True)


body = """
\n    query userContestRankingInfo($username: String!) 
{\n  userContestRanking(username: $username) 
{\n    attendedContestsCount\n    rating\n    globalRanking\n    totalParticipants\n    topPercentage\n    
badge {\n      name\n    }\n  }\n  userContestRankingHistory(username: $username) 
{\n    attended\n    trendDirection\n    problemsSolved\n    totalProblems\n    finishTimeInSeconds\n    
rating\n    ranking\n    contest {\n      title\n      startTime\n    }\n  }\n}\n 
"""

# create a pandas dataframe to store the results
dataframe = pd.DataFrame(columns=["Enrolment Number", "Name", "Leetcode ID", "Rating"])
action_dataframe = pd.DataFrame(
    columns=[
        "Enrolment Number",
        "Name",
        "Leetcode ID",
        "Rating",
        "Contests Missed",
        "Number of contest missed",
    ]
)

def fetch_data(username):
    result_row = df.loc[username].tolist()
    variables = {"username": username}
    request_body = {"query": body, "variables": variables}
    headers = {
        "Referer": "https://leetcode.com/" + username + "/",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token,
    }

    # send the request
    response = session.post(LEETCODE_URL, json=request_body, headers=headers)
    # get the response data
    data = response.json()
    # get the userContestRankingInfo

    result_row.append(username)
    if data["data"]["userContestRanking"] is not None:
        result_row.append(data["data"]["userContestRanking"]["rating"])
        # append the result row to the dataframe
        dataframe.loc[len(dataframe)] = result_row

        # check if the user has missed contests after start date
        contest_history = data["data"]["userContestRankingHistory"]
        contest_missed = []
        for contest in contest_history:
            if contest["contest"]["startTime"] > start_date and contest["contest"]["startTime"] < end_date:
                action_row = result_row.copy()
                if not contest["attended"]:
                    contest_missed.append(contest["contest"]["title"])
        str = ""
        for contest in contest_missed:
            str += contest + ", "
        action_row.append(str)
        action_row.append(len(contest_missed))
        print(action_row)
        action_dataframe.loc[len(action_dataframe)] = action_row
    else:
        result_row.append(0)
        dataframe.loc[len(dataframe)] = result_row
        action_row = result_row.copy()
        action_row.append("No Contest Given")
        action_row.append(20)
        print(action_row)
        action_dataframe.loc[len(action_dataframe)] = action_row

with requests.Session() as session:
    csrf_token = session.get("https://leetcode.com/").cookies["csrftoken"]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(fetch_data, usernames)


dataframe.sort_values(by=["Rating"], inplace=True, ascending=False)
action_dataframe.sort_values(
    by=["Number of contest missed"], inplace=True, ascending=False
)
# save the dataframe to csv
dataframe.to_csv("rating.csv", index=False)
action_dataframe.to_csv("misses.csv", index=False)

weak_coders = action_dataframe[action_dataframe["Number of contest missed"] >= THRESHOLD_CONTESTS].copy()
weak_coders.sort_values(
    by=["Number of contest missed"], inplace=True, ascending=False
)
weak_coders.to_csv("weak_coders.csv", index=False)
