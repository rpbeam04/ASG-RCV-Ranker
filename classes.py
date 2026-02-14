import pandas as pd
import numpy as np

class Voter:
    # n_candidates includes 'No Confidence' as a candidate
    def __init__(self, voter_id: int, school: str, year: int, n_candidates: int):
        self.voter_id = voter_id
        self.school = school
        self.year = year
        self.n_candidates = n_candidates
        for i in range(1, n_candidates + 1):
            setattr(self, f'choice_{i}', None)

    def __str__(self):
        choices = [getattr(self, f'choice_{i}') for i in range(1, self.n_candidates + 1)]
        return f"Voter ID: {self.voter_id}, School: {self.school}, Year: {self.year}, Choices: {choices}"
    
    def set_choice(self, rank: int, candidate: str):
        if 1 <= rank <= self.n_candidates:
            setattr(self, f'choice_{rank}', candidate)
        else:
            raise ValueError(f"Rank must be between 1 and {self.n_candidates}")
        
    def get_choice(self, rank: int):
        if 1 <= rank <= self.n_candidates:
            return getattr(self, f'choice_{rank}')
        else:
            raise ValueError(f"Rank must be between 1 and {self.n_candidates}")
        
    def count_vote(self, eliminated: list[str], no_confidence_last: bool = False):
        """
        Counts the vote for the voter based on their choices and the list of eliminated candidates. If no_confidence_last is True, no choices after 'No Confidence' will be considered.
        
        :param self: Voter object
        :param eliminated: List of eliminated candidates
        :type eliminated: list[str]
        :param no_confidence_last: If True, no choices after 'No Confidence' will be considered
        :type no_confidence_last: bool
        :return: The candidate that the vote counts for, or None if no valid choices remain
        :rtype: str or None
        """
        for i in range(1, self.n_candidates + 1):
            choice = getattr(self, f'choice_{i}')
            if choice not in eliminated:
                return choice
            if no_confidence_last and choice.lower() == 'no confidence':
                break
        return None
    
    def count_choices(self, eliminated: list[str], no_confidence_last: bool = False):
        """
        Returns a list of the voter's choices in order of preference, excluding eliminated and duplicate candidates. If no_confidence_last is True, no choices after 'No Confidence' will be included.
        
        :param self: Voter object
        :param eliminated: List of eliminated candidates
        :type eliminated: list[str]
        :param no_confidence_last: If True, no choices after 'No Confidence' will be included
        :type no_confidence_last: bool
        :return: A list of the voter's choices in order of preference
        :rtype: list[str]
        """
        choices = []
        for i in range(1, self.n_candidates + 1):
            choice = getattr(self, f'choice_{i}')
            if choice not in eliminated and choice not in choices:
                choices.append(choice)
            if no_confidence_last and choice.lower() == 'no confidence':
                break
        return choices

class VoteCounter:
    def __init__(self, candidates: list[str]):
        self.candidates = candidates
        self.vote_counts = {candidate: 0 for candidate in candidates}

    def __str__(self):
        return f"Vote Counts: {self.vote_counts}"
    
    def count_votes(self, voters: list[Voter], eliminated: list[str], no_confidence_last: bool = False, reset_counts: bool = True):
        """
        Counts the votes for a list of voters based on their choices and the list of eliminated candidates. If no_confidence_last is True, no choices after 'No Confidence' will be considered.
        
        :param self: VoteCounter object
        :param voters: List of Voter objects
        :type voters: list[Voter]
        :param eliminated: List of eliminated candidates
        :type eliminated: list[str]
        :param no_confidence_last: If True, no choices after 'No Confidence' will be considered
        :type no_confidence_last: bool
        :param reset_counts: If True, resets the vote counts before counting
        :type reset_counts: bool
        """
        if reset_counts:
            self.vote_counts = {candidate: 0 for candidate in self.candidates}
        
        for voter in voters:
            choice = voter.count_vote(eliminated, no_confidence_last)
            if choice in self.vote_counts:
                self.vote_counts[choice] += 1
            elif choice is not None:
                print(f"Warning: Choice '{choice}' not in candidates list.")

        return self.vote_counts

    def count_choices(self, voters: list[Voter], eliminated: list[str], no_confidence_last: bool = False):
        """
        Returns a dataframe with the number of votes for each candidate at each rank, excluding eliminated candidates. If no_confidence_last is True, no choices after 'No Confidence' will be included.
        
        :param self: VoteCounter object
        :param voters: List of Voter objects
        :type voters: list[Voter]
        :param eliminated: List of eliminated candidates
        :type eliminated: list[str]
        :param no_confidence_last: If True, no choices after 'No Confidence' will be included
        :type no_confidence_last: bool
        :return: A dataframe with the number of votes for each candidate at each rank
        :rtype: pd.DataFrame
        """
        choice_counts = {candidate: [0] * len(self.candidates) for candidate in self.candidates}
        
        for voter in voters:
            choices = voter.count_choices(eliminated, no_confidence_last)
            for rank, choice in enumerate(choices, start=1):
                if choice in choice_counts:
                    choice_counts[choice][rank-1] += 1
                elif choice is not None:
                    print(f"Warning: Choice '{choice}' not in candidates list.")
        
        df = pd.DataFrame(choice_counts, index=[f'Rank {i}' for i in range(1, len(self.candidates) + 1)])
        return df

    def eliminate_candidate(self, prev_eliminated: list[str] = None):
        """
        Returns the candidate with the fewest votes to be eliminated. In case of a tie, follow the tiebreaker rules.
        
        :param self: VoteCounter object
        :param prev_eliminated: List of previously eliminated candidates for tiebreaker rules
        :type prev_eliminated: list[str]
        :return: The candidate with the fewest votes
        :rtype: str
        """
        min_votes = min(self.vote_counts.values())
        candidates_with_min_votes = [candidate for candidate, votes in self.vote_counts.items() if votes == min_votes]
        
        if len(candidates_with_min_votes) == 1:
            return candidates_with_min_votes[0]
        
        # Stand in tiebreaker
        else:
            return np.random.choice(candidates_with_min_votes)
        
class Election:
    def __init__(self, voters: list[Voter], candidates: list[str]):
        self.voters = voters
        self.candidates = candidates
        self.vote_counter = VoteCounter(candidates)
        self.eliminated_candidates = []
        self.last_round = 0

    def run_election(self, no_confidence_last: bool = False):
        """
        Runs the election using the RCV method until a winner is determined.
        
        :param self: Election object
        :param no_confidence_last: If True, no choices after 'No Confidence' will be considered
        :type no_confidence_last: bool
        :return: The winning candidate
        :rtype: str
        """
        self.eliminated_candidates = []
        self.last_round = 0

        while True:
            self.vote_counter.count_votes(self.voters, self.eliminated_candidates, no_confidence_last)
            self.last_round += 1
            
            total_votes = sum(self.vote_counter.vote_counts.values())
            for candidate, votes in self.vote_counter.vote_counts.items():
                if votes > total_votes / 2:
                    return candidate
            
            eliminated_candidate = self.vote_counter.eliminate_candidate(self.eliminated_candidates)
            self.eliminated_candidates.append(eliminated_candidate)

            if len(self.eliminated_candidates) == len(self.candidates) - 1:
                remaining_candidates = [candidate for candidate in self.candidates if candidate not in self.eliminated_candidates]
                return remaining_candidates[0] if remaining_candidates else None

    def get_round_vote_counts(self, round: int, no_confidence_last: bool = False):
        """
        Returns a datarame with the number of votes for each candidate at each rank for a specific round of the election, excluding eliminated candidates. This method can only be run after calling run_election(). If no_confidence_last is True, no choices after 'No Confidence' will be included.
        
        :param self: Election object
        :param round: The round number for which to get the vote counts
        :type round: int
        :param no_confidence_last: If True, no choices after 'No Confidence' will be included
        :type no_confidence_last: bool
        """
        if round < 1 or round > self.last_round:
            raise ValueError(f"Round must be between 1 and {self.last_round}")
        
        if self.last_round == 0:
            raise ValueError("Election has not been run yet. Please call run_election() first.")

        eliminated = self.eliminated_candidates[:round-1]
        return self.vote_counter.count_choices(self.voters, eliminated, no_confidence_last)
    
    def get_filtered_round_vote_counts(self, round: int, school: str = None, year: int = None, no_confidence_last: bool = False):
        """
        Returns a datarame with the number of votes for each candidate at each rank for a specific round of the election, filtered by school and/or year, and excluding eliminated candidates. This method can only be run after calling run_election(). If no_confidence_last is True, no choices after 'No Confidence' will be included.
        
        :param self: Election object
        :param round: The round number for which to get the vote counts
        :type round: int
        :param school: The school to filter by (optional)
        :type school: str or None
        :param year: The year to filter by (optional)
        :type year: int or None
        :param no_confidence_last: If True, no choices after 'No Confidence' will be included
        :type no_confidence_last: bool
        """
        if round < 1 or round > self.last_round:
            raise ValueError(f"Round must be between 1 and {self.last_round}")
        
        if self.last_round == 0:
            raise ValueError("Election has not been run yet. Please call run_election() first.")

        eliminated = self.eliminated_candidates[:round-1]
        
        filtered_voters = [
            voter for voter in self.voters 
            if (school is None or voter.school == school) 
            and (year is None or voter.year == year)
        ]
        
        return self.vote_counter.count_choices(filtered_voters, eliminated, no_confidence_last)
    
    def get_election_results(self):
        """
        Returns a dataframe with the first choice vote counts for each candidate in each round of the election, excluding eliminated candidates. This method can only be run after calling run_election().

        :param self: Election object
        :return: A dataframe with the first choice vote counts for each candidate in each round
        :rtype: pd.DataFrame
        """
        if self.last_round == 0:
            raise ValueError("Election has not been run yet. Please call run_election() first.")

        results = []
        for round in range(1, self.last_round + 1):
            eliminated = self.eliminated_candidates[:round-1]
            vote_counts = self.vote_counter.count_votes(self.voters, eliminated, no_confidence_last=False, reset_counts=False)
            results.append(vote_counts.copy())
        
        df = pd.DataFrame(results, index=[f'Round {i}' for i in range(1, self.last_round + 1)])
        return df
    
    def get_filtered_election_results(self, school: str = None, year: int = None):
        """
        Returns a dataframe with the first choice vote counts for each candidate in each round of the election, filtered by school and/or year, and excluding eliminated candidates. This method can only be run after calling run_election().
        
        :param self: Election object
        :param school: The school to filter by (optional)
        :type school: str or None
        :param year: The year to filter by (optional)
        :type year: int or None
        :return: A dataframe with the first choice vote counts for each candidate in each round
        :rtype: pd.DataFrame
        """
        if self.last_round == 0:
            raise ValueError("Election has not been run yet. Please call run_election() first.")

        results = []
        for round in range(1, self.last_round + 1):
            eliminated = self.eliminated_candidates[:round-1]
            filtered_voters = [
                voter for voter in self.voters 
                if (school is None or voter.school == school) 
                and (year is None or voter.year == year)
            ]
            vote_counts = self.vote_counter.count_votes(filtered_voters, eliminated, no_confidence_last=False, reset_counts=False)
            results.append(vote_counts.copy())
        
        df = pd.DataFrame(results, index=[f'Round {i}' for i in range(1, self.last_round + 1)])
        return df