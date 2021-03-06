__author__ = 'siy'

import pandas as pd


def check_symbol(symbol):
    firm_df = pd.read_html("http://finviz.com/quote.ashx?t=" + symbol)[7]
    firm_df[4][4] = 'EPS next Y %'
    firm_dict = dict(zip(firm_df.get_values().flatten().tolist()[::2], firm_df.get_values().flatten().tolist()[1::2]))
    firm_dict['symbol'] = symbol
    return firm_dict


def pe_score(pe):
    score = 0
    if 2.5 <= pe < 12.5:
        score = 2
    elif pe < 0 or pe > 50:
        score = -1
    return score


def pfcf_score(pfcf):
    score = 0
    if 0 < pfcf < 12:
        score = 1
    elif pfcf < 0 or pfcf > 30:
        score = -1
    return score


def ps_score(ps):
    score = 0
    if 0 < ps < 0.8:
        score = 1
    elif ps < 0:
        score = -1
    return score


def pb_score(pb):
    score = 0
    if 0 < pb < 1:
        score = 1
    elif pb < 0:
        score = -1
    return score


def recom_score(recom):
    score = 0
    if 0 < recom <= 1.5:
        score = 1
    elif recom > 3:
        score = -1
    return score


def short_ratio_score(short_ratio):
    score = 0
    if short_ratio > 0.3:
        score = 1
    elif 0.1 <= short_ratio <= 0.2:
        score = -1
    return score


def insider_purchase_score(insider_purchase):
    if insider_purchase > 0:
        return 1
    return 0


def profit_margin_score(profit_margin):
    score = 0
    if profit_margin > 0.25:
        score = 1
    elif profit_margin < 0.05:
        score = -1
    return score


def sales_growth_score(revenue_growth):
    score = 0
    if revenue_growth > 0.15:
        score = 1
    elif revenue_growth < 0:
        score = -1
    return score


def earning_growth_score(earning_growth):
    score = 0
    if earning_growth > 0.2:
        score = 1
    elif earning_growth < 0:
        score = -1
    return score


def pred_price(d): return convert_num(d['Price']) < 1


def pred_vol(d): return convert_num(d['Avg Volume']) < 100000


def pred_mkt_cap(d): return convert_num(d['Market Cap']) < 100000000


def pred_52w_high_chg(d): return convert_num(d['52W High']) > -0.2


def pred_overbought(d): return convert_num(d['RSI (14)']) > 60


def get_graham_value(d):
    eps_ttm = convert_num(d['EPS (ttm)'])
    eps_next_y = convert_num(d['EPS next Y'])
    eps_growth_5y = convert_num(d['EPS next 5Y'])
    graham_value = (eps_ttm + eps_next_y) / 2 * (8.5 + 2 * eps_growth_5y * 100) * 4.4 / 3.9
    return graham_value


def pred_graham_value(d):
    px = convert_num(d['Price'])
    if px == 0:
        return 0
    return (get_graham_value(d) / px) < 1.2


def get_ebit_value(d):
    sales = convert_num(d['Sales'])
    margin = (convert_num(d['Profit Margin']) + convert_num(d['Oper. Margin'])) / 2
    operating_income = sales * margin
    pe = convert_num(d['Forward P/E'])
    business_value = operating_income * pe
    yahoo_stat = pd.read_html('http://finance.yahoo.com/q/ks?s=' + d['symbol'] + '+Key+Statistics')
    if len(yahoo_stat) == 4:
        return 0
    cash = convert_num(yahoo_stat[15][1][2])
    total_debt = convert_num(yahoo_stat[15][1][4])
    equity_value = business_value + cash - total_debt
    shares_outstand = convert_num(d['Shs Outstand'])
    if shares_outstand == 0:
        return 0
    ebit_value = equity_value / shares_outstand
    return ebit_value


def pred_ebit_value(d):
    px = convert_num(d['Price'])
    if px == 0:
        return 0
    return get_ebit_value(d) / px < 1.2


def check_score_common(d, *preds):
    if any([f(d) for f in preds]):
        return 0

    score = pe_score(convert_num(d['Forward P/E'])) + \
            pfcf_score(convert_num(d['P/FCF'])) + \
            ps_score(convert_num(d['P/S'])) + \
            pb_score(convert_num(d['P/B'])) + \
            recom_score(convert_num(d['Recom'])) + \
            short_ratio_score(convert_num(d['Short Float'])) + \
            insider_purchase_score(convert_num(d['Insider Trans'])) + \
            profit_margin_score(convert_num(d['Profit Margin'])) + \
            sales_growth_score(convert_num(d['Sales Q/Q'])) + \
            earning_growth_score(convert_num(d['EPS Q/Q']))

    return score


def check_score_hold(d):
    return check_score_common(d, pred_price, pred_vol, pred_mkt_cap)


def check_score_buy(d):
    return check_score_common(d, pred_price, pred_vol, pred_mkt_cap, pred_52w_high_chg, pred_overbought,
                              pred_graham_value, pred_ebit_value)


def get_all_symbols(idx=1):
    dfl = pd.read_html("http://finviz.com/screener.ashx?v=111&r={}".format(idx))
    all_df = dfl[13]
    all_df.columns = all_df.irow(0)
    return all_df['Ticker'].tolist()[1:]  # get Ticker column and skip the first value


def convert_num(val):
    lookup = {'K': 1000, 'M': 1000000, 'B': 1000000000, '%': 0.01}
    try:
        unit = val[-1]
        if unit in lookup:
            return lookup[unit] * float(val[:-1])
        return float(val)
    except:
        return 0

# 201-401-601-801
for i in range(4301, 4501, 20):
    for symbol in get_all_symbols(i):
        score = check_score_buy(check_symbol(symbol))
        if score >= 3:
            print('{}={}'.format(symbol, score))

