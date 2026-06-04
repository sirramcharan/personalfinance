"""Data persistence and state management for the finance app."""

import json
import os
from datetime import datetime
from typing import Any

# Storage path (local JSON for now, can extend to Google Sheets)
DATA_DIR = "data"
DEFAULT_FILE = os.path.join(DATA_DIR, "finance_data.json")

# User defaults (Charan's profile)
DEFAULT_DATA = {
    "profile": {
        "name": "Charan",
        "location": "Bangalore",
        "stipend_monthly": 65000,
        "transfer_to_parents": 20000,
        "rent": 15000,
        "food": 7000,
    },
    "income": {
        "salary_monthly": 65000,
        "other_income": [],  # [{"source": "...", "amount": 0, "recurring": True}]
    },
    "expenses": {
        "fixed": {
            "rent": 15000,
            "transfer_to_parents": 20000,
            "food_groceries": 7000,
            "transport": 2000,
            "phone_bill": 500,
            "utilities": 1000,
        },
        "variable": {
            "dining_out": 3000,
            "entertainment": 2000,
            "shopping": 2000,
            "miscellaneous": 2000,
        },
        "categories": ["rent", "transfer_to_parents", "food_groceries", "transport",
                       "phone_bill", "utilities", "dining_out", "entertainment",
                       "shopping", "miscellaneous"],
    },
    "loan": {
        "type": "education",
        "principal": 2500000,
        "interest_rate_annual": 9.5,
        "tenure_months": 120,
        "emi_start_date": None,  # e.g., "2026-10-01" or "2027-10-01"
        "current_balance": 2500000,
        "status": "moratorium",  # moratorium, active, prepaid
        "gold_collateral_value": 0,
        "gold_loan_rate": 10.5,
    },
    "savings": {
        "emergency_fund_target": 150000,
        "current_emergency": 50000,
        "sip_monthly": 10000,
        "sip_rate_annual": 12,
        "investments": [],  # [{"name": "...", "amount": 0, "type": "..."}]
    },
    "goals": [],  # [{"name": "...", "target_amount": 0, "current": 0, "deadline": "..."}]
    "net_worth": {
        "cash": 50000,
        "bank_balance": 100000,
        "investments": 200000,
        "liabilities": 2500000,
    },
    "history": [],  # [{"date": "...", "type": "income|expense|transfer", "amount": 0, "category": "..."}]
}


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_data(path: str = None) -> dict:
    """Load data from JSON file or return defaults."""
    path = path or DEFAULT_FILE
    _ensure_data_dir()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge with defaults for any missing keys
                return _deep_merge(DEFAULT_DATA, data)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()


def save_data(data: dict, path: str = None):
    """Save data to JSON file."""
    path = path or DEFAULT_FILE
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def reset_to_defaults(path: str = None):
    """Reset data file to defaults."""
    save_data(DEFAULT_DATA.copy(), path or DEFAULT_FILE)


class DataManager:
    """Central data manager with session state integration."""

    def __init__(self, data_path: str = None):
        self.path = data_path or DEFAULT_FILE
        self._data = None
        self.load()

    def load(self):
        self._data = load_data(self.path)

    def save(self):
        save_data(self._data, self.path)

    @property
    def data(self) -> dict:
        return self._data

    def get_profile(self) -> dict:
        return self._data["profile"]

    def get_income(self) -> dict:
        return self._data["income"]

    def get_expenses(self) -> dict:
        return self._data["expenses"]

    def get_loan(self) -> dict:
        return self._data["loan"]

    def get_savings(self) -> dict:
        return self._data["savings"]

    def get_goals(self) -> list:
        return self._data["goals"]

    def get_net_worth(self) -> dict:
        return self._data["net_worth"]

    def get_history(self) -> list:
        return self._data["history"]

    def add_history_entry(self, entry: dict):
        entry["date"] = entry.get("date", datetime.now().strftime("%Y-%m-%d %H:%M"))
        self._data["history"].append(entry)
        self.save()

    def update_profile(self, updates: dict):
        self._data["profile"].update(updates)
        self.save()

    def update_expense(self, category: str, amount: float, is_fixed: bool = True):
        section = "fixed" if is_fixed else "variable"
        self._data["expenses"][section][category] = amount
        if category not in self._data["expenses"]["categories"]:
            self._data["expenses"]["categories"].append(category)
        self.save()

    def add_goal(self, goal: dict):
        self._data["goals"].append(goal)
        self.save()

    def update_goal(self, index: int, updates: dict):
        if 0 <= index < len(self._data["goals"]):
            self._data["goals"][index].update(updates)
            self.save()

    def update_net_worth(self, updates: dict):
        self._data["net_worth"].update(updates)
        self.save()

    def update_loan(self, updates: dict):
        self._data["loan"].update(updates)
        self.save()
