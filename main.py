import os
import pandas as pd
from iFinDPy import *

# ===================== 核心配置（替换成你的账号密码） =====================
IFIND_ACCOUNT = "bjffsm006"  # 或用os.getenv("IFIND_ACCOUNT")
IFIND_KEY = "k5wY93kE"      # 或用os.getenv("IFIND_KEY")
SAVE_PATH = "./data//stock_data/semiconductor_data.csv"  # 数据保存路径
BATCH_SIZE = 20  # 每批抓取20只股票（确保单次数据<1万条）

# ===================== 完整股票列表 + 抓取参数 =====================
# 你的全部半导体股票代码（已还原完整列表）
STOCK_CODES_FULL = "920179.BJ,600206.SH,605358.SH,688126.SH,688138.SH,688146.SH,688233.SH,688234.SH,688401.SH,688432.SH,688530.SH,688535.SH,688584.SH,688661.SH,688720.SH,688721.SH,688727.SH,688783.SH,002119.SZ,002409.SZ,003026.SZ,300666.SZ,300706.SZ,301611.SZ,301678.SZ,600360.SH,600460.SH,600745.SH,603290.SH,605111.SH,688048.SH,688167.SH,688172.SH,688230.SH,688261.SH,688498.SH,688689.SH,688693.SH,688711.SH,300046.SZ,300373.SZ,300623.SZ,300831.SZ,603501.SH,603893.SH,603986.SH,688008.SH,688018.SH,688041.SH,688047.SH,688049.SH,688099.SH,688107.SH,688110.SH,688123.SH,688213.SH,688252.SH,688256.SH,688259.SH,688262.SH,688279.SH,688332.SH,688380.SH,688385.SH,688416.SH,688449.SH,688486.SH,688521.SH,688525.SH,688589.SH,688591.SH,688593.SH,688595.SH,688608.SH,688620.SH,688702.SH,688709.SH,688728.SH,688766.SH,688795.SH,688802.SH,688807.SH,001309.SZ,002049.SZ,002213.SZ,300053.SZ,300077.SZ,300223.SZ,300327.SZ,300458.SZ,300613.SZ,300672.SZ,301308.SZ,301536.SZ,600171.SH,600877.SH,603068.SH,603160.SH,603375.SH,688045.SH,688052.SH,688061.SH,688130.SH,688141.SH,688153.SH,688173.SH,688209.SH,688220.SH,688270.SH,688286.SH,688325.SH,688368.SH,688381.SH,688391.SH,688458.SH,688484.SH,688508.SH,688512.SH,688515.SH,688536.SH,688582.SH,688601.SH,688653.SH,688699.SH,688790.SH,688798.SH,300661.SZ,300671.SZ,300782.SZ,688249.SH,688347.SH,688396.SH,688469.SH,688691.SH,688981.SH,300456.SZ,920139.BJ,600584.SH,603005.SH,688135.SH,688216.SH,688352.SH,688362.SH,688372.SH,688403.SH,002077.SZ,002156.SZ,002185.SZ,301348.SZ,603061.SH,603690.SH,603991.SH,688012.SH,688037.SH,688072.SH,688082.SH,688120.SH,688200.SH,688361.SH,688409.SH,688419.SH,688478.SH,688605.SH,688652.SH,688729.SH,688785.SH,688809.SH,002371.SZ,003043.SZ,300604.SZ,301297.SZ,301369.SZ,301629.SZ"

# 抓取参数（最近3个月）
indicators = "ths_close_price_stock;ths_high_price_stock;ths_low_stock;ths_open_price_stock;ths_chg_ratio_stock;ths_vol_stock"
indicator_params = "0;0;0;0;0;0"
start_date = "2026-01-01"
end_date = "2026-03-22"

# ===================== 核心逻辑：分批抓取 + 合并保存 =====================
def main():
    # 1. 拆分股票列表为批次
    stock_list = [code.strip() for code in STOCK_CODES_FULL.split(",") if code.strip()]
    batches = [stock_list[i:i+BATCH_SIZE] for i in range(0, len(stock_list), BATCH_SIZE)]
    print(f"共{len(stock_list)}只股票，拆分为{len(batches)}批（每批{BATCH_SIZE}只）")

    # 2. 初始化总数据容器
    all_data = pd.DataFrame()

    # 3. 登录iFinD（仅登录一次）
    login_result = THS_iFinDLogin(IFIND_ACCOUNT, IFIND_KEY)
    if login_result != 0:
        print(f"登录失败，错误码: {login_result}")
        return

    # 4. 循环抓取每一批
    for batch_idx, batch in enumerate(batches, 1):
        batch_codes = ",".join(batch)
        print(f"\n===== 抓取第{batch_idx}/{len(batches)}批 =====")
        try:
            # 调用THS_DS抓取当前批次
            result = THS_DS(batch_codes, indicators, indicator_params, "", start_date, end_date)
            if result.errorcode != 0:
                print(f"第{batch_idx}批抓取失败: {result.errmsg}")
                continue

            # 转换为DataFrame并合并到总数据
            batch_df = pd.DataFrame(result.data)
            all_data = pd.concat([all_data, batch_df], ignore_index=True)
            print(f"第{batch_idx}批抓取成功，新增{len(batch_df)}行数据")

        except Exception as e:
            print(f"第{batch_idx}批执行出错: {str(e)}")
            continue

    # 5. 保存总数据到CSV
    if not all_data.empty:
        # 确保保存目录存在
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        all_data.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")
        print(f"\n✅ 所有批次抓取完成！总数据行数: {len(all_data)}")
        print(f"✅ 数据已保存至: {SAVE_PATH}")
    else:
        print("\n❌ 未抓取到任何有效数据")

    # 6. 登出释放资源
    THS_iFinDLogout()

if __name__ == "__main__":
    main()