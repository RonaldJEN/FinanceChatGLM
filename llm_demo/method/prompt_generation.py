from llm_demo.method.query_functions import dq
import pandas as pd
from fuzzywuzzy import process
from llm_demo.method.template_manager import template_manager

def find_best_match(question, mapping, threshold=40):
    matches = process.extract(question, mapping.keys())
    best_matches = [match[0] for match in matches if match[1] >= threshold]
    return best_matches

def row_to_sentence_onlydata(row):
    year = row['年份']
    code = row['证券代码']
    name = row['证券简称']
    other_data = {k: v for k, v in row.items() if k not in ['年份', '证券代码', '证券简称']}
    details = ",\n ".join([f"{col}为{value:.2f}" for col, value in other_data.items()])
    return f"在{year}年，{name}的{details}元。"

def row_to_sentence(row):
    year = row['年份']
    name = row['证券简称']
    data = dq.query_company_annual_reports()
    company_full_name = data[data['company_short_name'] == name]['company_full_name'].values[0]
    valid_columns = [col for col in row.index if col not in ['年份', '证券代码', '证券简称'] and "增长率" not in col and "上一年" not in col]

    details = []
    for col in valid_columns:
        value = row[col]
        growth_rate_col = f"{col}增长率"
        last_year_value_col = f"{col}上一年"
        if growth_rate_col in row and pd.notna(row[growth_rate_col]) and last_year_value_col in row:
            growth_rate = row[growth_rate_col]
            last_year_value = row[last_year_value_col]
            detail = f"{name}{year-1}年的{col}为{last_year_value:.2f}元，{year}年的{col}为{value:.2f}元，根据公式，{col}增长率=({col}-上年{col})/上年{col}，得出结果{name}{year}年的{col}增长率为{growth_rate:.2f}%。\n"
        else:
            detail = f"{name}{year}年的{col}为{value:.2f}元。\n"
        details.append(detail)

    return f"{name}(全称:{company_full_name})的{year}年数据:{' '.join(details)}\n"

def get_balance_static(q, stock_name,year=[]):
    chinese_mapping =[
    "年份",
    "证券代码",
    "证券简称",
    "流动资产合计",
    "非流动资产合计",
    "流动负债合计",
    "非流动负债合计"]
    data = dq.query_balance_static_data()
    data = data[chinese_mapping]
    data = data.loc[data['证券简称']==stock_name]

    matches = process.extract(q, [k for k in chinese_mapping if  k not in ['年份', '证券代码', '证券简称']])
    total_q = [match[0] for match in matches if match[1] >= 40]
    if total_q:
        total_q = ['年份', '证券代码', '证券简称'] + total_q
        data = data[total_q]
        data = data.sort_values(by="年份")
        if '增长率' in q :
            for col in data.columns:
                if col not in ['年份', '证券代码', '证券简称']:
                    data[f"{col}增长率"] = data[col].pct_change() * 100
                    data[f"{col}上一年"] = data[col].shift(1)
            if len(year) != 0:
                data = data.loc[(data['年份'] == int(year[0]))]
            if data.empty:
                return ''
            sentences = data.apply(row_to_sentence, axis=1)
            sentences = '\n'.join(sentences)
        else:
            if len(year) != 0:
                data = data.loc[(data['年份'] == int(year[0]))]
            if data.empty:
                return ''
            sentences = data.apply(row_to_sentence_onlydata, axis=1)
            sentences = '\n'.join(sentences)
        return sentences
    else:
        return ''

def get_balance_sheet_prompt(q, stock_name, year=[]):
    chinese_to_english_mapping = {'年份': 'reporting_year', '证券代码': 'stock_code', '证券简称': 'stock_name',
                                  '货币资金': 'cash', '应收票据': 'receivables', '应收利息': 'interest_receivable', '应收账款': 'accounts_receivable',
                                  '其他应收款': 'other_receivables', '预付款项': 'prepayments', '存货': 'inventories',
                                  '一年内到期的非流动资产': 'non_current_assets_due_within_one_year', '其他流动资产': 'other_current_assets',
                                  '投资性房地产': 'investment_property', '长期股权投资': 'long_term_equity_investments',
                                  '长期应收款': 'long_term_receivables', '固定资产': 'fixed_assets', '工程物资': 'construction_materials',
                                  '在建工程': 'construction_in_progress', '无形资产': 'intangible_assets', '商誉': 'goodwill',
                                  '长期待摊费用': 'long_term_prepaid_expenses', '递延所得税资产': 'deferred_tax_assets', '其他非流动资产': 'other_non_current_assets',
                                  '短期借款': 'short_term_borrowings', '应付票据': 'bills_payable', '应付账款': 'accounts_payable',
                                  '预收款项': 'receipts_in_advance', '应付职工薪酬': 'employee_benefits_payable', '应付股利': 'dividends_payable',
                                  '应交税费': 'taxes_payable', '应付利息': 'interest_payable', '其他应付款': 'other_payables',
                                  '一年内到期的非流动负债': 'non_current_liabilities_due_within_one_year', '其他流动负债': 'other_current_liabilities',
                                  '长期借款': 'long_term_borrowings', '应付债券': 'bonds_payable', '长期应付款': 'long_term_payables',
                                  '预计负债': 'provisions', '递延所得税负债': 'deferred_tax_liabilities', '其他非流动负债': 'other_non_current_liabilities',
                                  '实收资本': 'paid_in_capital', '资本公积': 'capital_reserve', '盈余公积': 'surplus_reserve', '未分配利润': 'undistributed_profit',
                                  '其他综合收益': 'other_comprehensive_income', '长期应付职工薪酬': 'long_term_employee_benefits_payable',
                                  '长期递延收益': 'long_term_deferred_income', '合同资产': 'contract_assets', '其他非流动金融资产': 'other_non_current_financial_assets',
                                  '应付票据及应付账款': 'notes_and_accounts_payable', '合同负债': 'contractual_obligations', '其他权益工具投资': 'other_equity_instruments_investments',
                                  '总负债': 'total_liabilities', '总资产': 'total_assets', '净资产': 'net_assets'}
    english_to_chinese_mapping = {v: k for k, v in chinese_to_english_mapping.items()}
    data = dq.query_balance_sheet(stock_name)
    data.rename(columns=english_to_chinese_mapping, inplace=True)
    data = data[list(chinese_to_english_mapping.keys())]

    chinese_to_english_mapping = {k: v for k, v in chinese_to_english_mapping.items() if k not in ['年份', '证券代码', '证券简称']}
    total_q = find_best_match(q, chinese_to_english_mapping)

    if total_q:
        total_q = ['年份', '证券代码', '证券简称'] + total_q
        data = data[total_q]
        data = data.sort_values(by="年份")
        if '增长率' in q :
            for col in data.columns:
                if col not in ['年份', '证券代码', '证券简称']:
                    data[f"{col}增长率"] = data[col].pct_change() * 100
                    data[f"{col}上一年"] = data[col].shift(1)

            if len(year) != 0:
                data = data.loc[(data['年份'] == int(year[0]))]
            if data.empty:
                return ''
            sentences = data.apply(row_to_sentence, axis=1)
            sentences = '\n'.join(sentences)
        else:
            if len(year) != 0:
                data = data.loc[(data['年份'] == int(year[0]))]
            if data.empty:
                return ''
            sentences = data.apply(row_to_sentence_onlydata, axis=1)
            sentences = '\n'.join(sentences)
        # 从数据库中查询数据
        return sentences
    else:
        return ''

def get_cash_flow_statement_prompt(q, stock_name, year=[]):
    chinese_to_english_mapping = {
        '年份': 'reporting_year', '证券代码': 'stock_code', '证券简称': 'stock_name',
        '销售商品、提供劳务收到的现金': 'sales_cash', '收到的税费返还': 'tax_refund',
        '收到其他与经营活动有关的现金': 'other_operating_cash', '购买商品、接受劳务支付的现金': 'purchase_goods_services_cash',
        '支付给职工以及为职工支付的现金': 'employee_wages_cash', '支付的各项税费': 'tax_payments',
        '支付其他与经营活动有关的现金': 'other_cash_related_operations', '经营活动产生的现金流量净额': 'net_operating_cash_flow',
        '收回投资收到的现金': 'investment_recovery_cash', '取得投资收益收到的现金': 'investment_profit_cash',
        '处置固定资产、无形资产和其他长期资产收回的现金净额': 'dispose_assets_cash',
        '处置子公司及其他营业单位收到的现金净额': 'dispose_subsidiary_cash',
        '购建固定资产、无形资产和其他长期资产支付的现金': 'purchase_fixed_assets_cash',
        '投资支付的现金': 'investment_payments_cash', '支付其他与投资活动有关的现金': 'other_investment_activity_cash',
        '投资活动产生的现金流量净额': 'net_investment_cash_flow', '吸收投资收到的现金': 'investment_received_cash',
        '取得借款收到的现金': 'loan_received_cash', '偿还债务支付的现金': 'debt_repayment_cash',
        '分配股利、利润或偿付利息支付的现金': 'dividend_interest_payment_cash',
        '筹资活动产生的现金流量净额': 'net_financing_cash_flow', '汇率变动对现金及现金等价物的影响': 'exchange_rate_effects',
        '现金及现金等价物余额': 'final_cash_balance',
        #'期初现金及现金等价物余额': 'initial_cash_balance', '期末现金及现金等价物余额': 'final_cash_balance',
        '现金的期末余额': 'cash_end_balance'
    }

    english_to_chinese_mapping = {v: k for k, v in chinese_to_english_mapping.items()}
    data = dq.query_cash_flow_statement(stock_name)
    data.rename(columns=english_to_chinese_mapping, inplace=True)
    data = data[list(chinese_to_english_mapping.keys())]

    chinese_to_english_mapping = {k: v for k, v in chinese_to_english_mapping.items() if k not in ['年份', '证券代码', '证券简称']}

    total_q = find_best_match(q, chinese_to_english_mapping)

    if total_q:
        total_q = ['年份', '证券代码', '证券简称'] + total_q
        data = data[total_q]
        data = data.sort_values(by="年份")
        if '增长率' in q :
            for col in data.columns:
                if col not in ['年份', '证券代码', '证券简称']:
                    data[f"{col}增长率"] = data[col].pct_change() * 100
                    data[f"{col}上一年"] = data[col].shift(1)

            if len(year) != 0:
                data = data.loc[(data['年份'] == int(year[0]))]
            if data.empty:
                return ''
            sentences = data.apply(row_to_sentence, axis=1)
            sentences = '\n'.join(sentences)
        else:
            if len(year) != 0:
                data = data.loc[(data['年份'] == int(year[0]))]
            if data.empty:
                return ''
            sentences = data.apply(row_to_sentence_onlydata, axis=1)
            sentences = '\n'.join(sentences)
        return sentences
    else:
        return ''

def get_profit_statement_prompt(q,stock_name,year=[]):
    chinese_to_english_mapping = {'年份':'reporting_year','证券代码': 'stock_code', '证券简称': 'stock_name', '营业收入': 'total_revenue',  '其他业务收入': 'other_business_revenue',
                                  '营业成本': 'total_cost', '营业税金及附加': 'business_taxes_and_surcharges', '销售费用': 'selling_expenses', '管理费用': 'administrative_expenses',
                                  '研发费用': 'rd_expense', '财务费用': 'financial_expenses', '利息支出': 'interest_expenses', '利息收入': 'interest_income',
                                  '公允价值变动净收益': 'fair_value_change_income', '投资收益': 'investment_income', '营业利润': 'operating_profit',
                                  '营业外收入': 'non_operating_income', '营业外支出': 'non_operating_expenses', '利润总额': 'total_profit', '所得税费用': 'income_tax_expense',
                                  '净利润': 'net_profit', '其他收益': 'other_income', '综合收益总额': 'total_comprehensive_income',
                                  '每股收益': 'basic_earnings_per_share', '稀释每股收益': 'diluted_earnings_per_share'}
    english_to_chinese_mapping = {v: k for k, v in chinese_to_english_mapping.items()}
    data = dq.query_profit_statement(stock_name)
    data.rename(columns=english_to_chinese_mapping, inplace=True)
    data = data[list(chinese_to_english_mapping.keys())]

    chinese_to_english_mapping = {k: v for k, v in chinese_to_english_mapping.items() if k not in ['年份', '证券代码', '证券简称']}
    total_q = find_best_match(q, chinese_to_english_mapping)

    if total_q:
        total_q = ['年份', '证券代码', '证券简称'] + total_q
        data = data[total_q]
        data = data.sort_values(by="年份")
        if '增长率' in q :
            for col in data.columns:
                if col not in ['年份', '证券代码', '证券简称']:
                    data[f"{col}增长率"] = data[col].pct_change() * 100
                    data[f"{col}上一年"] = data[col].shift(1)
            if len(year) != 0:
                data = data.loc[(data['年份'] == int(year[0]))]
            if data.empty:
                return ''
            sentences = data.apply(row_to_sentence, axis=1)
            sentences = '\n'.join(sentences)
        else:
            if len(year) != 0:
                data = data.loc[(data['年份'] == int(year[0]))]
            if data.empty:
                return ''
            sentences = data.apply(row_to_sentence_onlydata, axis=1)
            sentences = '\n'.join(sentences)
        return sentences
    else:
        return ''

def calculate_indicator(year_, stock_name,index_name):
    financial_formulas = {
    "资产负债比率": (["总负债", "总资产"], "总负债 / 总资产 × 100"),
    "营业利润率": (["营业利润", "营业收入"], "营业利润 / 营业收入 × 100"),
    "速动比率": (["流动资产合计", "存货", "流动负债合计"], "(流动资产合计 - 存货) / 流动负债合计"),
    "流动比率": (["流动资产合计", "流动负债合计"], "流动资产合计 / 流动负债合计"),
    "现金比率": (["货币资金", "流动负债合计"], "货币资金 / 流动负债合计"),
    "净利润率": (["净利润", "营业收入"], "净利润 / 营业收入 × 100"),
    "毛利率": (["营业收入", "营业成本"], "(营业收入-营业成本) / 营业收入 × 100"),
    "财务费用率": (["财务费用", "营业收入"], "财务费用 / 营业收入 × 100"),
    "营业成本率": (["营业成本", "营业收入"], "营业成本 / 营业收入 × 100"),
    "管理费用率": (["管理费用", "营业收入"], "管理费用 / 营业收入 × 100"),
    "流动负债比率": (["流动负债合计", "总负债"], "流动负债合计 / 总负债 × 100"),
    "非流动负债比率": (["非流动负债合计", "总负债"], "非流动负债合计 / 总负债× 100"),
    "投资收益占营业收入比率": (["投资收益", "营业收入"], "投资收益 / 营业收入× 100"),
    "研发经费与利润比值": (["研发费用", "净利润"], "研发费用 / 净利润"),
    "三费比重": (["管理费用", "财务费用","销售费用","营业收入"],"(管理费用+财务费用+销售费用) / 营业收入"),
    "研发经费与营业收入比值": (["研发费用", "营业收入"], "研发费用 / 营业收入"),
    "企业研发经费占费用": (["销售费用","财务费用","管理费用","研发费用"], "研发费用 / (研发费用+管理费用+财务费用+销售费用)"),
    }
    formula_data = financial_formulas[index_name]
    data_values = {}
    values_str = []
    finance_data = dq.get_financial_data(year_, stock_name)
    if len(finance_data)==0:
        return None

    for field in formula_data[0]:
        value = finance_data.get(field)
        data_values[field] = value
        values_str.append(f"{year_}年{field}为{value:.2f}元")
    result_str = ', '.join(values_str)
    formula_str = formula_data[1]
    calculation_str = formula_str.replace("×", "*").replace(" ", "")
    for key, value in data_values.items():
        calculation_str = calculation_str.replace(key, str(value))
    try:
        result_value = eval(calculation_str)
    except Exception as e :
        print(calculation_str)
        return None
    if index_name in ["速动比率","流动比率"]:
        return f"{stock_name}{result_str}，根据公式:{index_name}={formula_str}，得出结果{stock_name}{year_}年{index_name}{result_value:.2f}。"
    else:
        return f"{stock_name}{result_str}，根据公式:{index_name}={formula_str}，得出结果{stock_name}{year_}年{index_name}{result_value:.2f}%。"

class GLMPrompt:
    def __init__(self):
        self.company_data = self._load_company_data()
        self.name_to_info = self.company_data.set_index('company_short_name')['info'].to_dict()
        self.full_names = set(self.company_data['company_full_name'])
        self.short_names = set(self.company_data['company_short_name'])
        self.stock_codes = set(self.company_data['stock_code'])

    @staticmethod
    def _load_company_data():
        data = dq.query_company_annual_reports()
        data['info'] = data.apply(
            lambda row: f"证券全称:{row['company_full_name']}||证券简称:{row['company_short_name']}||证券代码:{row['stock_code']}",
            axis=1
        )
        return data

    @staticmethod
    def find_years(search_str, years=['2019', '2020', '2021']):
        found_years = [year for year in years if year in search_str]
        return bool(found_years), found_years

    def has_stock(self,search_str):
        data = dq.query_company_annual_reports()
        data['info'] = data.apply(lambda
                                      row: f"证券全称:{row['company_full_name']}||证券简称:{row['company_short_name']}||证券代码:{row['stock_code']}",
                                  axis=1)
        full_names = set(data['company_full_name'])
        short_names = set(data['company_short_name'])
        stock_codes = set(data['stock_code'])

        info_dict = data.set_index('company_short_name')['info'].to_dict()

        for name_set, name_column in [(full_names, 'company_full_name'), (short_names, 'company_short_name'),
                                      (stock_codes, 'stock_code')]:
            matched_name = next((name for name in name_set if name in search_str), None)
            if matched_name:
                company_short_name = data[data[name_column] == matched_name]['company_short_name'].values[0]
                return company_short_name, info_dict[company_short_name], True

        return '', '', False

    def handler_q(self, q):
        contains_year, year_ = self.find_years(q)
        stock_name, stock_info, has_q = self.has_stock(q)

        if has_q:
            prompts = [
                get_profit_statement_prompt(q, stock_name, year_),
                get_balance_sheet_prompt(q, stock_name, year_),
                get_cash_flow_statement_prompt(q, stock_name, year_),
                get_balance_static(q, stock_name, year_)
            ]
            prompt_res = [prompt for prompt in prompts if len(prompt) > 5]
            if prompt_res:
                prompt_res = '\n'.join(prompt_res)
                return template_manager.get_template("prompt_financial").format(context=stock_info+'\n'+prompt_res,question=q)
            else:
                keyword_mappings = {
                    ("员工", "人员", "职工", "硕士", "博士"): ("prompt_financial", dq.query_people_data(year_, stock_name)),
                    ("邮箱", "地址", "信箱", "法定代表", "网址", "网站"): ("prompt_financial", dq.query_basic_data(stock_name))
                }
                for keywords, (template, data_func) in keyword_mappings.items():
                    if any(keyword in q for keyword in keywords) and contains_year:
                        data = data_func
                        if data is None:
                            return template_manager.get_template("basic_input").format(context=stock_info, question=q)
                        else:
                            return template_manager.get_template(template).format(context=f"{stock_info}\n{data}", question=q)
                return template_manager.get_template("basic_input").format(context=stock_info, question=q)
        else:
            return template_manager.get_template("open_input").format(question=q)
