
import pandas as pd

def pad_stock_codes(stock_series):
    stock_series = stock_series.astype(str).str.strip()
    stock_series_padded = stock_series.str.zfill(6)
    return stock_series_padded

def process_csv_to_excel(csv_path, excel_path, columns, sep="\001"):
    data = pd.read_csv(csv_path, sep=sep, header=None)
    data.columns = columns
    data['报告年份'] = data['报告年份'].str.replace('年', '')
    data["股票代码"] = pad_stock_codes(data["股票代码"])
    data['股票代码'] = data['股票代码'].astype(str)
    data = data.astype(str)
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        data.to_excel(writer, index=False)
    result_df = pd.read_excel(excel_path)
    result_df["股票代码"] = pad_stock_codes(result_df["股票代码"])
    result_df.to_excel(excel_path, index=False)

profit_columns = [
    "报告年份","信息来源","股票代码","股票简称", "营业总收入", "主营业务收入", "其他业务收入",
    "营业总成本", "主营业务成本", "其他业务成本", "营业税金及附加", "销售费用", "管理费用",
    "研发费用", "财务费用", "利息费用", "利息收入", "公允价值变动净收益", "投资净收益", "营业利润",
    "营业外收入", "营业外支出", "利润总额", "所得税费用", "净利润", "其他收益", "综合收益总额",
    "基本每股收益", "稀释每股收益"
]
cash_columns = [
    "报告年份",
    "信息来源",
    "股票代码",
    "股票简称",
    "销售商品、提供劳务收到的现金",
    "收到的税费返还",
    "收到其他与经营活动有关的现金",
    "购买商品、接受劳务支付的现金",
    "支付给职工以及为职工支付的现金",
    "支付的各项税费",
    "支付其他与经营活动有关的现金",
    "经营活动产生的现金流量净额",
    "收回投资收到的现金",
    "取得投资收益收到的现金",
    "处置固定资产、无形资产和其他长期资产收回的现金净额",
    "处置子公司及其他营业单位收到的现金净额",
    "购建固定资产、无形资产和其他长期资产支付的现金",
    "投资支付的现金",
    "支付其他与投资活动有关的现金",
    "投资活动产生的现金流量净额",
    "吸收投资收到的现金",
    "取得借款收到的现金",
    "偿还债务支付的现金",
    "分配股利、利润或偿付利息支付的现金",
    "筹资活动产生的现金流量净额",
    "汇率变动对现金及现金等价物的影响",
    "期初现金及现金等价物余额",
    "期末现金及现金等价物余额",
    "现金的期末余额"
]
balance_columns = [
    "报告年份",
    "信息来源",
    "股票代码",
    "股票名称",
    "货币资金",
    "应收票据",
    "应收利息",
    "应收账款",
    "其他应收款",
    "预付款项",
    "存货",
    "一年内到期的非流动资产",
    "其他流动资产",
    "投资性房地产",
    "长期股权投资",
    "长期应收款",
    "固定资产",
    "工程物资",
    "在建工程",
    "无形资产",
    "商誉",
    "长期待摊费用",
    "递延所得税资产",
    "其他非流动资产",
    "短期借款",
    "应付票据",
    "应付账款",
    "预收款项",
    "应付职工薪酬",
    "应付股利",
    "应交税费",
    "应付利息",
    "其他应付款",
    "一年内到期的非流动负债",
    "其他流动负债",
    "长期借款",
    "应付债券",
    "长期应付款",
    "预计负债",
    "递延所得税负债",
    "其他非流动负债",
    "实收资本",
    "资本公积",
    "盈余公积",
    "未分配利润",
    "其他综合收益",
    "长期应付职工薪酬",
    "长期递延收益",
    "合同资产",
    "其他非流动金融资产",
    "应付票据及应付账款",
    "合同负债",
    "其他权益工具投资",
    "总负债",
    "总资产",
    "净资产"
]
balance_static_columns = [
    "报告年份",
    "信息来源",
    "股票代码",
    "股票简称",
    "流动资产合计",
    "非流动资产合计",
    "流动负债合计",
    "非流动负债合计"]
people_columns = [
    "报告年份",
    "信息来源",
    "股票代码",
    "股票简称",
    "职工人数",
    "研发人员",
    "研发人员比率",
    "硕士人数",
    "硕士以上人数",
    "博士人数",
    "博士以上人数"
]
basic_columns = [
    "报告年份",
    "信息来源",
    "股票代码",
    "股票简称",
    "办公地址",
    "注册地址",
    "公司邮箱",
    "法定代表人",
    "公司网址"
]

if __name__ == '__main__':
    process_csv_to_excel('../data/profit.csv', '../data/profit_statement.xlsx', profit_columns)
    process_csv_to_excel('../data/cashflow.csv', '../data/cash_flow_statement.xlsx', cash_columns)
    process_csv_to_excel('../data/balance.csv', '../data/balance_sheet.xlsx', balance_columns)
    process_csv_to_excel('../data/balance_static.csv', '../data/balance_static.xlsx', balance_static_columns)
    process_csv_to_excel('../data/people.csv', '../data/people.xlsx', people_columns)
    process_csv_to_excel('../data/baseinfo.csv', '../data/baseinfo.xlsx', basic_columns)