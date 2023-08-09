from langchain import PromptTemplate

class TemplateManager:
    def __init__(self):
        self.templates = {
            "open_input": PromptTemplate(
                input_variables=["question"],
                template="简洁和专业的来回答用户的问题，在回答涉及数字的回复时，请用纯数字，若问题有要求小数点请遵守。"
                          "如果无法从中得到答案，可以乱编或改写提问句子回复。答案请使用中文。 问题是：{question}."
            ),
            "basic_input": PromptTemplate(
                input_variables=["context", "question"],
                template="已知信息：\n{context}\n"
                         "简洁和专业的来回答用户的问题，在回答涉及数字的回复时，请用纯数字，若问题有要求小数点请遵守。"
                         "如果无法从中得到答案，可以乱编。答案请使用中文。 问题是：{question}."
            ),
            "ratio_input": PromptTemplate(
                input_variables=["context","question"],
                template="已知信息：\n{context}\n" \
                        "简洁和专业的来回答用户的问题，在回答涉及数字的回复时，请用纯数字，若问题有要求小数点请遵守，增长率请列出公式和过程。如果无法从中得到答案，可以改写提问句子回复。答案请使用中文。 问题是：{question}."
            ),
            "prompt_financial": PromptTemplate(
                input_variables=["context", "question"],
                template="【任务要求】\n" \
                        "请按照以下的步骤和要求，回答提问：\n" \
                        "第一，读取并理解【背景知识】。\n" \
                        "第二，财务指标的增长率【背景知识】里已算好，直接取即可。\n" \
                        "第三，整理你找到或计算出的数据。若涉及数字，请用纯数字。\n" \
                        "第四，若回答需要计算，请明确并简洁地给出计算步骤。\n" \
                        "第五，遵守小数点的要求，确保答案精确性。\n" \
                        "第六，用中文表述并回答问题。\n" \
                        "第七，涉及比率，请用百分比% 。\n" \
                         "如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”。答案请使用中文。\n"\
                         "【背景知识】\n"\
                         "{context}\n"\
                         "【提问】\n"\
                         "{question}\n" \
)
        }

    def get_template(self, template_name):
        return self.templates.get(template_name, None)

template_manager = TemplateManager()
