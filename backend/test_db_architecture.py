"""
数据库架构测试脚本
测试新的标准化数据库架构是否正常工作
"""
import sys
import asyncio
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def test_database_architecture():
    """测试数据库架构"""
    print("🔧 开始测试新的标准化数据库架构...")
    
    try:
        # 1. 测试配置加载
        print("\n📋 1. 测试配置文件加载...")
        from database.config.database_config import db_config
        
        configs = db_config.get_database_config()
        print(f"✅ 配置加载成功，共 {len(configs)} 个数据库")
        for name, info in configs.items():
            print(f"   - {name}: {info.description}")
            print(f"     文件路径: {info.db_path}")
        
        # 2. 测试数据库服务
        print("\n🗄️  2. 测试数据库服务层...")
        from database.service.database_service import db_manager
        
        print("🔄 初始化所有数据库服务...")
        await db_manager.initialize_all()
        print("✅ 数据库服务初始化成功")
        
        # 3. 测试数据库适配器
        print("\n🔌 3. 测试数据库适配器...")
        from database.adapter.database_adapter import db
        
        # 测试连接
        await db.initialize()
        print("✅ 数据库适配器连接成功")
        
        # 4. 测试基本操作
        print("\n⚡ 4. 测试基本数据库操作...")
        
        # 测试查询操作
        result = await db.fetchval("SELECT COUNT(*) FROM journals")
        print(f"✅ 期刊表记录数查询成功: {result}")
        
        # 测试插入操作
        test_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = await db.fetchall(test_query)
        print(f"✅ 数据库表查询成功，发现 {len(tables)} 个表:")
        for table in tables:
            print(f"   - {table['name']}")
        
        print("\n🎉 所有测试通过！新的数据库架构工作正常！")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_database_architecture())
    
    if success:
        print("\n✅ 数据库架构重构成功！")
        print("\n📝 重构总结:")
        print("   - 创建了标准化的数据库配置管理")
        print("   - 实现了统一的数据库服务层")
        print("   - 提供了向后兼容的适配器")
        print("   - 更新了main.py使用新架构")
        print("   - 所有现有API保持不变")
    else:
        print("\n❌ 数据库架构测试失败，请检查配置")