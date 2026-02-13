import pandas as pd
from classes import Voter
import re

def read_election_data(filepath: str):
    """
    Reads election data into classes from a CSV file downloaded from 'Cats on Campus.
    
    :param filepath: The path to the CSV file containing the election data.
    :type filepath: str
    :return: A list of Voter objects representing the election data.
    :rtype: list[Voter]
    """
    try:
        data = pd.read_csv(filepath)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None
    
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

    all_voters = []
    for _, row in data.iterrows():
        voter_id = int(row[ID_COL])
        school = str(row[SCHOOL]).strip()
        year = re.search(r'\d{4}', str(row[YEAR]))
        year = int(year.group(0)) if year is not None else None
        voter = Voter(voter_id, school, year, N_CANDIDATES)
        
        for i in range(1, N_CANDIDATES + 1):
            choice_col = CHOICE_COLUMNS[i-1]
            if choice_col in row:
                choice = str(row[choice_col]).strip()
                voter.set_choice(i, choice)

        all_voters.append(voter)

    return all_voters