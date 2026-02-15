import pandas as pd
from classes import Voter
import json
import re

def read_election_data(filepath: str):
    """
    Reads election data into classes from a CSV file downloaded from 'Cats on Campus.
    
    :param filepath: The path to the CSV file containing the election data.
    :type filepath: str
    :return: A list of Voter objects representing the election data and a list of candidates.
    :rtype: tuple[list[Voter], list[str]]
    """
    with open("Data/names.json", "r") as f:
        CANDIDATE_REPLACEMENTS = json.load(f)
    CANDIDATE_REPLACEMENTS = {k.lower(): v for k, v in CANDIDATE_REPLACEMENTS.items()}

    try:
        data = pd.read_csv(filepath)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None, None
    
    ID_COL = "User Id"
    N_CANDIDATES = 5   # 'No Confidence' counts as a candidate
    FIRST_CHOICE = "Please select your TOP choice for president/vice president ticket"
    SECOND_CHOICE = "Please select your SECOND choice for president/vice president ticket"
    THIRD_CHOICE = "Please select your THIRD choice for president/vice president ticket"
    FOURTH_CHOICE = "Please select your FOURTH choice for president/vice president ticket"
    FIFTH_CHOICE = "Please select your FIFTH choice for president/vice president ticket"
    CHOICE_COLUMNS = [FIRST_CHOICE, SECOND_CHOICE, THIRD_CHOICE, FOURTH_CHOICE, FIFTH_CHOICE]
    SCHOOL = "Please select your primary college of enrollment"
    YEAR = "Please select your expected graduation year"

    _cols = [ID_COL, SCHOOL, YEAR, "Submitted On"] + CHOICE_COLUMNS
    assert all(col in data.columns for col in _cols), f"Missing columns in the data. Required columns: {_cols}"
    data = data[_cols]

    all_voters = []
    for _, row in data.iterrows():
        submission_time = row["Submitted On"]
        submission_time = pd.to_datetime(submission_time, errors='coerce')
        voter_id = int(row[ID_COL])
        school = str(row[SCHOOL]).strip()
        year = re.search(r'\d{4}', str(row[YEAR]))
        year = int(year.group(0)) if year is not None else 0
        voter = Voter(voter_id, school, year, N_CANDIDATES, submission_time if not pd.isna(submission_time) else None)
        
        for i in range(1, N_CANDIDATES + 1):
            choice_col = CHOICE_COLUMNS[i-1]
            if choice_col in row:
                if pd.isna(row[choice_col]):
                    choice = None
                else:
                    choice = str(row[choice_col]).strip()
                    if choice.lower() in CANDIDATE_REPLACEMENTS:
                        choice = CANDIDATE_REPLACEMENTS[choice.lower()]
                voter.set_choice(i, choice)

        all_voters.append(voter)

    candidates = set()
    for voter in all_voters:
        for i in range(1, N_CANDIDATES + 1):
            choice = voter.get_choice(i)
            if choice and choice is not None:
                candidates.add(choice)

    return all_voters, list(candidates)

def remove_candidate(voters: list[Voter], candidate: str):
    """
    Removes a candidate from all voters' choices and replaces with None.

    :param voters: A list of Voter objects.
    :type voters: list[Voter]
    :param candidate: The name of the candidate to remove.
    :type candidate: str
    """
    for voter in voters:
        for i in range(1, voter.n_candidates + 1):
            if voter.get_choice(i) == candidate:
                voter.set_choice(i, None)
                break