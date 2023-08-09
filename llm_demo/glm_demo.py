import json
from llm_demo.method.template_manager import template_manager
from llm_demo.method.prompt_generation import (
    get_balance_static, get_balance_sheet_prompt, get_profit_statement_prompt,
    get_cash_flow_statement_prompt, calculate_indicator, GLMPrompt
)
from modelscope.utils.constant import Tasks
from modelscope import Model
from modelscope.pipelines import pipeline
model = Model.from_pretrained('ZhipuAI/chatglm2-6b', device_map='auto', revision='v1.0.7')
pipe = pipeline(task=Tasks.chat, model=model)
COMPUTE_INDEX_SET = [
    '非流动负债比率', '资产负债比率', '营业利润率', '速动比率', '流动比率', '现金比率', '净利润率',
    '毛利率', '财务费用率', '营业成本率', '管理费用率', "企业研发经费占费用",
    '投资收益占营业收入比率', '研发经费与利润比值', '三费比重', '研发经费与营业收入比值', '流动负债比率'
]

def read_questions(path):
    with open(path, encoding="utf-8") as file:
        return [json.loads(line) for line in file.readlines()]

def process_question(question_obj):
    glm_prompt = GLMPrompt()

    q = question_obj['question']
    contains_year, year_ = glm_prompt.find_years(q)
    stock_name, stock_info, has_stock = glm_prompt.has_stock(q)
    compute_index = False

    if contains_year and has_stock:
        for t in COMPUTE_INDEX_SET:
            if t in q:
                prompt_res = calculate_indicator(year_[0], stock_name, index_name=t)
                if prompt_res is not None:
                    prompt_ = template_manager.get_template("ratio_input").format(context=prompt_res, question=q)
                    inputs_t = {'text': prompt_, 'history': []}
                    response_ = pipe(inputs_t)['response']
                    question_obj["answer"] = str(response_)
                    compute_index = True
                    break

    if not compute_index and '增长率' in q:
        statements = [
            get_profit_statement_prompt(q, stock_name, year_),
            get_balance_sheet_prompt(q, stock_name, year_),
            get_cash_flow_statement_prompt(q, stock_name, year_),
            get_balance_static(q, stock_name, year_)
        ]
        prompt_res = [stmt for stmt in statements if len(stmt) > 5]
        if prompt_res:
            prompt_ = template_manager.get_template("ratio_input").format(context=prompt_res, question=q)
            inputs_t = {'text': prompt_, 'history': []}
            response_ = pipe(inputs_t)['response']
            question_obj["answer"] = str(response_)
            compute_index = True

    if not compute_index:
        prompt_ = glm_prompt.handler_q(q=question_obj['question'])
        inputs_t = {'text': prompt_, 'history': []}
        response_ = pipe(inputs_t)['response']
        question_obj["answer"] = str(response_)

    with open("./submit_example.json", "a", encoding="utf-8") as f:
        json.dump(question_obj, f, ensure_ascii=False)
        f.write('\n')


if __name__ == '__main__':
    questions = read_questions("./data/test_questions.jsonl")

    for idx, question_obj in enumerate(questions):
        print(f'Processing question {idx}\n')
        process_question(question_obj)