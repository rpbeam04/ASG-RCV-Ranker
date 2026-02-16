import numpy as np
import pandas as pd

from classes import Voter

def generate_voters(n_voters: int, candidates: list[str], weights: list[float], variances: list[float], correlation_matrix: np.ndarray = None, time_factors: list[float] = None, seed: int = None) -> list['Voter']:
    """
    Generates a list of Voter objects with random choices for testing. The choices are generated based on a weighted random selection of candidates, with weights randomly adjusted by a variance factor for each voter.

    :param n_voters: The number of voters to generate.
    :type n_voters: int
    :param candidates: A list of candidate names to choose from.
    :type candidates: list[str]
    :param weights: A list of weights corresponding to the candidates, indicating the likelihood of each candidate being chosen.
    :type weights: list[float]
    :param variances: A list of variance values corresponding to the candidates, indicating how much the weights can vary for each voter.
    :type variances: list[float]
    :param correlation_matrix: A 2D numpy array representing the correlation between candidates.
    :type correlation_matrix: np.ndarray
    :param time_factors: A list of time factors corresponding to the candidates, indicating whether canditdates gain or lose performance as time goes on.
    :type time_factors: list[float]
    :param seed: An optional random seed for reproducibility.
    :type seed: int, optional
    :return: A list of Voter objects with generated choices.
    :rtype: list[Voter]
    """
    if seed is not None:
        np.random.seed(seed)

    if correlation_matrix is None:
        correlation_matrix = np.zeros((len(candidates), len(candidates)))

    if time_factors is None:
        time_factors = [0.0] * len(candidates)

    voters = []
    for i in range(n_voters):
        voter = Voter(voter_id=i+1, school="N/A", year=0, n_candidates=len(candidates))
        # Adjust weights for time factors
        adjusted_weights = [w * (1 - tf/2 + tf * i/n_voters) for w, tf in zip(weights, time_factors)]
        # Adjust weights for randomness
        adjusted_weights = [max(1e-6, w + np.random.normal(0, var)) for w, var in zip(adjusted_weights, variances)]
        total_weight = sum(adjusted_weights)
        probabilities = [w / total_weight for w in adjusted_weights]
        # Select first choice
        first_choice = np.random.choice(candidates, p=probabilities)
        # Correlation between first choice and others
        first_idx = candidates.index(first_choice)
        corr_with_first = correlation_matrix[first_idx]
        # Compute ranking probability for each candidate (except first)
        ranking_probs = []
        for idx, candidate in enumerate(candidates):
            if idx == first_idx:
                ranking_probs.append(1.0)  # Always rank first choice
            else:
                # Higher correlation: more likely to rank
                # Lower correlation: less likely to rank
                # Map corr (-1,1) to probability (0.2, 1.0)
                prob = 0.2 + 0.8 * max(0, corr_with_first[idx])
                ranking_probs.append(prob)
        # Randomly decide which candidates are ranked
        ranked_mask = [np.random.rand() < prob for prob in ranking_probs]
        # Always include first choice
        ranked_mask[first_idx] = True
        ranked_candidates = [c for c, m in zip(candidates, ranked_mask) if m]
        # Shuffle ranked candidates, but keep first choice at the top
        rest_ranked = [c for c in ranked_candidates if c != first_choice]
        np.random.shuffle(rest_ranked)
        final_choices = [first_choice] + rest_ranked
        for rank, choice in enumerate(final_choices, start=1):
            voter.set_choice(rank, choice)
        voters.append(voter)

    return voters