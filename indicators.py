import yfinance as yf
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import statsmodels.formula.api as smf

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)

tickers = {
    "NVDA", "AAPL", "MSFT", "AMD", "INTC", #1Tech
    "AMZN", "TSLA", "MCD", "BKNG", "SBUX", #3ConsumerCYC
    "GOOG", "META", "NFLX", "DIS", "SPOT", #4ComunicationServices
    "JNJ", "PFE", "LLY", "ABBV", "UNH", #5Healthcare
    "DE", "CAT", "BA", "GE", "RTX", #6Industrials
    "WMT", "KO", "PM", "MNST", "MDLZ", #7ConsDefensive
    "LIN", "SCCO", "NEM", "ECL", "APD", #8BasicMAt
    "WELL", "PLD", "SPG", "O", "VTR", #9RealEstate
    "NEE", "SO", "D", "XEL", "DUK" #10Utilities
}

def safe(df, row):
    try:
        return df.loc[row].iloc[0]
    except (KeyError, IndexError):
        return None

records = {}
for t in tickers:
    tk = yf.Ticker(t)
    bs = tk.balance_sheet
    fin = tk.financials
    info = tk.info

    records[t] = {
        "sector": info.get("sector"),
        "net_income": safe(fin, "Net Income"),
        "revenue": safe(fin, "Total Revenue"),
        "operating_income": safe(fin, "Operating Income"),
        "total_assets": safe(bs, "Total Assets"),
        "equity": safe(bs, "Stockholders Equity"),
        "total_debt": safe(bs, "Total Debt"),
        "current_liab": safe(bs, "Current Liabilities"),
        "current_assets": safe(bs, "Current Assets"),
        "cost": safe(fin, "Cost Of Revenue"),
        "ncurrent_assets": safe(bs, "Total Non Current Assets")
    }

df = pd.DataFrame(records).T

#INDICATORS

net_margin = "net_income * 100 / revenue"
roa = "net_income * 100 / total_assets"
roe = "net_income * 100 / equity"
dte = "total_debt / equity"
current_ratio = "current_assets / current_liab"

conn = sqlite3.connect("financials.db")
df.to_sql("companies", conn, if_exists="replace", index=True, index_label="Ticker")

#ALL SECTORS ALL POSITIONS

df = pd.read_sql("SELECT * FROM companies", conn)
positions = ["net_income", "revenue", "operating_income", "total_assets",
             "equity", "total_debt", "current_liab", "current_assets",
             "cost", "ncurrent_assets"]

sector_pos = df.groupby("sector")[positions].median() / 1_000_000
sector_pos = sector_pos.round(1)
# print(sector_pos)
# sector_pos.to_csv("sectors_position.csv", sep=";", decimal=",")

#ALL SECTORS ALL INDICATORS

df = pd.read_sql("SELECT * FROM companies", conn)
df["net_margin"] = df["net_income"] * 100 / df["revenue"]
df["roa"] = df["net_income"] * 100 / df["total_assets"]
df["roe"] = df["net_income"] * 100 / df["equity"]
df["dte"] = df["total_debt"] / df["equity"]
df["current_ratio"] = df["current_assets"] / df["current_liab"]

#INDICATORS CORELATIONS
corr = df[["net_margin", "roa", "roe", "dte", "current_ratio"]].corr()
corr2 = df[["net_margin","roa","roe","dte","current_ratio"]].corr(method="spearman")
# print(corr.round(2))
print(corr2.round(2))

#CORRELATIONS

indicators = ["net_margin", "roa", "roe", "dte", "current_ratio"]
def corrp(indi):
    for other in indicators:
        if other != indi:
            r, p = spearmanr(df[indi], df[other])
            print(f"{indi} ↔ {other}: r = {r:.2f}, p = {p:.3f} ? < 0,05")

# corrp("roa")

sector_medians = df.groupby("sector")[["net_margin", "roa", "roe", "dte", "current_ratio"]].median().round(2)
# print(sector_medians)
# sector_medians.to_csv("sectors_indicators.csv", sep=";", decimal=",")

#ALL SECTORS ALL STRUCTURALS INDICATORS

df = pd.read_sql("SELECT * FROM companies", conn)

df["cost_ratio"] = df["cost"] * 100 / df["revenue"]                      # wyjaśnia marżę
df["ncurrent_ratio"] = df["ncurrent_assets"] * 100 / df["total_assets"]  # wyjaśnia ROA
df["asset_turnover"] = df["revenue"] / df["total_assets"]                # wyjaśnia ROA
df["opincome_ratio"] = df["operating_income"] * 100 / df["revenue"]      # marża operacyjna

structure = df.groupby("sector")[
    ["cost_ratio", "ncurrent_ratio", "asset_turnover", "opincome_ratio"]
].median().round(2)

# structure.to_csv("structure_indicators.csv", sep=";", decimal=",")

#TOP/WORST 5 COMPANIES

def comp_func(tw,indi, name, desc):
    query = f"SELECT ticker, ROUND({indi}, 2) as {name} FROM companies ORDER BY {name} {desc} LIMIT 5;"
    worst = pd.read_sql(query, conn)
    worst = worst.sort_values(by=name, ascending=True)
    ax = worst.plot(kind="barh", x="Ticker", title=f"{tw} 5: {name}", legend=False)
    ax.bar_label(ax.containers[0])
    ax.axvline(0, color="black", linewidth=0.8)
    ax.margins(x=0.15)
    plt.tight_layout()
    plt.show()

# # WORST 5 COMPANIES

# comp_func("Worst", net_margin, "net_margin", "")
# comp_func("Worst", roa, "roa", "")
# comp_func("Worst", roe, "roe", "")
# comp_func("Worst", dte, "dte", "")
# comp_func("Worst", current_ratio, "current_ratio", "")

# # TOP 5 COMPANIES

# comp_func("Top", net_margin, "net_margin", "desc")
# comp_func("Top", roa, "roa", "desc")
# comp_func("Top", roe, "roe", "desc")
# comp_func("Top", dte, "dte", "desc")
# comp_func("Top", current_ratio, "current_ratio", "desc")

#MEDIAN SECTOR INDICATORS

def median_sector_plot(indi, name):
    que = f"SELECT sector, ROUND({indi},2) as {name} from companies"
    df_indi = pd.read_sql(que, conn)
    indicator = df_indi.groupby("sector")[name].median().sort_values(ascending=False)
    ax = indicator.plot(kind="barh", title=f"Top sectors by: {name}")
    ax.bar_label(ax.containers[0])
    ax.axvline(0, color="black", linewidth=0.8)
    ax.margins(x=0.15)
    plt.tight_layout()
    plt.show()

# median_sector_plot(net_margin, "net_margin")
# median_sector_plot(roa, "roa")
# median_sector_plot(roe, "roe")
# median_sector_plot(dte, "dte")
# median_sector_plot(current_ratio, "current_ratio")

#REGRESION
df_clean = df[df["equity"] > 0].copy()

df_clean["net_margin"] = df_clean["net_income"] * 100 / df_clean["revenue"]
df_clean["roa"] = df_clean["net_income"] * 100 / df_clean["total_assets"]
df_clean["roe"] = df_clean["net_income"] * 100 / df_clean["equity"]
df_clean["dte"] = df_clean["total_debt"] / df_clean["equity"]

model = smf.ols("roe ~ roa + dte + net_margin", data=df_clean).fit()
print(model.summary())
