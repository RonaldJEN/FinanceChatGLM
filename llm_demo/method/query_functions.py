import pandas as pd
import numpy as np
from functools import lru_cache
from sqlalchemy import create_engine


class DataQuery:
    DATABASE_URL = "postgresql://dbusername:dbpassword@ip:port/db"
    engine = create_engine(DATABASE_URL)

    def __init__(self):
        self.peopledata_path = './data/people.xlsx'
        self.basedata_path = './data/baseinfo.xlsx'
        self.balance_static_path = './data/balance_static.xlsx'

    @staticmethod
    def _row_to_sentence(row):
        year = row['报告年份']
        name = row['股票简称']
        data = dq.query_company_annual_reports()
        company_full_name = data[data['company_short_name'] == name]['company_full_name'].values[0]
        other_data = {k: v for k, v in row.items() if k not in ['报告年份', '证券代码', '证券简称']}
        details = " 。\n ".join([f"{col}为{value}" for col, value in other_data.items()])
        return f"- {name}(全称:{company_full_name})的{year}年报内容:\n{details}。\n"

    def query_people_data(self, report_year, stock_name):
        data = pd.read_excel(self.peopledata_path, index_col=None)
        data = data.loc[(data['股票简称'] == stock_name)]
        data = data.ffill().bfill()
        data.dropna(axis=0, how='any')
        data = data.loc[(data['报告年份'] == int(report_year[0]))]
        data = data.loc[:, (data != 0).any(axis=0)]

        if data.empty:
            return ''
        sentences = data.apply(self._row_to_sentence, axis=1)
        sentences = '\n -'.join(sentences)
        return sentences

    def query_basic_data(self, stock_name):
        data = pd.read_excel(self.basedata_path, index_col=None)
        data = data.loc[data['股票简称'] == stock_name]
        data = data.ffill().bfill()
        data.dropna(axis=0, how='any')
        if data.empty:
            return ''
        sentences = data.apply(self._row_to_sentence, axis=1)
        sentences = '\n -'.join(sentences)
        return sentences
    def query_balance_static_data(self):
        return pd.read_excel(self.balance_static_path)
    @lru_cache(maxsize=None)
    def query_company_annual_reports(self):
        query = f"""select DISTINCT  company_full_name,stock_code,company_short_name from company_annual_reports"""
        return pd.read_sql(query, self.engine)

    @lru_cache(maxsize=None)  # 设置缓存大小为1024
    def query_profit_statement(self, stock_name):
        # 假设这是一个查询数据库的昂贵操作
        query = f"""select * from profit_statement where   reporting_year in (2019,2020,2021) and stock_name='{stock_name}' """
        data = pd.read_sql(query, self.engine)
        return data

    @lru_cache(maxsize=None)
    def query_balance_sheet(self, stock_name):
        query = f"""select * from balance_sheet where  reporting_year in (2019,2020,2021) and  stock_name='{stock_name}' """
        return pd.read_sql(query, self.engine)

    @lru_cache(maxsize=None)
    def query_cash_flow_statement(self, stock_name):
        query = f"""select * from cash_flow_statement where reporting_year in (2019,2020,2021) and  stock_name='{stock_name}' """
        return pd.read_sql(query, self.engine)

    def get_financial_data(self, year, stock_name):
        query_balance = f"select total_liabilities, total_assets, inventories, cash from balance_sheet where reporting_year in ({year}) and stock_name='{stock_name}'"
        balance_data = pd.read_sql(query_balance, self.engine)

        excel_data = self.query_balance_static_data()
        filtered_data = excel_data.loc[
            (excel_data['证券简称'] == stock_name) & (excel_data['年份'] == int(year)), ['流动资产合计', '流动负债合计',
                                                                                         '非流动负债合计']]

        query_profit = f"select net_profit, total_revenue, total_cost, operating_profit, administrative_expenses, selling_expenses, financial_expenses, rd_expense, investment_income from profit_statement where reporting_year in ({year}) and stock_name='{stock_name}'"
        profit_data = pd.read_sql(query_profit, self.engine)

        try:
            combined_data = {
                '总负债': balance_data['total_liabilities'].iloc[0],
                '总资产': balance_data['total_assets'].iloc[0],
                '存货': balance_data['inventories'].iloc[0],
                '货币资金': balance_data['cash'].iloc[0],
                '流动资产合计': filtered_data['流动资产合计'].iloc[0],
                '流动负债合计': filtered_data['流动负债合计'].iloc[0],
                '非流动负债合计': filtered_data['非流动负债合计'].iloc[0],
                '净利润': profit_data['net_profit'].iloc[0],
                '营业收入': profit_data['total_revenue'].iloc[0],
                '营业成本': profit_data['total_cost'].iloc[0],
                '营业利润': profit_data['operating_profit'].iloc[0],
                '管理费用': profit_data['administrative_expenses'].iloc[0],
                '财务费用': profit_data['financial_expenses'].iloc[0],
                '研发费用': profit_data['rd_expense'].iloc[0],
                '销售费用': profit_data['selling_expenses'].iloc[0],
                '投资收益': profit_data['investment_income'].iloc[0],
            }
        except:
            combined_data = {}

        return combined_data


# 创建 DataQuery 的实例
dq = DataQuery()
