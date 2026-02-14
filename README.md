# ASG Ranked Choice Voting Counter

This program takes a CSV file exported from 'Cats on Campus and uses the RCV rules outlined in the ASG Election Commission Guidelines to tabulate the results of the ASG Presidential Election.

### Note on Confidentiality and Private Data

All real student data must be hidden locally via .gitignore and not published online.

## RCV Rules

All votes are counted. If a ticket has a majority of the vote, they are declared the winner. Otherwise, follow the procedure below:

1. The ticket with the least votes is eliminated from contention.
2. The ballots of the eliminated ticket have their votes shifted to the next highest ranked ticket on their ballot.
3. Any ballots which have no more ranked tickets remaining are exhausted and removed from the ballot pool.
4. The votes are recounted and this procedure is repeated until a ticket reaches a majority.

Note: Votes for 'No Confidence' are treated as a ticket.

## RCV Tiebreaker Rules

When two or more tickets have the same number of votes and are either subject to elimination or victory, the tiebreaker rules apply.

### Tiebreaker Rules (for elimination or victory)

When two or more tickets are tied for elimination or victory, resolve the tie as follows:

1. **Current Round Secondary Preferences:**  
   Compare the number of second-choice votes each tied ticket received in the current round.  
   If still tied, compare third-choice votes, then fourth-choice votes, etc., until the tie is broken.

2. **Previous Round First-Choice Votes:**  
   If the tie persists, compare the number of first-choice votes each tied ticket received in the previous round.  
   If still tied, repeat this comparison for earlier rounds in reverse order until the tie is broken.

3. **Previous Round Lower Preferences:**  
   If the tie remains, compare second-choice votes in the previous round, then third-choice votes, etc., for each earlier round, until the tie is broken.

4. **Random Selection and Runoff:**  
   In a tie for elimination, eliminate the remaining tied candidates. In a tie for victory, there will be a runoff.