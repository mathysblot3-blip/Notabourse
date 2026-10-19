NotaBourse rates the **strength** of a stock: its ability to deliver stable and persistent long-term returns. The score
comes from research by Mathys Blot on S&P 500 members. The website applies this formula, unchanged, to Yahoo Finance
data.

### In short

- Four parts scored from 0 to 100: **profitability, growth, balance sheet, momentum**.
- Each company is compared with the S&P 500 members of **its group**: industrial and service companies, financials, or
  real estate investment trusts (REITs).
- The average of the four parts gives the **M score**, then the **score out of 100**: the share of S&P 500 members that
  do worse. 50 = the middle.
- Fragile financial health, recent losses or negative equity **exclude** the company from the selection, without
  changing its score.
- The score **does not say whether the stock is expensive** and **is not investment advice**.

### 1. The four parts

| Part | Question | Ratios used |
|---|---|---|
| Profitability | Does it earn a good living, compared with its competitors? | Net income over the last 12 months / equity (ROE), as a gap to its sector average. Financials: income / assets, as a gap to their sub-sector (banks, insurers, others) |
| Growth | Are its sales and earnings growing, and steadily? | Annual growth of sales and operating earnings (EBITDA) over the last 4 fiscal years: regularity (a bad year weighs up to three times as much as a good one) and level. REITs: recurring earnings per share (FFO); financials: revenue |
| Balance sheet | Can it withstand hard times? | Debts and cash relative to the company's value (debts + market value), and size. REITs: net debt / EBITDA. Financials: equity / assets, and size |
| Momentum | Does the stock beat the market, and steadily? | Weekly gap to the S&P 500 (dividends included) over 11 months, last month excluded; weeks with an exceptional rise are neutralised |

For each ratio, extreme values are brought back to the 5th and 95th percentiles, then the company is ranked within its
group. The 0 to 100 score translates this rank: 0 for the bottom 5%, 100 for the top 5%.

### 2. From four scores to a score out of 100

1. **S** = average of the available part scores (at least 2).
2. **M** = (S − average S of the group) / standard deviation of the group's S. Comparing within the group avoids judging
   a bank by an industrial company's standards.
3. **Score out of 100** = share of S&P 500 members with a lower M score.
4. **Stars**: 5 from 95, 4.5 from 90, 4 from 80, 3.5 from 70, 3 from 55, 2.5 from 40, 2 from 30, 1.5 from 20, 1 from 10,
   0.5 below.

Each company page shows these calculations with the company's own figures, in the "The calculation in detail" menus.

### 3. Groups and sectors

The group and sector come from the industry code (SIC) the company reports to the SEC, the US market regulator, mapped
into the 12 Fama and French sectors. Without an SEC code (most non-US companies), the website takes the industry given
by Yahoo Finance and maps it to the most frequent group and sector among the S&P 500 members of that industry.

### 4. Financial health (safeguard)

Three lights, scored from −1 to +1 (a financial company has only one: equity / assets):

| Light | Green | Red |
|---|---|---|
| Cash, if the business burns cash | 2 years of cash or more | 1 year or less |
| Leverage: debts / (debts + market value) | 80% or less | 90% or more |
| Interest: EBITDA / interest | 2x or more | 1x or less |
| Financials: equity / assets | 5% or more | 4% or less |

The company is **excluded from the selection** if the average of its lights is not green, if it lost money in either of
its last two fiscal years, or if its equity is negative. Exclusion does not change the score: it signals that the
company fails one of the method's safety conditions.

These thresholds let almost the whole S&P 500 through. To warn earlier, the website shows an **orange** "watch point"
from 60% debt, EBITDA below 4 times interest, negative operating cash flow or, for a financial company, less than 6%
equity. This orange is a display warning only: it changes neither the score nor the exclusion.

### 5. Data

- Accounts, prices and market values: **Yahoo Finance**, converted into dollars. Ratios are computed item by item as in
  the research.
- Last 12 months: the last 4 published quarters, otherwise the last fiscal year (companies reporting half-yearly).
- S&P 500 members are scored against each other **every week**; their page comes from that calculation. Any other
  company is computed on request, then compared with these members as if it were added to its group, without changing
  their scores.

### 6. How the website differs from the research

The research used the accounts filed with the SEC. The website applies the same formula to Yahoo data, with these
adaptations:

| Adaptation | Why |
|---|---|
| Yahoo Finance data instead of SEC filings; accounting items chosen by definition, before any test | Yahoo covers companies worldwide, the SEC only those that file with it |
| Operating income: Yahoo's figure, already cleaned of one-off items | Adjusting it again would count impairments twice |
| Annual growth over 4 fiscal years, instead of quarterly over 5 years | Yahoo keeps only a few years of accounts |
| A score from 2 parts, with a warning (the research requires momentum) | Author's choice: also score incomplete companies, while flagging it |
| Companies listed for less than 12 months are scored, with a warning (the research does not score them) | Same choice |
| Classification by the Yahoo industry when the SEC has no industry code | Non-US companies |
| IFRS accounts (European, Asian companies...) | Close but not identical definitions (leases, one-off items): a less exact comparison |
| Simple sentences and the orange watch point | Display only: the score does not change |

**Acceptance test (19 October 2026).** Before going live, the website recomputed with Yahoo data the scores of the S&P
500 members at the research's last date (31 August 2026), then compared them with the research scores. The thresholds
were set before the calculation.

| Measure | Result | Threshold |
|---|---|---|
| Rank correlation of M scores (495 companies scored on both sides) | 0.95 | at least 0.80 |
| Median gap in the score out of 100 | 4 points | less than 10 |
| Financials only | 0.88; 7 points | |

Test passed. The largest gaps come from data missing on one side or the other, from how asset managers' earnings are
defined, and from annual growth.

### 7. Limits

- **This is not investment advice.** The author is not a licensed financial adviser.
- **Nothing has been proven in real life.** A first formula, frozen before the test, failed on the reserved test period
  (2018-2026). The current formula was built afterwards, knowing that period: what it did in the past may be luck. Only
  tracking it over time can prove it.
- **The score ignores the price.** A very good company can be an overpriced stock.
- **A relative score.** It compares the company with the current S&P 500 members: it can fall because others improve.
- **Designed for large US companies.** For a small or a foreign company, the comparison is less reliable (accounting
  standards, currencies, scarcer data).
- **Data without guarantee.** Yahoo Finance may contain errors or gaps; a page can change when Yahoo corrects its data.

### 8. Sources

The method draws in particular on Novy-Marx (2013) for the comparison with the sector, Chan, Karceski and Lakonishok
(2003) and Lakonishok, Shleifer and Vishny (1994) for growth, Campbell, Hilscher and Szilagyi (2008) for leverage and
cash, and Jegadeesh and Titman (1993) for momentum. Data: Yahoo Finance, SEC (industry codes), Fama and French sectors.
