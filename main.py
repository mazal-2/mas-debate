import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.debate_mas.loader.dossier import Dossier
from src.debate_mas.loader.data_loader import DataLoader
import pandas as pd


def demonstrate_dossier():
    """演示Dossier类的使用"""
    print("=== 对抗性选股系统 - Dossier载体演示 ===\n")

    # 1. 创建dossier
    print("1. 创建Dossier...")
    dossier = DataLoader.create_sample_dossier(
        mission="构建科技股投资组合，目标年化回报15%"
    )
    print(f"   任务: {dossier.mission}")
    print(f"   股票池: {dossier.stock_pool}")
    print(f"   数据源: {dossier.data_sources}")
    print()

    # 2. 展示数据摘要
    print("2. Dossier数据摘要...")
    summary = dossier.to_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    print()

    # 3. 搜索功能演示
    print("3. 搜索功能演示...")
    search_results = dossier.search_documents("earnings", limit=3)
    print(f"   搜索 'earnings' 找到 {len(search_results)} 个文档:")
    for doc in search_results:
        print(f"   - {doc.title} ({doc.content_type})")
    print()

    # 4. 股票数据检索演示
    print("4. 股票数据检索演示...")
    for symbol in ["AAPL", "TSLA"][:2]:  # 演示两个股票
        stock_docs = dossier.get_stock_documents(symbol)
        print(f"   {symbol} 相关文档: {len(stock_docs)} 个")
        for doc in stock_docs[:2]:  # 每个股票显示最多2个文档
            print(f"     - {doc.title}")
    print()

    # 5. 添加新数据演示
    print("5. 添加新数据演示...")
    # 添加新的数值数据
    new_data = pd.DataFrame({
        "AAPL": [180.5, 182.3, 181.7],
        "MSFT": [420.1, 422.5, 419.8]
    }, index=["2024-12-27", "2024-12-30", "2024-12-31"])

    doc_id = dossier.add_numerical_document(
        title="最新股价数据",
        data=new_data,
        metadata={"period": "2024年底", "source": "manual_update"}
    )
    print(f"   添加了新文档: {doc_id}")
    print()

    # 6. 检索添加的数据
    print("6. 检索新添加的数据...")
    new_doc = dossier.get_document(doc_id)
    if new_doc:
        print(f"   文档标题: {new_doc.title}")
        print(f"   内容类型: {new_doc.content_type}")
        print(f"   元数据: {new_doc.metadata}")

        # 转换为DataFrame查看
        df = dossier.get_numerical_data_as_dataframe(doc_id)
        if df is not None:
            print(f"   数据预览:")
            print(df.head())
    print()

    print("=== 演示完成 ===")
    print("\nDossier已准备好作为Agent辩论的数据载体。")
    print("在LangGraph工作流中，各个Agent可以:")
    print("1. 通过dossier.search_documents()查找相关论据")
    print("2. 通过dossier.get_stock_documents()获取特定股票数据")
    print("3. 通过dossier.add_*_document()添加新的证据")
    print("4. 通过dossier.get_document()引用具体数据源")


def main():
    demonstrate_dossier()


if __name__ == "__main__":
    main()
