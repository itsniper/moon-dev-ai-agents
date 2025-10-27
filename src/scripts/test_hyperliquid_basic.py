# Add project root to Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.exchange_manager import ExchangeManager

em = ExchangeManager()
print(f"Balance: ${em.get_balance():.2f}")
print(f"Account Value: ${em.get_account_value():.2f}")
