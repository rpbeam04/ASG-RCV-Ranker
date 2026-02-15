import pandas as pd
import numpy as np
import copy
from pprint import pprint

class Voter:
    # n_candidates includes 'No Confidence' as a candidate
    def __init__(self, voter_id: int, school: str, year: int, n_candidates: int, timestamp: pd.Timestamp = None):
        self.voter_id = voter_id
        self.school = school
        self.year = year
        self.n_candidates = n_candidates
        self.timestamp = timestamp
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
            if choice is not None:
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
            if choice is None:
                continue
            if choice not in eliminated and choice not in choices:
                choices.append(choice)
            if no_confidence_last and choice.lower() == 'no confidence':
                break
        return choices

class VoteCounter:
    def __init__(self, candidates: list[str]):
        self.candidates = candidates
        self.vote_counts = {candidate: 0 for candidate in candidates}
        self.choice_counts = {candidate: [0] * len(candidates) for candidate in candidates}

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
            self.vote_counts = {candidate: 0 for candidate in self.candidates if candidate not in eliminated}
            self.choice_counts = {candidate: [0] * len(self.candidates) for candidate in self.candidates if candidate not in eliminated}
        
        for voter in voters:
            choice = voter.count_vote(eliminated, no_confidence_last)
            if choice in self.vote_counts:
                self.vote_counts[choice] += 1
            elif choice is not None:
                pass
                # print(f"Warning: Choice '{choice}' not in candidates list.")

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
        choice_counts = {candidate: [0] * (len(self.candidates) - len(eliminated)) for candidate in self.candidates if candidate not in eliminated}
        
        for voter in voters:
            choices = voter.count_choices(eliminated, no_confidence_last)
            for rank, choice in enumerate(choices, start=1):
                if choice in choice_counts:
                    try:
                        choice_counts[choice][rank-1] += 1
                    except IndexError:
                        print(f"Warning: Rank {rank} for choice '{choice}' exceeds the number of candidates. Voter ID: {voter.voter_id}")
                elif choice is not None:
                    pass
                    print(f"Warning: Choice '{choice}' not in candidates list.")
        
        self.choice_counts = choice_counts

        df = pd.DataFrame(choice_counts, index=[f'Rank {i}' for i in range(1, len(self.candidates) - len(eliminated) + 1)])
        df = df.transpose()
        df = df.sort_values(by='Rank 1', ascending=False)
        return df

    def eliminate_candidate(self, voters: list[Voter], prev_eliminated: list[str] = None):
        """
        Returns the candidate with the fewest votes to be eliminated. In case of a tie, follow the tiebreaker rules.
        
        :param self: VoteCounter object
        :param voters: List of Voter objects
        :type voters: list[Voter]
        :param prev_eliminated: List of previously eliminated candidates for tiebreaker rules
        :type prev_eliminated: list[str]
        :return: The candidate with the fewest votes
        :rtype: str
        """
        assert all(candidate not in self.vote_counts for candidate in (prev_eliminated or [])), "Eliminated candidates should not be in vote counts."

        round = len(prev_eliminated) + 1 if prev_eliminated is not None else 1

        min_votes = min(self.vote_counts.values())
        candidates_with_min_votes = [candidate for candidate, votes in self.vote_counts.items() if votes == min_votes and candidate not in (prev_eliminated or [])]
        
        if len(candidates_with_min_votes) == 1:
            return candidates_with_min_votes[0]
        
        """
        Tiebreaker rules:
        When two or more tickets have the same number of votes and are either subject to elimination or victory, these tiebreaker rules apply;
        1. When two or more tickets are tied for elimination or victory, resolve the tie as follows;
        2. Compare the number of second-choice votes each tied ticket received in the current round.
        3. Compare third-choice votes, then fourth-choice votes, etc., until the tie is broken.
        4. Compare the number of first-choice votes each tied ticket received in the previous round.
        5. Repeat this comparison for earlier rounds in reverse order until the tie is broken.
        6. Compare second-choice votes in the previous round, then third-choice votes, etc., for each earlier round, until the tie is broken.
        7. In a tie for elimination, eliminate the remaining tied candidates. In a tie for victory, there will be a runoff.        
        """
        # choices for current round
        self.count_choices(voters, prev_eliminated or [])
        for choice_rank in range(2, len(self.candidates) + 1):
            # Only consider candidates with enough ranks
            valid_candidates = [c for c in candidates_with_min_votes if choice_rank-1 < len(self.choice_counts[c])]
            if not valid_candidates:
                continue
            min_choice_votes = min(self.choice_counts[c][choice_rank-1] for c in valid_candidates)
            candidates_with_min_choice_votes = [c for c in valid_candidates if self.choice_counts[c][choice_rank-1] == min_choice_votes]
            if len(candidates_with_min_choice_votes) == 1:
                return candidates_with_min_choice_votes[0]
            candidates_with_min_votes = candidates_with_min_choice_votes

        # choices for previous rounds
        for choice_rank in range(1, len(self.candidates) + 1):
            for prev_round in range(round - 1, 0, -1):
                self.count_choices(voters, prev_eliminated[:prev_round] or [])
                # Only consider candidates with enough ranks
                valid_candidates = [c for c in candidates_with_min_votes if choice_rank-1 < len(self.choice_counts[c])]
                if not valid_candidates:
                    continue
                min_choice_votes = min(self.choice_counts[c][choice_rank-1] for c in valid_candidates)
                candidates_with_min_choice_votes = [c for c in valid_candidates if self.choice_counts[c][choice_rank-1] == min_choice_votes]
                if len(candidates_with_min_choice_votes) == 1:
                    return candidates_with_min_choice_votes[0]
                candidates_with_min_votes = candidates_with_min_choice_votes
        
        # If still tied, return None for now
        return None

class Election:
    def __init__(self, voters: list[Voter], candidates: list[str], no_confidence_last: bool = False):
        self.voters = voters
        self.candidates = candidates
        self.no_confidence_last = no_confidence_last
        self.vote_counter = VoteCounter(candidates)
        self.eliminated_candidates = []
        self.last_round = 0
        self.winner = None

    def run_election(self):
        """
        Runs the election using the RCV method until a winner is determined.
        
        :param self: Election object
        :return: The winning candidate
        :rtype: str
        """
        self.eliminated_candidates = []
        self.last_round = 0

        while True:
            self.vote_counter.count_votes(self.voters, self.eliminated_candidates, self.no_confidence_last)
            self.last_round += 1
            
            total_votes = sum(self.vote_counter.vote_counts.values())
            for candidate, votes in self.vote_counter.vote_counts.items():
                if votes > total_votes / 2:
                    self.winner = candidate
                    return candidate
            
            eliminated_candidate = self.vote_counter.eliminate_candidate(self.voters, self.eliminated_candidates)
            if eliminated_candidate is None:
                print("Tie detected among remaining candidates. No winner can be determined.")
                self.winner = None
                return None
            
            self.eliminated_candidates.append(eliminated_candidate)

            if len(self.eliminated_candidates) == len(self.candidates) - 1:
                remaining_candidates = [candidate for candidate in self.candidates if candidate not in self.eliminated_candidates]
                if remaining_candidates:
                    self.winner = remaining_candidates[0]
                    return remaining_candidates[0]
                else:
                    self.winner = None
                    return None

            if self.last_round > len(self.candidates):
                print("Error: More rounds than candidates. Possible issue with vote counting or elimination.")
                self.winner = None
                return None

    def get_round_vote_counts(self, round: int):
        """
        Returns a datarame with the number of votes for each candidate at each rank for a specific round of the election, excluding eliminated candidates. This method can only be run after calling run_election(). If no_confidence_last is True, no choices after 'No Confidence' will be included.
        
        :param self: Election object
        :param round: The round number for which to get the vote counts
        :type round: int
        """
        if round < 1 or round > self.last_round:
            raise ValueError(f"Round must be between 1 and {self.last_round}")
        
        if self.last_round == 0:
            raise ValueError("Election has not been run yet. Please call run_election() first.")

        eliminated = self.eliminated_candidates[:round-1]
        return self.vote_counter.count_choices(self.voters, eliminated, self.no_confidence_last)
    
    def get_filtered_round_vote_counts(self, round: int, school: str = None, year: int = None):
        """
        Returns a datarame with the number of votes for each candidate at each rank for a specific round of the election, filtered by school and/or year, and excluding eliminated candidates. This method can only be run after calling run_election(). If no_confidence_last is True, no choices after 'No Confidence' will be included.
        
        :param self: Election object
        :param round: The round number for which to get the vote counts
        :type round: int
        :param school: The school to filter by (optional)
        :type school: str or None
        :param year: The year to filter by (optional)
        :type year: int or None
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
        
        return self.vote_counter.count_choices(filtered_voters, eliminated, self.no_confidence_last)
    
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
            vote_counts = self.vote_counter.count_votes(self.voters, eliminated, self.no_confidence_last)
            results.append(copy.deepcopy(vote_counts))
        
        df = pd.DataFrame(results, index=[f'Round {i}' for i in range(1, self.last_round + 1)])
        df = df.transpose()

        sorted_candidates = sorted(self.candidates, key=lambda c: self.eliminated_candidates.index(c) if c in self.eliminated_candidates else float('inf'), reverse=True)
        winner = self.winner if self.winner is not None else df[df.columns[-1]].idxmax()
        sorted_candidates = [winner] + [c for c in sorted_candidates if c != winner]
        df = df.reindex(sorted_candidates)
        
        df = df.fillna('')
        for column in df.columns:
            df[column] = df[column].apply(lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else x)
        
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
            vote_counts = self.vote_counter.count_votes(filtered_voters, eliminated, self.no_confidence_last)
            results.append(copy.deepcopy(vote_counts))
        
        df = pd.DataFrame(results, index=[f'Round {i}' for i in range(1, self.last_round + 1)])
        df = df.transpose()

        sorted_candidates = sorted(self.candidates, key=lambda c: self.eliminated_candidates.index(c) if c in self.eliminated_candidates else float('inf'), reverse=True)
        winner = self.winner if self.winner is not None else df[df.columns[-1]].idxmax()
        sorted_candidates = [winner] + [c for c in sorted_candidates if c != winner]
        df = df.reindex(sorted_candidates)

        df = df.fillna('')
        for column in df.columns:
            df[column] = df[column].apply(lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else x)
        
        return df