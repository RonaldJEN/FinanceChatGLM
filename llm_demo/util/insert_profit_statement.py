import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Float, Column, text
from .transfer_to_excel import pad_stock_codes

DATABASE_URL = "postgresql://dbusername:dbpassword@ip:port/db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()
schema_name = 'public'
table_name = 'profit_statement'
file_path = "../data/profit_statement.xlsx"

profit_statement_items = [
    ("reporting_year", Integer, "报告年份"),
    ("source_of_information", String(255), "信息来源"),
    ("stock_code", String(50), "股票代码"),
    ("stock_name", String(100), "股票简称"),
    ("total_revenue", Float, "营业总收入"),
    ("main_business_revenue", Float, "主营业务收入"),
    ("other_business_revenue", Float, "其他业务收入"),
    ("total_cost", Float, "营业总成本"),
    ("main_business_cost", Float, "主营业务成本"),
    ("other_business_cost", Float, "其他业务成本"),
    ("business_taxes_and_surcharges", Float, "营业税金及附加"),
    ("selling_expenses", Float, "销售费用"),
    ("administrative_expenses", Float, "管理费用"),
    ("rd_expense", Float, "研发费用"),
    ("financial_expenses", Float, "财务费用"),
    ("interest_expenses", Float, "利息费用"),
    ("interest_income", Float, "利息收入"),
    ("fair_value_change_income", Float, "公允价值变动净收益"),
    ("investment_income", Float, "投资净收益"),
    ("operating_profit", Float, "营业利润"),   # 这是新增的字段
    ("non_operating_income", Float, "营业外收入"),
    ("non_operating_expenses", Float, "营业外支出"),
    ("total_profit", Float, "利润总额"),
    ("income_tax_expense", Float, "所得税费用"),
    ("net_profit", Float, "净利润"),
    ("other_income", Float, "其他收益"),
    ("total_comprehensive_income", Float, "综合收益总额"),
    ("basic_earnings_per_share", Float, "基本每股收益"),
    ("diluted_earnings_per_share", Float, "稀释每股收益")
]

def create_table():
    columns = [Column('id', Integer, primary_key=True)]
    columns.extend([Column(item[0], item[1], comment=item[2]) for item in profit_statement_items])

    profit_statement_table = Table(table_name, metadata, *columns, schema=schema_name)
    profit_statement_table.create(engine, checkfirst=True)

    with engine.connect() as conn:
        table_comment = "上市公司利润表"
        conn.execute(text(f"COMMENT ON TABLE {schema_name}.{table_name} IS '{table_comment}'"))
    print(f"Table {schema_name}.{table_name} created with comments!")

def read_data_from_excel():
    df = pd.read_excel(file_path, engine='openpyxl')
    df["股票代码"] = pad_stock_codes(df["股票代码"])
    column_mapping = {item[2]: item[0] for item in profit_statement_items}
    return df[column_mapping.keys()].rename(columns=column_mapping)

def write_data_to_db(df):
    df.to_sql(table_name, engine, schema=schema_name, if_exists='append', index=False)
    print("Data successfully written to the database!")

if __name__ == "__main__":
    try:
        create_table()
        df = read_data_from_excel()
        write_data_to_db(df)
    except Exception as e:
        print(f"An error occurred: {e}")
