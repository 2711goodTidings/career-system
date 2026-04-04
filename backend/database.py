from sqlalchemy import create_engine

# 核心修正：HOST改localhost + PORT改数字 + 密码和你重置的完全一致
USERNAME = "root"
PASSWORD = "123456Aa!"  # 注意：和你重置的密码完全一致（包括空格）
HOST = "localhost"        # 匹配 root@localhost，不要用127.0.0.1
PORT = 3306               # 必须是数字，不是字符串
DATABASE = "career_planner"

# 修正URL拼接（避免格式错误）
DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# 创建引擎（添加连接参数，解决兼容问题）
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 检查连接有效性
    connect_args={"charset": "utf8mb4"}  # 字符集兼容
)

def test_connection():
    try:
        with engine.connect() as conn:
            print("MySQL connected successfully!")
    except Exception as e:
        print("MySQL connection failed:", e)

# 执行测试
if __name__ == "__main__":
    test_connection()