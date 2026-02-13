# ASG Ranked Choice Voting Counter

This program takes a CSV file exported from 'Cats on Campus and uses the RCV rules outlined in the ASG Election Commission Guidelines to tabulate the results of the ASG Presidential Election.

## RCV Rules

All votes are counted. If a ticket has a majority of the vote, they are declared the winner. Otherwise, follow the procedure below:

1. The ticket with the least votes is eliminated from contention.
2. The ballots of the eliminated ticket have their votes shifted to the next highest ranked ticket on their ballot.
3. Any ballots which have no more ranked tickets remaining are exhausted and removed from the ballot pool.
4. The votes are recounted and this procedure is repeated until a ticket reaches a majority.

Note: Votes for 'No Confidence' are treated as a ticket.