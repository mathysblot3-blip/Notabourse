Backtesting means testing a method on past data, as if it had been followed. Here is what the score would have done
from 2010 to 2026, with a simulated portfolio: the 50 best-rated S&P 500 stocks,
weighted by market size (at most 10% per stock and 40% per sector), reviewed once a year, transaction costs included
(0.1% per purchase or sale). A stock already held is kept as long as it stays in the top 60. This portfolio does not
exist: I neither offer nor manage it.

**Read this before the charts.** These results are simulated and computed **in sample**: the formula was designed
knowing the whole period, after 211 trials. They show that the method holds up, not that it will work in the future.

### 1. One dollar invested in 2010

$1 invested in August 2010 grows to $13.9, against $9.3 in the S&P 500. This is the figure most sensitive to the
formula's settings: on its own, it is worth little.

{{graphique:3_un_dollar}}

### 2. Year by year

Ahead of the S&P 500 in 12 years out of 15, from 2011 to 2025 (in yellow: the years won).

{{graphique:4_annees}}

### 3. Every 10-year period

The S&P 500 (dividends reinvested) is beaten over each of the 75 ten-year periods starting between 2010 and 2016, by at
least 2.4 points a year.

{{graphique:2_fenetres_10_ans}}

### 4. The "Bankruptcy risk" filter

This filter costs nothing in return: 18.9% a year over the last 10 years, with or without it. On the other hand, the
companies it excludes lost more than 40% in a year three times as often as the others (7.2% vs 2.4%). The middle bar
counts all exclusions, including negative earnings or equity. Limits: the filter excludes about 5 companies a month,
and a delisted stock is replaced by the market for the rest of the year, which softens bankruptcies (the real gap is
probably larger).

{{graphique:7_exclusion}}

### 5. Limit: the score mainly spots the top of the ranking

Only the best-rated 10% of stocks clearly beat the others; groups 1 to 8 do about the same. The gap between the top and
the bottom (+3.8 points a year) is not statistically significant (t of 1.2). The portfolio's lead therefore comes from
the top of the ranking and from size weighting, not from an ability to sort every stock. Groups 1 to 9 are below zero
because each group is equally weighted, while the S&P 500 is driven by its giants.

{{graphique:1_deciles}}

### 6. Limit: deeper drops

More return, but deeper drops: −30.2% at worst (in 2022), against −23.9% for the S&P 500.

{{graphique:9_baisses}}

### 7. A consistent score outside the S&P 500

A stock rated from outside, like a company outside the S&P 500, gets almost the same score as among the members: 0.26
point apart on average over 4,197 cases. This chart shows that the calculation is consistent, not a performance.

{{graphique:8_hors_indice:sans_avertissement}}

### 8. Depending on the portfolio settings

The lead holds whatever the settings: from +2.5 to +4.9 points a year over the last 10 years (+3.6 for the settings
chosen, in yellow). The chosen settings (caps per stock and per sector, buffer, yearly review) were picked for the
safety and stability the score aims for, not for the highest return: without a sector cap, for example, the lead
would have been +4.9 points.

{{graphique:5_robustesse}}
