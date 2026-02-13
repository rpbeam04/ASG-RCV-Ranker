class Voter:
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

class VoteCounter:
    def __init__(self):
        pass