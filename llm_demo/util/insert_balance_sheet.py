from sqlalchemy import create_engine, MetaData, Table, String, Column, Integer, text, Float
import pandas as pd
from llm_demo.util.transfer_to_excel import pad_stock_codes

DATABASE_URL = "postgresql://dbusername:dbpassword@ip:port/db"
FILE_PATH = "../data/balance_sheet.xlsx"
SCHEMA_NAME = 'public'
TABLE_NAME = 'balance_sheet'
TABLE_COMMENT = "上市公司资产负债表"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Balance Sheet columns and comments
balance_sheet_items = [
    ("reporting_year", Integer, "报告年份"),
    ("source_of_information", String(255), "信息来源"),
    ("stock_code", String(50), "股票代码"),
    ("stock_name", String(100), "股票名称"),
    ("cash", Float, "货币资金"),
    ("receivables", Float, "应收票据"),
    ("interest_receivable", Float, "应收利息"),
    ("accounts_receivable", Float, "应收账款"),
    ("other_receivables", Float, "其他应收款"),
    ("prepayments", Float, "预付款项"),
    ("inventories", Float, "存货"),
    ("non_current_assets_due_within_one_year", Float, "一年内到期的非流动资产"),
    ("other_current_assets", Float, "其他流动资产"),
    ("investment_property", Float, "投资性房地产"),
    ("long_term_equity_investments", Float, "长期股权投资"),
    ("long_term_receivables", Float, "长期应收款"),
    ("fixed_assets", Float, "固定资产"),
    ("construction_materials", Float, "工程物资"),
    ("construction_in_progress", Float, "在建工程"),
    ("intangible_assets", Float, "无形资产"),
    ("goodwill", Float, "商誉"),
    ("long_term_prepaid_expenses", Float, "长期待摊费用"),
    ("deferred_tax_assets", Float, "递延所得税资产"),
    ("other_non_current_assets", Float, "其他非流动资产"),
    ("short_term_borrowings", Float, "短期借款"),
    ("bills_payable", Float, "应付票据"),
    ("accounts_payable", Float, "应付账款"),
    ("receipts_in_advance", Float, "预收款项"),
    ("employee_benefits_payable", Float, "应付职工薪酬"),
    ("dividends_payable", Float, "应付股利"),
    ("taxes_payable", Float, "应交税费"),
    ("interest_payable", Float, "应付利息"),
    ("other_payables", Float, "其他应付款"),
    ("non_current_liabilities_due_within_one_year", Float, "一年内到期的非流动负债"),
    ("other_current_liabilities", Float, "其他流动负债"),
    ("long_term_borrowings", Float, "长期借款"),
    ("bonds_payable", Float, "应付债券"),
    ("long_term_payables", Float, "长期应付款"),
    ("provisions", Float, "预计负债"),
    ("deferred_tax_liabilities", Float, "递延所得税负债"),
    ("other_non_current_liabilities", Float, "其他非流动负债"),
    ("paid_in_capital", Float, "实收资本"),
    ("capital_reserve", Float, "资本公积"),
    ("surplus_reserve", Float, "盈余公积"),
    ("undistributed_profit", Float, "未分配利润"),
    ("other_comprehensive_income", Float, "其他综合收益"),
    ("long_term_employee_benefits_payable", Float, "长期应付职工薪酬"),
    ("long_term_deferred_income", Float, "长期递延收益"),
    ("contract_assets", Float, "合同资产"),
    ("other_non_current_financial_assets", Float, "其他非流动金融资产"),
    ("notes_and_accounts_payable", Float, "应付票据及应付账款"),
    ("contractual_obligations", Float, "合同负债"),
    ("other_equity_instruments_investments", Float, "其他权益工具投资"),
    ("total_liabilities", Float, "总负债"),
    ("total_assets", Float, "总资产"),
    ("net_assets", Float, "净资产")
]

def create_table():
    columns = [Column('id', Integer, primary_key=True)] + [
        Column(item_name, data_type, comment=comment) for item_name, data_type, comment in balance_sheet_items
    ]
    balance_sheet_table = Table(TABLE_NAME, metadata, *columns, schema=SCHEMA_NAME)
    balance_sheet_table.create(engine, checkfirst=True)

    # Add table comments
    with engine.connect() as conn:
        conn.execute(text(f"COMMENT ON TABLE {SCHEMA_NAME}.{TABLE_NAME} IS '{TABLE_COMMENT}'"))
    logger.info(f"Table {SCHEMA_NAME}.{TABLE_NAME} created with comments!")

def read_excel_and_process():
    df = pd.read_excel(FILE_PATH, engine='openpyxl')
    df["股票代码"] = pad_stock_codes(df["股票代码"])
    column_mapping = {item[2]: item[0] for item in balance_sheet_items}
    df = df.rename(columns=column_mapping)
    df = df[[item[0] for item in balance_sheet_items]]
    return df

def write_to_database(df):
    df.to_sql(TABLE_NAME, engine, schema=SCHEMA_NAME, if_exists='append', index=False)
    print("Data successfully written to the database!")

def main():
    try:
        create_table()
        df = read_excel_and_process()
        write_to_database(df)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()