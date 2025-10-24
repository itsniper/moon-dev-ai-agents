# AI Agent Development Guide - Moon Dev AI Trading System

## 🏗️ Architecture Overview

**Modular Multi-Agent Trading System** with unified abstractions for LLM providers, exchanges, and shared utilities.

### Core Components
- **Agents** (`src/agents/`): 48+ specialized AI agents (trading, analysis, content creation)
- **Models** (`src/models/`): LLM provider abstraction via `ModelFactory.create_model()`
- **Exchange Manager** (`src/exchange_manager.py`): Unified trading across Solana/HyperLiquid/Aster
- **Shared Utilities** (`src/nice_funcs*.py`): 1200+ lines of trading functions
- **Configuration** (`src/config.py`): Global settings, risk limits, API configs
- **Data Storage** (`src/data/[agent_name]/`): Agent outputs and memory

### Data Flow Pattern
```
Config/Input → Agent Init → API Data Fetch → LLM Analysis → Decision → Data Storage
```

## 🤖 Agent Development Patterns

### Base Agent Inheritance
```python
from src.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__('my_agent', use_exchange_manager=True)
        # Agent-specific initialization
```

### LLM Integration (Required)
```python
from src.models.model_factory import ModelFactory

model = ModelFactory.create_model('claude')  # or 'openai', 'deepseek', 'groq', 'gemini', 'ollama', 'xai'
response = model.generate_response(system_prompt, user_content, temperature=0.7, max_tokens=1024)
```

### Standalone Execution Pattern
Every agent must be executable independently:
```python
if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```

### Data Storage Convention
Store outputs in `src/data/[agent_name]/` with descriptive filenames:
```python
output_dir = f"src/data/{self.type}"
os.makedirs(output_dir, exist_ok=True)
with open(f"{output_dir}/analysis_{timestamp}.json", 'w') as f:
    json.dump(results, f, indent=2)
```

## ⚙️ Configuration Patterns

### Global Config (`src/config.py`)
- Trading settings: `MONITORED_TOKENS`, position sizing, risk limits
- AI settings: `AI_MODEL`, `AI_MAX_TOKENS`, `AI_TEMPERATURE`
- Exchange selection: `EXCHANGE = 'hyperliquid'` (options: 'solana', 'hyperliquid')
- Risk management: `MAX_LOSS_USD`, `MINIMUM_BALANCE_USD`, `USE_AI_CONFIRMATION`

### Agent-Specific Config
Place ALL settings at top of agent file (lines 55-120):
```python
# Agent configuration section
USE_SWARM_MODE = True
usd_size = 25
max_usd_order_size = 3
MONITORED_TOKENS = ['token_address_1', 'token_address_2']
```

## 🌊 Swarm Consensus Pattern

Trading agents support dual-mode execution:

### Single Model Mode (~10s per token)
```python
USE_SWARM_MODE = False
# Uses single model from config.py AI_MODEL setting
```

### Swarm Mode (~45-60s per token)
```python
USE_SWARM_MODE = True
# Queries 6 models simultaneously: Claude, GPT-4, Gemini, Grok, DeepSeek, DeepSeek-R1
# Majority vote determines action with confidence percentage
```

## 💰 Exchange Abstraction

### Supported Exchanges
- **Solana**: On-chain DEX (long-only spot trading)
- **HyperLiquid**: Perpetuals (long/short with leverage)
- **Aster**: Futures DEX (long/short capable)

### Exchange Manager Usage
```python
from src.exchange_manager import ExchangeManager

em = ExchangeManager()
# Unified interface across all exchanges
position = em.get_position(token_address)
em.market_buy(token_address, usd_size)
```

### Trading Mode Configuration
```python
LONG_ONLY = True   # Long positions only (works on all exchanges)
LONG_ONLY = False  # Long & short positions (HyperLiquid/Aster only)
```

## 🛡️ Risk Management

### Risk-First Philosophy
Risk agent runs first in main orchestrator loop before any trading decisions.

### Circuit Breakers
- `MAX_LOSS_USD`: Stop trading if losses exceed threshold
- `MINIMUM_BALANCE_USD`: Emergency stop if balance too low
- `USE_AI_CONFIRMATION`: Consult AI before closing positions

### Position Sizing
- `usd_size`: Target position size (notional exposure)
- `max_usd_order_size`: Maximum order chunk size
- `MAX_POSITION_PERCENTAGE`: Max % allocation per position
- `CASH_PERCENTAGE`: Minimum cash buffer

## 📊 Data & API Patterns

### Market Data Fetching
```python
from src.nice_funcs import token_overview, get_ohlcv_data, token_price

# Comprehensive token data
overview = token_overview(token_address)

# Historical OHLCV data
ohlcv = get_ohlcv_data(token_address, timeframe='1H', days_back=3)

# Current price
price = token_price(token_address)
```

### API Sources
- **BirdEye**: Token data, price, volume, liquidity, OHLCV
- **Moon Dev API**: Custom signals (liquidations, funding, OI, copybot data)
- **CoinGecko**: Token metadata, market caps, sentiment
- **Helius RPC**: Solana blockchain interaction

## 🔄 Development Workflow

### Environment Setup
```bash
# Use existing conda environment (DO NOT create new)
conda activate tflow

# Install/update dependencies
pip install -r requirements.txt

# Update requirements.txt after adding packages
pip freeze > requirements.txt
```

### File Size Limits
- Keep agent files under 800 lines
- Split larger files into logical modules
- Update imports and documentation

### Testing & Validation
- Run agents standalone first: `python src/agents/my_agent.py`
- Test via main orchestrator: Enable in `ACTIVE_AGENTS` dict in `main.py`
- Validate with real market data (no synthetic data)

### Main Orchestrator
```python
# Enable agents in src/main.py ACTIVE_AGENTS dict
ACTIVE_AGENTS = {
    'my_agent': True,  # Enable for orchestration
    # ... other agents
}

# Run all active agents
python src/main.py
```

## 🎯 Key Conventions

### Naming Patterns
- Agent files: `[purpose]_agent.py` (e.g., `trading_agent.py`, `risk_agent.py`)
- Data directories: `src/data/[agent_name]/`
- Config variables: `SCREAMING_SNAKE_CASE`

### Error Handling
- Minimal try/except blocks (user wants to see errors)
- Graceful failure with logging
- Continue execution on individual agent failures

### Logging & Output
- Use `termcolor.cprint()` for colored console output
- Store structured data (JSON) for analysis
- Include timestamps in filenames

### Import Organization
```python
# Standard library
import os
import sys

# Third-party
import pandas as pd
from termcolor import cprint

# Local imports
from src.config import *
from src.models.model_factory import ModelFactory
```

## 🚀 Common Patterns

### RBI Agent (Research-Backtest-Implement)
1. Analyzes trading strategies from YouTube/PDF/text
2. Generates backtesting.py compatible code
3. Executes backtest and returns performance metrics
4. Cost: ~$0.027 per execution

### Strategy Development
Place strategies in `src/strategies/`:
```python
class MyStrategy(BaseStrategy):
    name = "my_strategy"
    description = "Strategy description"

    def generate_signals(self, token_address, market_data):
        return {
            "action": "BUY"|"SELL"|"NOTHING",
            "confidence": 0-100,
            "reasoning": "Explanation"
        }
```

### Backtesting
- Use `backtesting.py` library (NOT built-in indicators)
- Use `pandas_ta` or `talib` for technical indicators
- Sample data: `/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv`

## ⚠️ Critical Reminders

- **No synthetic data**: Always use real market data
- **Risk management first**: Test thoroughly before live trading
- **Update requirements.txt**: After any package additions
- **Standalone agents**: Every agent must run independently
- **Data organization**: Use date-based folders for RBI outputs
- **API key security**: Never expose keys in output or logs

## 🔧 Quick Agent Template

```python
"""
🌙 Moon Dev's [Agent Name] Agent
Built with love by Moon Dev 🚀
"""

from src.agents.base_agent import BaseAgent
from src.models.model_factory import ModelFactory
import json
import os
from datetime import datetime

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__('my_agent')
        self.model = ModelFactory.create_model('claude')

    def run(self):
        """Main agent execution logic"""
        cprint("🤖 Running My Agent...", "cyan")

        # Agent logic here
        results = {"status": "success", "timestamp": datetime.now().isoformat()}

        # Store results
        output_dir = f"src/data/{self.type}"
        os.makedirs(output_dir, exist_ok=True)

        with open(f"{output_dir}/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(results, f, indent=2)

        cprint("✅ My Agent completed", "green")

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```</content>
<parameter name="filePath">/Users/jus10sb/Documents/Finances/Trading/Crypto/Source/moon-dev-ai-agents/.github/copilot-instructions.md