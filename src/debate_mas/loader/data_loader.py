import pandas as pd
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime, timedelta
import numpy as np
from .dossier import Dossier


class DataLoader:
    """数据加载器，负责从各种源加载数据到Dossier"""

    @staticmethod
    def create_sample_dossier(mission: str = "构建科技股投资组合") -> Dossier:
        """创建示例dossier（用于测试）"""
        # 示例股票池
        tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "ADBE", "INTC", "AMD"]

        dossier = Dossier(
            mission=mission,
            stock_pool=tech_stocks
        )

        # 添加示例数值数据（股价信息）
        price_data = DataLoader._generate_sample_price_data(tech_stocks)
        dossier.add_numerical_document(
            title="股票价格数据",
            data=price_data,
            metadata={"type": "price", "period": "2024-01-01 to 2024-12-31"},
            source="simulated"
        )

        # 添加示例财务数据
        financial_data = DataLoader._generate_sample_financial_data(tech_stocks)
        dossier.add_numerical_document(
            title="财务指标数据",
            data=financial_data,
            metadata={"type": "financial", "metrics": ["PE", "PB", "ROE", "Debt/Equity"]},
            source="simulated"
        )

        # 添加示例文本数据（新闻）
        news_data = DataLoader._generate_sample_news_data(tech_stocks)
        for i, news in enumerate(news_data):
            dossier.add_textual_document(
                title=f"新闻摘要 {i+1}",
                text=news["content"],
                metadata={"stock": news["stock"], "sentiment": news["sentiment"]},
                source="simulated"
            )

        return dossier

    @staticmethod
    def load_from_yahoo_finance(dossier: Dossier, symbols: Optional[List[str]] = None,
                               period: str = "1mo") -> Dossier:
        """从Yahoo Finance加载真实数据"""
        try:
            import yfinance as yf
        except ImportError:
            print("yfinance not installed. Install with: pip install yfinance")
            return dossier

        symbols_to_load = symbols or dossier.stock_pool
        if not symbols_to_load:
            print("No symbols to load")
            return dossier

        # 加载价格数据
        try:
            tickers = yf.Tickers(" ".join(symbols_to_load))
            price_data = tickers.history(period=period)

            if not price_data.empty:
                # 转换为合适的格式
                price_df = price_data[['Close', 'Volume']].unstack(level=0)
                dossier.add_numerical_document(
                    title=f"Yahoo Finance价格数据 ({period})",
                    data=price_df,
                    metadata={"source": "yahoo_finance", "period": period},
                    source="yahoo_finance"
                )
                dossier.add_data_source("yahoo_finance")
        except Exception as e:
            print(f"Error loading Yahoo Finance data: {e}")

        return dossier

    @staticmethod
    def load_from_csv(dossier: Dossier, filepath: str, title: Optional[str] = None) -> Dossier:
        """从CSV文件加载数据"""
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return dossier

        try:
            df = pd.read_csv(filepath)
            if title is None:
                title = os.path.basename(filepath)

            dossier.add_numerical_document(
                title=title,
                data=df,
                metadata={"source": "csv", "filepath": filepath},
                source=filepath
            )
            dossier.add_data_source(filepath)
        except Exception as e:
            print(f"Error loading CSV file: {e}")

        return dossier

    @staticmethod
    def load_from_json(dossier: Dossier, filepath: str, title: Optional[str] = None) -> Dossier:
        """从JSON文件加载数据"""
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return dossier

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if title is None:
                title = os.path.basename(filepath)

            # 判断是数值数据还是文本数据
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # 可能是表格数据
                df = pd.DataFrame(data)
                dossier.add_numerical_document(
                    title=title,
                    data=df,
                    metadata={"source": "json", "filepath": filepath},
                    source=filepath
                )
            else:
                # 文本数据
                dossier.add_textual_document(
                    title=title,
                    text=str(data),
                    metadata={"source": "json", "filepath": filepath},
                    source=filepath
                )

            dossier.add_data_source(filepath)
        except Exception as e:
            print(f"Error loading JSON file: {e}")

        return dossier

    @staticmethod
    def _generate_sample_price_data(symbols: List[str]) -> pd.DataFrame:
        """生成示例价格数据"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='B')
        data = {}

        for symbol in symbols:
            # 模拟价格数据
            base_price = 100 + hash(symbol) % 200  # 伪随机基础价格
            returns = np.random.normal(0.0005, 0.02, len(dates))
            prices = base_price * np.exp(np.cumsum(returns))

            data[symbol] = pd.Series(prices, index=dates)

        return pd.DataFrame(data)

    @staticmethod
    def _generate_sample_financial_data(symbols: List[str]) -> pd.DataFrame:
        """生成示例财务数据"""
        metrics = ["PE", "PB", "ROE", "Debt/Equity", "Revenue_Growth", "Profit_Margin"]
        data = {}

        for symbol in symbols:
            row = {}
            row["PE"] = 20 + hash(symbol) % 30
            row["PB"] = 3 + hash(symbol) % 5
            row["ROE"] = 0.1 + (hash(symbol) % 20) / 100
            row["Debt/Equity"] = 0.5 + (hash(symbol) % 10) / 10
            row["Revenue_Growth"] = 0.05 + (hash(symbol) % 15) / 100
            row["Profit_Margin"] = 0.15 + (hash(symbol) % 10) / 100

            data[symbol] = row

        return pd.DataFrame.from_dict(data, orient='index')

    @staticmethod
    def _generate_sample_news_data(symbols: List[str]) -> List[Dict[str, Any]]:
        """生成示例新闻数据"""
        news_templates = [
            "{stock} reported better-than-expected earnings for Q4, with revenue growth of {growth}%.",
            "Analysts are raising price targets for {stock} following strong quarterly results.",
            "{stock} faces regulatory challenges in its key markets, potentially impacting future growth.",
            "New product launch from {stock} receives positive reviews from industry experts.",
            "{stock} announces major partnership that could drive future revenue streams."
        ]

        sentiments = ["positive", "negative", "neutral"]
        news_items = []

        for symbol in symbols:
            for i in range(2):  # 每个股票2条新闻
                template = news_templates[(hash(symbol) + i) % len(news_templates)]
                growth = 10 + hash(symbol) % 20
                content = template.format(stock=symbol, growth=growth)
                sentiment = sentiments[(hash(symbol) + i) % len(sentiments)]

                news_items.append({
                    "stock": symbol,
                    "content": content,
                    "sentiment": sentiment,
                    "date": (datetime.now() - timedelta(days=i*7)).strftime("%Y-%m-%d")
                })

        return news_items


