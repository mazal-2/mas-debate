import os
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from iFinDPy import *

class StockHunter:
    def __init__(self, dossier=None, storage_path: str = "./data/stocks"):
        self.dossier = dossier
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    
    def fetch_sector_data(self, sector_name: str, limit: int = 100, skip_exists: bool = True):
        """
        抓取指定板块的成分股近一年日频前复权数据，并保存为单个 CSV 文件
        """
        print(f"正在获取板块 [{sector_name}] 的成员名单...")
        try:
            stock_list_df = ak.stock_board_industry_cons_em(symbol=sector_name)
            stock_codes = stock_list_df['代码'].tolist()[:limit]
            print(f"获取到 {len(stock_codes)} 只成分股")
        except Exception as e:
            print(f"获取板块成分股失败: {e}")
            return []

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=370)).strftime("%Y%m%d")  # 多取几天以防节假日

        sector_dir = os.path.join(self.storage_path, sector_name.replace(" ", "_").replace("/", "_"))
        os.makedirs(sector_dir, exist_ok=True)

        downloaded = []

        for i, code in enumerate(stock_codes, 1):
            file_path = os.path.join(sector_dir, f"{code}.csv")

            if skip_exists and os.path.exists(file_path):
                print(f"[{i}/{len(stock_codes)}] 已存在，跳过: {code}")
                downloaded.append(code)
                continue

            print(f"[{i}/{len(stock_codes)}] 正在下载: {code} ... ", end="")
            try:
                df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                if df.empty:
                    print("数据为空")
                    continue

                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                print("成功")
                downloaded.append(code)
            except Exception as e:
                print(f"失败: {e}")

        print(f"\n板块 [{sector_name}] 下载完成，有效保存 {len(downloaded)} 只股票")
        return downloaded


