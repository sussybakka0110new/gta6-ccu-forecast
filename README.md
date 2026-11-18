# gta6-ccu-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/sussybakka0110new/gta6-ccu-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/sussybakka0110new/gta6-ccu-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Quantile forecast of the concurrent Twitch viewers in the Grand Theft Auto VI
category for every hour of its launch day after the first.

The program reads one case JSON from the input directory and writes one output
JSON per case. It has no network access and uses only the Python standard
library.

## Method

The case ships the hourly viewer curves of dozens of earlier big game launches.
A launch day has a characteristic shape — an opening spike, a lull while part
of the audience sleeps, then a second peak as another region comes online — and
that shape depends heavily on how big the category already is at hour 1. The
model weights each comparable by how close its hour-1 count is to today's,
then takes the weighted quantiles of each comparable's log-ratio to its own
hour 1, with a small residual spread. This produces five honest quantiles per
hour rather than a single point estimate.

## Run it

```sh
mkdir -p output
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=output python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
