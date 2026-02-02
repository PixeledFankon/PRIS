
import streamlit as st
from mock_data import test_entity as default_data
from logic import check_rules

st.title("Rule-Based System Debugger")
st.write("Настрой входные данные и нажми кнопку.")

metric_value = st.sidebar.number_input(
    "Метрика (число):",
    value=int(default_data["metric_value"])
)

is_verified = st.sidebar.checkbox(
    "Объект верифицирован (True/False):",
    value=bool(default_data["is_verified"])
)

tags_text = st.sidebar.text_input(
    "Теги (через запятую):",
    value=",".join(default_data["tags_list"])
)

tags_list = [t.strip() for t in tags_text.split(",") if t.strip()]

if st.button("Запустить проверку"):
    current_test_data = {
        "category_text": default_data["category_text"],
        "metric_value": metric_value,
        "tags_list": tags_list,
        "is_verified": is_verified
    }

    result = check_rules(current_test_data)

    if result.startswith("SUCCESS"):
        st.success(result)
    elif result.startswith("CRITICAL") or result.startswith("ERROR"):
        st.error(result)
    else:
        st.warning(result)

