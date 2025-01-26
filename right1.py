from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import random
import time

# 初始化 WebDriver
chrome_service = Service(r"C:\Users\Administrator\Documents\script\chromedriver.exe")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--ignore-certificate-errors")  # 忽略 SSL 证书错误
chrome_options.add_argument("--allow-insecure-localhost")  # 允许不安全的本地连接


# 问卷页面链接
survey_url = "https://www.wenjuan.com/s/UZBZJv3yEv/"  # 替换为实际问卷链接

# 随机答案库
answers = {
    "您的性别": ["男", "女"],
    "您所学的专业是": ["计算机科学与技术", "土木工程", "信息工程", "数学与应用数学"],
    "您的民族是": ["汉族", "彝族", "壮族", "白族"],
    "您是否了解彝绣文创产品？": ["非常了解", "了解一些", "听说过但不太了解", "完全不了解"],
    "您对彝绣文创产品的总体态度？": ["非常感兴趣", "一般感兴趣", "不太感兴趣", "完全没有兴趣"],
    "您是否愿意购买彝绣文创产品？": ["非常愿意", "愿意","一般","不愿意"],
    "您曾经购买过彝绣文创产品吗？": ["买过", "没有买过"],
    "您认为宣传推广彝绣文创产品必要吗？":["有", "没有买过"] ,
    "您对彝绣文创产品的发展有何建议或看法？":["提高创新力度", "支持发展"] ,
}

# 访问问卷页面
driver.get(survey_url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
print("页面加载成功")

def click_continue():
    try:
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.continue-answering"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
        continue_button.click()
        print("已点击继续答题按钮")
        
        # 等待题目部分加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question-box"))
        )
    except Exception as e:
        print("未检测到继续答题按钮，可能无需此步骤。错误信息：", e)

click_continue()

def clean_question_text(question_text):
    """
    清理问题文本，去除多余符号、序号等，统一格式。
    """
    # 去除数字、特殊字符和多余空格
    import re
    question_text = re.sub(r"^[\d\*\.\s]+", "", question_text)  # 去掉前面的数字、*、. 和空格
    return question_text.replace("：", "").strip().lower()  # 去除冒号并转换为小写

def ensure_element_clickable(element):
    """
    确保元素可见并可以交互
    """
    try:
        if element.is_displayed() and element.is_enabled():
            element.click()
            print(f"成功点击选项：{element.text}")
        else:
            print(f"元素不可见或不可交互：{element.text}")
    except Exception as e:
        print(f"点击元素时出错：{e}")

def ensure_element_clickable_with_scroll(element):
    """
    滚动到元素位置后确保可交互
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        ensure_element_clickable(element)
    except Exception as e:
        print(f"滚动并点击元素时出错：{e}")

def answer_multiple_choice_question(options):
    """
    多选题逻辑：随机选择多个选项，但排除“其它”选项。
    """
    try:
        # 过滤掉包含“其它”的选项
        filtered_options = [option for option in options if "其它" not in option.text]
        if not filtered_options:
            print("多选题没有可选择的选项（除‘其它’外），跳过该题")
            return

        # 随机选择至少一个选项
        num_to_select = random.randint(1, len(filtered_options))  # 随机选择的数量
        selected_options = random.sample(filtered_options, num_to_select)

        # 点击选中的选项
        for option in selected_options:
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            ensure_element_clickable(option)
            print(f"多选题：已选择选项 - {option.text}")
        
        # 如果选中了“其它”，自动填写合理的内容
        for option in options:
            if "其它" in option.text:
                other_input = option.find_element(By.XPATH, "./following-sibling::textarea")
                if other_input:
                    other_input.send_keys("价格较高，需求不明确")
                    print("已为‘其它’选项填写内容")
    except Exception as e:
        print(f"处理多选题时出错：{e}")


def answer_radio_question(answer_options):
    """
    选择题逻辑：随机选择一个选项
    """
    try:
        random_choice = random.choice(answer_options)
        random_choice.click()
        print(f"已随机选择答案：{random_choice.text}")
    except Exception as e:
        print(f"随机选择答案时出错：{e}")



def answer_text_question(question_text, text_area):
    """
    填空题逻辑：
    1. 如果问题在答案库中，随机填写答案库中的答案；
    2. 如果问题不在答案库中，跳过并输出提示信息。
    """
    # 清理问题文本
    cleaned_question_text = clean_question_text(question_text)

    if cleaned_question_text in answers:
        # 从答案库中随机选择答案
        answer = random.choice(answers[cleaned_question_text])
        text_area.send_keys(answer)
        print(f"填空题已填写答案：{answer}")
    else:
        # 输出提示信息，跳过填写
        print(f"问题 '{question_text}' 不在答案库中，请手动补充答案库。跳过填写。")

def answer_sorting_question(options):
    """
    排序题逻辑：依次点击每一个选项。
    """
    try:
        print(f"进入排序题处理逻辑，总共有 {len(options)} 个选项")  # 打印选项数量
        for index, option in enumerate(options):
            print(f"尝试点击第 {index + 1} 个选项：{option.text}")  # 打印选项信息
            driver.execute_script("arguments[0].scrollIntoView(true);", option)  # 滚动到元素位置
            time.sleep(0.5)  # 等待避免操作过快
            driver.execute_script("arguments[0].click();", option)  # 强制点击选项
            print(f"成功点击第 {index + 1} 个选项：{option.text}")
    except Exception as e:
        print(f"处理排序题时出错：{e}")  # 捕获异常并打印详细信息





# 自动答题部分
questions = driver.find_elements(By.CLASS_NAME, "question-box")
for question in questions:
    try:
        # 提取问题文本
        question_text = question.find_element(By.CLASS_NAME, "question-title").text.strip()
        print(f"正在处理问题：{question_text}")

        # 判断题目类型并调用相应的处理函数
        options = question.find_elements(By.CSS_SELECTOR, "div[id^='option-']")
        if options:
            if "排序" in question_text or "您对以下哪些" in question_text:
               # 调用排序题处理函数
                answer_sorting_question(options)

            elif "多选" in question_text:
                # 调用多选题处理函数
                answer_multiple_choice_question(options)
            else:
                # 调用单选题处理函数
                answer_radio_question(options)

        # 处理填空题
        text_areas = question.find_elements(By.CSS_SELECTOR, "textarea.ws-textarea__inner")
        for text_area in text_areas:
            answer_text_question(question_text, text_area)

    except Exception as e:
        print(f"处理问题时出错：{e}")



# 提交问卷
try:
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button#answer-submit-btn"))
    )
    submit_button.click()
    print("问卷已提交")
except Exception as e:
    print(f"提交问卷时出错：{e}")

# 关闭浏览器
time.sleep(500)
driver.quit()
