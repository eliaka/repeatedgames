Playing Repeated Games Experiment

> Elif Akata. June 2024.
> Let GPT-4 play two games against humans.
> Code is based on https://github.com/ericschulz/banditexperiment

## Experiment

This is the html/js-implementation of the experiment.

- index.html: the pages with instructions of the experiment.
- js: script.js contains the documented code

Currently, there are 2 games with 10 rounds each. There are 2 options in each game and the rules are as follows:

#### Game 1 (Prisoner's Dilemma)

- If you choose J and the other player chooses J, then you win 8 points and the other player wins 8 points.
- If you choose J and the other player chooses F, then you win 0 points and the other player wins 10 points.
- If you choose F and the other player chooses J, then you win 10 points and the other player wins 0 points.
- If you choose F and the other player chooses F, then you win 5 points and the other player wins 5 points.

#### Game 2 (Battle of the Sexes)

- If you choose J and the other player chooses J, then you win 7 points and the other player wins 10 points.
- If you choose J and the other player chooses F, then you win 0 points and the other player wins 0 points.
- If you choose F and the other player chooses J, then you win 0 points and the other player wins 0 points.
- If you choose F and the other player chooses F, then you win 10 points and the other player wins 7 points.