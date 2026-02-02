
import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(BASE_DIR, "data", "raw", "rules.json")


def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def check_rules(data: dict) -> str:
    rules = load_rules()

    if rules["critical_rules"]["must_be_verified"] and not data["is_verified"]:
        return "Критическая ошибка: объект не верифицирован"

    min_v = rules["thresholds"]["min_value"]
    max_v = rules["thresholds"]["max_value"]

    if data["metric_value"] < min_v:
        return f"Отказ: значение ниже минимума ({data['metric_value']} < {min_v})"
    if data["metric_value"] > max_v:
        return f"Отказ: значение выше максимума ({data['metric_value']} > {max_v})"

    for tag in data["tags_list"]:
        if tag in rules["lists"]["blacklist"]:
            return f"Предупреждение: найден запрещённый тег ({tag})"

    return f"Успех: объект соответствует сценарию '{rules['scenario_name']}'"
