Bourse à lunettes rates the **strength** of a stock: its ability to deliver stable and persistent long-term returns. The score
comes from my research on S&P 500 members. The website applies this formula, unchanged, to Yahoo Finance
data.

### In short

- Four parts scored from 0 to 100: **profitability, growth, balance sheet, momentum**.
- Each company is compared with the S&P 500 members of **its group**: industrial and service companies, financials, or
  real estate investment trusts (REITs).
- The average of the four parts gives the **M score**, then the **score out of 100**. 50 = the middle.
- Fragile financial health, recent losses or negative equity **exclude** the company from the selection, without
  changing its score. The "Bankruptcy risk" indicator on each company page shows it.
- The score **does not say whether the stock is expensive**: each company page shows it separately, by
  comparing its price with its sector (part 6). It **is not investment advice**.

### 1. The four parts

| Part | Question | Ratios used |
|---|---|---|
| Profitability | Does it earn a good living, compared with its competitors? | Net income over the last 12 months / equity (ROE), as a gap to its sector average. Financials: income / assets, as a gap to their sub-sector (banks, insurers, others) |
| Growth | Are its sales and earnings growing, and steadily? | Annual growth of sales and operating earnings (EBITDA) over the last 4 fiscal years: regularity (a bad year weighs up to three times as much as a good one) and level. REITs: recurring earnings per share (FFO); financials: revenue |
| Balance sheet | Can it withstand hard times? | Debts and cash relative to the company's value (debts + market value), and size. REITs: net debt / EBITDA. Financials: equity / assets, and size |
| Momentum | Does the stock beat the market, and steadily? | Weekly gap to the S&P 500 (dividends included) over 11 months, last month excluded; weeks with an exceptional rise are neutralised |

For each ratio, extreme values are brought back to the 5th and 95th percentiles, then the company is ranked within its
group. The 0 to 100 score translates this rank: 0 for the bottom 5%, 100 for the top 5%.

I also tested share price volatility and the price (earnings or EBITDA relative to the company's value), without
keeping them: picking calm stocks cost return, and the price gave uneven results from one period to the next. Safety
therefore comes from excluding companies in danger (part 4), not from picking calm stocks.

### 2. From four scores to a score out of 100

1. **S** = average of the available part scores (at least 2).
2. **M** = (S − average S of the group) / standard deviation of the group's S. Comparing within the group avoids judging
   a bank by an industrial company's standards.
3. **Score out of 100** = share of S&P 500 members with a lower M score.
4. **Stars**: 5 from 95, 4.5 from 90, 4 from 80, 3.5 from 70, 3 from 55, 2.5 from 40, 2 from 30, 1.5 from 20, 1 from 10,
   0.5 below.

Each company page shows these calculations with the company's own figures, in the "Calculation details" menus.

### 3. Groups and sectors

The group and sector come from the industry code (SIC) the company reports to the SEC (Securities and Exchange
Commission), the US market regulator, mapped into the 12 Fama and French sectors. Without an SEC code (most
non-US companies), the website takes the industry given by Yahoo Finance and maps it to the most frequent group and sector among the S&P 500 members of that industry.

### 4. Bankruptcy risk

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

These thresholds let almost the whole S&P 500 through. To warn earlier, the website shows an **orange** "watch point"
from 60% debt, EBITDA below 4 times interest, negative operating cash flow or, for a financial company, less than 6%
equity. This orange is a display warning only: it changes neither the score nor the exclusion.

### 5. Data

- Accounts, prices and market values: **Yahoo Finance**.
- Last 12 months: the last 4 published quarters, otherwise the last fiscal year (companies reporting half-yearly).
- The reference, meaning the S&P 500 members and their ratios, is recomputed automatically every Saturday.
- The website counts searches (date and company searched) to see what interests visitors; it records nothing about
  the visitor.

The website's score is an adaptation of my research score, computed on the accounts filed with the SEC. Before going
live, I checked that they match: on S&P 500 members, a rank correlation of 0.95 and a median gap of 4 points out of
100.

### 6. Price compared with the sector

Each company page compares the stock's price with that of the other companies in its sector. This benchmark stands
apart: it is not part of the score.

1. The company's **P/E ratio** = market value / net income over the last 12 months: the price is worth so many times
   annual earnings. A loss-making company has no P/E.
2. **Sector P/E** = 1 / average of (earnings / market value) of the profitable S&P 500 members in the same sector (at
   least 5, otherwise the whole group). This is the harmonic mean of their P/E ratios: a company with tiny earnings,
   hence a huge P/E, does not distort the average. Comparing with similar companies and using this mean follows Liu,
   Nissim and Thomas (2002), see the Sources page.
3. **Gap** = P/E / sector P/E − 1. The stock is called **cheap** at −20% or less, **expensive** at +25% or more, **in
   line** in between. The two thresholds mirror each other: 1 / 0.8 = 1.25.

When a figure is missing, the company page still gives an estimate, flagged "unreliable value": earnings of the last
fiscal year, average earnings over the last fiscal years for a loss-making company, the P/E ratio given by Yahoo
Finance or, as a last resort, price relative to sales against the same ratio in the sector.

This benchmark describes the price, it predicts nothing: over 2010-2026, it had no clear link with the return of the
following 12 months.

### 7. Role of AI

I carried out this project with Claude Code (Anthropic's Opus 5.5 model), an artificial intelligence. All choices are
mine or were approved by me; the AI did the following:

- run online research;
- write all the Python code, for the research and for the website;
- download the free data (accounts filed with the SEC, prices, indices) and check that no future data is used;
- run the calculations: backtests, reserved test, 211 trials, statistical tests;
- produce the charts, reports and texts, which I reread and corrected.

The AI made mistakes several times (missing data, a month left out of a calculation). Every error found was
corrected, but the AI is imperfect: errors may remain.

### 8. Limits

- **This is not investment advice.** I am not a licensed financial adviser.
- **Nothing has been proven in real life.** A first formula, frozen before the test, failed on the reserved test period
  (2018-2026). The current formula was built afterwards, knowing that period: what it did in the past may be luck. Only
  tracking it over time can prove it. The simulated results, good and bad, are on the Backtesting page.
- **The score ignores the price.** A very good company can be an overpriced stock; the price is still shown on each
  company page, compared with the sector (part 6).
- **A relative score.** It compares the company with the current S&P 500 members: it can fall because others improve.
- **Designed for large US companies.** For a small or a foreign company, the comparison is less reliable (accounting
  standards, currencies, scarcer data).
- **Data without guarantee.** Yahoo Finance may contain errors or gaps; a page can change when Yahoo corrects its data.
