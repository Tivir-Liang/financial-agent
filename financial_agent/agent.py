import sys
import io
import contextlib
import json
import re  
import openai
import ssl  
import traceback
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# 工具层：Python 代码执行沙盒
# ─────────────────────────────────────────────
def execute_python_code(code_string: str) -> str:
    """改进版：增加自动调用、错误栈追踪和环境兼容性"""
    output_buffer = io.StringIO()
    
    # 自动补全 main() 调用
    if "def main():" in code_string and "main()" not in code_string.split('\n')[-2:]:
        code_string += "\n\nif __name__ == '__main__':\n    main()"

    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        
        with contextlib.redirect_stdout(output_buffer):
            exec_globals = {
                "__name__": "__main__",
                "pd": pd,
                "np": np
            } 
            exec(code_string, exec_globals)
            
        result = output_buffer.getvalue()
        return result if result.strip() else "代码执行成功，但没有任何 print 输出。请检查逻辑或数据源。"
        
    except BaseException: 
        error_msg = traceback.format_exc()
        return f"代码执行报错:\n{error_msg}"

# ─────────────────────────────────────────────
# 规划与执行层：Meta-Agent 大脑
# ─────────────────────────────────────────────
class AdvancedTeachingAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key="请输入你的DeepSeek API Key", 
            base_url="https://api.deepseek.com"
        )
        self.history = []
        
    def _generate_execution_plan(self, user_input: str) -> str:
        history_context = ""
        if self.history:
            history_context = "\n\n【历史对话上下文】（如果是追问，请参考以下背景）：\n" + "\n".join([f"{'学生' if m['role']=='user' else '导师'}: {m['content']}" for m in self.history[-4:]])

        meta_prompt = f"""
        你是一个资深的金融量化研发总监。{history_context}
        你的0基础学生提出了一个研究需求（或追问）："{user_input}"
        
        为了完成这个研究，你需要写一段极其详尽的 Prompt 给到底层负责写代码的 Agent。
        
        【强制约束】
        1. 【智能分析分流】：
           - 财务报表或日历事件类：明确指示底层使用 `yfinance` 对应接口提取并基础计算，【严禁】使用回归。
           - 市场定价类（如ERC、Beta）：指示底层使用 `statsmodels` 进行 OLS 回归，并用 `pandas_datareader` 获取对应数据。
        2. 【数据结构处理】：取消单一库限制。对于外部 API 的交互使用原生兼容的 pandas。
        3. 【精确数据源】：严禁使用 mock 数据。
        4. 【架构与稳定性】：要求底层代码必须包含充分的异常处理。
        
        【深度财务稳健性补丁】：
        1. **索引拍平**：`df = yf.download(...)` 之后，哪怕只下载一个标的，也必须写 `if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)`。
        2. **动态列名**：为了应对 Yahoo Finance 频繁修改字段，下载后必须打印 `df.columns`，并使用动态查找（如 `col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'`）来获取价格。
        3. **零报错退出**：不要因为找不到一个字段就直接崩溃，要尝试备份字段或打印详细的数据结构。
        4. 时间对齐审计：所有合并（merge）操作必须显式检查样本流失率，若流失率 > 50% 必须 print 警告。
        5. 频率一致性：严禁日频与季度频直接相加。
        6. 统计稳健性：必须对因变量进行 1% 和 99% 的缩尾处理（Winsorize）。
        7. 盈余公告特算：处理 `earnings_dates` 时，必须考虑交易日偏移（若公告时间在 16:00 之后，反应窗口应设为 T+1）。
        """
        response = self.client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "system", "content": meta_prompt}],
        )
        return response.choices[0].message.content

    def _generate_and_run_code(self, execution_plan: str, max_retries: int = 2) -> tuple:
        coder_system_prompt = """
        你是一个高级 Python 量化工程师。请严格按照用户的【需求文档】编写完整的 Python 代码。
        
        【架构与输出约束】：
        1. 你的回答必须且只能包含一段可以立即执行的 Python 代码，包裹在 ```python 和 ``` 之间。
        2. 必须处理 yfinance 返回的 MultiIndex 问题：如果 `yf.download` 返回了多层列名，请立即使用 `df.columns = df.columns.get_level_values(0)`。
        3. 必须在所有数据合并前清除时区信息（tz_localize(None)）。
        4. 代码长度不限，必须包含严谨的缺失值处理。
        5. 必须保持面向过程的脚本风格，【严禁】生成绘图代码。
        6. 必须通过 print() 打印出核心计算结果。
        7. **数据结构防灾**：使用 yfinance 下载数据后，必须第一时间检查是否为 MultiIndex 索引，如果是，立即执行 `df.columns = df.columns.get_level_values(0)`。
        8. **字段灵活匹配**：严禁直接取 `df['Adj Close']`，必须写一段逻辑判断：优先取 `Adj Close`，不存在则取 `Close`，并 print 告知。
        9. **时区中立性**：在所有 merge/join 操作前，必须强制执行 `df.index = df.index.tz_localize(None)`。
        """
        
        messages = [
            {"role": "system", "content": coder_system_prompt},
            {"role": "user", "content": f"这是你的【需求文档】：\n{execution_plan}"}
        ]
        
        for attempt in range(max_retries + 1):
            response = self.client.chat.completions.create(
                model="deepseek-v4-pro",
                messages=messages,
            )
            full_response = response.choices[0].message.content
            messages.append({"role": "assistant", "content": full_response}) 
            
            code_match = re.search(r"```python\n(.*?)\n```", full_response, re.DOTALL)
            if code_match:
                python_code = code_match.group(1)
            else:
                python_code = full_response.replace("```python\n", "").replace("\n```", "")
                
            execution_result = execute_python_code(python_code)
            
            if "代码执行报错:" not in execution_result:
                return python_code, execution_result 
                
            if attempt < max_retries:
                print(f"\n[⚠️ 沙盒报错] 正在让大模型自动 Debug (第 {attempt+1} 次重试)...")
                error_feedback = f"代码运行报错：\n{execution_result}\n提示：请检查 yfinance 的列索引是否为 MultiIndex？日期是否因为时区（timezone）没对齐导致合并后为空？请修复这些问题。"
                messages.append({"role": "user", "content": error_feedback})
                
        return python_code, execution_result

    def run_research(self, user_input: str):
        """主调度流"""
        print("1. [外层] 正在转化为执行指南...\n")
        execution_plan = self._generate_execution_plan(user_input)
        
        print("2. [内层] 接收指南，正在实时编写底层代码并执行...\n")
        python_code, execution_result = self._generate_and_run_code(execution_plan)
        
        print("--- Agent 最终生成的真实业务代码 ---")
        print(python_code)
        print("------------------------------------------\n")
        
        print("3. [底层沙盒] 代码运行结果:")
        print(execution_result)
        
        if "代码执行报错:" in execution_result:
            print("\n❌ 遗憾：代码经过多次尝试依然报错，本次研究中断。")
            return
            
        print("\n4. [外层] 正在将生硬的数据翻译为解析...\n")
        teaching_prompt = f"""
        学生问了这个问题（或提出了追问）：{user_input}
        底层跑代码得出的真实结果如下：
        {execution_result}
        请结合我们的上下文，用通俗的比喻解释数据的含义，并基于上述结果得出明确结论。
        """
        
        # 【新增】携带历史对话数组给讲课导师
        messages = [{"role": m["role"], "content": m["content"]} for m in self.history[-4:]] 
        messages.append({"role": "user", "content": teaching_prompt})

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True
        )
        
        full_reply = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_reply += content
        print("\n")
        
        # 【新增】将本轮问答计入历史，以备下次追问
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": full_reply})

if __name__ == "__main__":
    agent = AdvancedTeachingAgent()
    print("===========================================")
    print("🎓 你的financial Agent已上线！(输入 'q' 退出)")
    print("===========================================")

    while True:
        user_q = input("\n请提出你想研究的财务问题或继续追问：\n> ") 
        if user_q.strip().lower() in ['q', 'quit', 'exit']:
            print("研究结束。")
            break
        elif user_q.strip():
            agent.run_research(user_q) 
        else:
            continue