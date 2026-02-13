from reader import read_election_data
from classes import Voter
from pprint import pprint

def test_read_simple_1():
    file = "Data/test_data.csv"
    voters = read_election_data(file)
    assert len(voters) == 14
    for voter in voters:
        print(voter)

    return True

def test_fake_simple_1():
    file = "Fake Data/fake_data_test_1.csv"
    voters = read_election_data(file)
    assert len(voters) == 6
    for voter in voters:
        print(voter)

    return True

if __name__ == "__main__":
    assert test_read_simple_1()
    print()
    assert test_fake_simple_1()