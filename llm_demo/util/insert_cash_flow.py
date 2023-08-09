import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Float, Column, text
from llm_demo.util.transfer_to_excel import pad_stock_codes

DATABASE_URL = "postgresql://dbusername:dbpassword@ip:port/db"
schema_name = 'public'
table_name = 'cash_flow_statement'
file_path = "../data/cash_flow_statement.xlsx"


engine = create_engine(DATABASE_URL)
metadata = MetaData()
cash_flow_statement_items = [
    ("reporting_year", Integer, "报告年份"),
    ("source_of_information", String(255), "信息来源"),
    ("stock_code", String(50), "股票代码"),
    ("stock_name", String(100), "股票简称"),
    ("sales_cash", Float, "销售商品、提供劳务收到的现金"),
    ("tax_refund", Float, "收到的税费返还"),
    ("other_operating_cash", Float, "收到其他与经营活动有关的现金"),
    ("purchase_goods_services_cash", Float, "购买商品、接受劳务支付的现金"),
    ("employee_wages_cash", Float, "支付给职工以及为职工支付的现金"),
    ("tax_payments", Float, "支付的各项税费"),
    ("other_cash_related_operations", Float, "支付其他与经营活动有关的现金"),
    ("net_operating_cash_flow", Float, "经营活动产生的现金流量净额"),
    ("investment_recovery_cash", Float, "收回投资收到的现金"),
    ("investment_profit_cash", Float, "取得投资收益收到的现金"),
    ("dispose_assets_cash", Float, "处置固定资产、无形资产和其他长期资产收回的现金净额"),
    ("dispose_subsidiary_cash", Float, "处置子公司及其他营业单位收到的现金净额"),
    ("purchase_fixed_assets_cash", Float, "购建固定资产、无形资产和其他长期资产支付的现金"),
    ("investment_payments_cash", Float, "投资支付的现金"),
    ("other_investment_activity_cash", Float, "支付其他与投资活动有关的现金"),
    ("net_investment_cash_flow", Float, "投资活动产生的现金流量净额"),
    ("investment_received_cash", Float, "吸收投资收到的现金"),
    ("loan_received_cash", Float, "取得借款收到的现金"),
    ("debt_repayment_cash", Float, "偿还债务支付的现金"),
    ("dividend_interest_payment_cash", Float, "分配股利、利润或偿付利息支付的现金"),
    ("net_financing_cash_flow", Float, "筹资活动产生的现金流量净额"),
    ("exchange_rate_effects", Float, "汇率变动对现金及现金等价物的影响"),
    ("initial_cash_balance", Float, "期初现金及现金等价物余额"),
    ("final_cash_balance", Float, "期末现金及现金等价物余额"),
    ("cash_end_balance", Float, "现金的期末余额")
]

def create_table():
    columns = [Column('id', Integer, primary_key=True)]
    columns.extend([Column(item[0], item[1], comment=item[2]) for item in cash_flow_statement_items])

    cash_flow_statement_table = Table(table_name, metadata, *columns, schema=schema_name)
    cash_flow_statement_table.create(engine, checkfirst=True)

    with engine.connect() as conn:
        table_comment = "上市公司现金流量表"
        conn.execute(text(f"COMMENT ON TABLE {schema_name}.{table_name} IS '{table_comment}'"))
    print(f"Table {schema_name}.{table_name} created with comments!")

def read_data_from_excel():
    df = pd.read_excel(file_path, engine='openpyxl')
    df["股票代码"] = pad_stock_codes(df["股票代码"])
    column_mapping = {item[2]: item[0] for item in cash_flow_statement_items}
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


