from langchain.tools import tool

"""
data_path = C:\Users\mazal\vs_projects\debate-mas\data\stock_data\semiconductor_data.csv


设计三种不同的量化策略,里面能够读取到本地stockhunter抓回来后存在本地csv的数据
三个策略能够按照其各自的量化指标或者信号，挑选出该策略下表现最积极的股票以及相关股票价格数据，返回给agent并存以 date_hunter_strategy.csv的格式输出到某个文件夹内

def strategy_1():

def strategy_2():

def strategy_3()

设计完三个策略后，建立一个tool：

@tool
def pick_stock_by_strategy(strategy:str,limit:int = 5):
    '''
    按照这个策略名称参数 if 出以上三种不同的策略，进行结果筛选
    '''


"""
