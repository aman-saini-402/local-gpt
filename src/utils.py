import csv
import os
from datetime import datetime, date

import streamlit as st
import yaml

# Load project settings
with open("setup.yaml", "r") as file:
    config = yaml.load(file, yaml.Loader)


def clear_chat() -> None:
    st.session_state["messages"] = []
    st.session_state["feedback"] = []
    st.session_state["log_success"] = []


def log_text_convo() -> None:
    """
    Save a less detailed chat history with only inputs and outputs
    """
    # Check if the log file exists
    if not os.path.exists("conversations.csv"):
        with open("conversations.csv", 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["username", "time", "user_input", "output"])
            writer.writeheader()

    with open("conversations.csv", 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["username", "time", "user_input", "output"])
        writer.writerow({
            'username': st.session_state["username"],
            'time': datetime.now(),
            'user_input': st.session_state["messages"][-1][0],
            'output': st.session_state["messages"][-1][1]
        })


def log_convo() -> None:
    """
    Function to save chat history to a CSV file
    """
    # get log file name
    filename = "chat_log/chat_log" + f"_{date.today()}" + ".csv"
    fieldnames = ["username", "time", "user_input", "output", "feedback", "model_name",
                  "model_temperature", "chat_history_window", "system_prompt"]

    # Check if the log file exists
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    # log inputs
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if len(st.session_state["log_success"]) == (len(st.session_state["messages"]) - 1):
            # All previous interactions were successfully logged
            writer.writerow({
                'username': st.session_state["username"],
                'time': datetime.now(),
                'user_input': st.session_state["messages"][-1][0],
                'output': st.session_state["messages"][-1][1],
                'feedback': st.session_state["feedback"][-1],
                'model_name': st.session_state["model_name"],
                'model_temperature': st.session_state["model_temperature"],
                'chat_history_window': config["CHAT_HISTORY_WINDOW"],
                'system_prompt': st.session_state["system_prompt"]
            })
            st.session_state["log_success"].append(1)
        elif (len(st.session_state["messages"])) == len(st.session_state["feedback"]):
            # User didn't give feedback in previous messages but finally gives one
            logged = len(st.session_state["log_success"])
            to_log = len(st.session_state["feedback"]) - logged
            for i in range(logged, logged + to_log):
                writer.writerow({
                    'username': st.session_state["username"],
                    'time': datetime.now(),
                    'user_input': st.session_state["messages"][i][0],
                    'output': st.session_state["messages"][i][1],
                    'feedback': st.session_state["feedback"][i],
                    'model_name': st.session_state["model_name"],
                    'model_temperature': st.session_state["model_temperature"],
                    'chat_history_window': config["CHAT_HISTORY_WINDOW"],
                    'system_prompt': st.session_state["system_prompt"]
                })
                st.session_state["log_success"].append(1)
        else:
            # User didn't give feedback in previous messages and one of the next message didn't require feedback
            logged = len(st.session_state["log_success"])
            to_log = len(st.session_state["messages"]) - logged
            for i in range(logged, logged + int(to_log)):
                writer.writerow({
                    'username': st.session_state["username"],
                    'time': datetime.now(),
                    'user_input': st.session_state["messages"][i][0],
                    'output': st.session_state["messages"][i][1],
                    'feedback': "NaN",
                    'model_name': st.session_state["model_name"],
                    'model_temperature': st.session_state["model_temperature"],
                    'chat_history_window': config["CHAT_HISTORY_WINDOW"],
                    'system_prompt': st.session_state["system_prompt"]
                })
                st.session_state["log_success"].append(1)


def collect_feedback(feedback: bool) -> None:
    # Check if user gave feedback the last time
    x = (len(st.session_state["messages"]) - 1) - len(st.session_state["feedback"])
    if x == 0:
        st.session_state["feedback"].append(feedback)
    else:
        st.session_state["feedback"].extend(["NaN"] * int(x))
        st.session_state["feedback"].append(feedback)
    log_convo()
