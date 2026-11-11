# Financial Indicators Analysis: 45 Companies, 9 Sectors

Analysis of what drives profitability across sectors, based on the financial statements of 45 large listed companies (5 per sector).

## Goal
Understand how profitability, leverage and liquidity differ between sectors, and what really explains ROE.

## Data
Financial statements of 45 companies in 9 sectors (Technology, Communication Services, Consumer Defensive, Consumer Cyclical, Industrials, Healthcare, Utilities, Real Estate, Basic Materials). Single reporting period.

## Methods
- Calculated net margin, ROA, ROE, debt-to-equity (D/E) and current ratio
- Compared sectors using medians to limit the effect of outliers
- Built Pearson and Spearman correlation matrices
- Estimated an OLS regression: ROE ~ ROA + D/E + net margin
- Investigated individual outliers (e.g. McDonald's, Intel) to explain unusual values

## Key findings
- Digital-product sectors (Technology 26.9%, Communication Services 24.3%) have the highest net margins; Industrials and Consumer Cyclical the lowest.
- Capital-intensive sectors (Real Estate, Utilities) have the lowest ROA because ~94% of their assets are non-current.
- A high ROE often reflects debt, not efficiency (D/E vs ROE correlation +0.39, D/E vs ROA -0.36).
- The regression explains 68.7% of ROE variation (adjusted R-squared 0.687); D/E and ROA are significant, net margin is not once ROA is included.

## Limitations
Small sample (45 large companies, 5 per sector), one reporting period, and companies with negative equity (from share buybacks) distort ROE and D/E.

## Tools
Python (pandas, statsmodels), Excel

## Author
Oleksii Biruk, Economics, Jagiellonian University
