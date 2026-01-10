#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置系统测试文件
演示优化后的配置访问方法
"""

from core.config import config

def test_config_access():
    """测试配置访问方法"""
    print("=== 配置系统测试 ===\n")
    
    # 1. 显示所有可用配置键
    print("1. 所有可用配置键:")
    config_info = config.get_config_info()
    print(f"配置文件: {config_info['config_files']}")
    print(f"总配置键数: {config_info['total_keys']}")
    print(f"前10个配置键: {list(config_info['available_keys'])[:10]}")
    print()
    
    # 2. 测试字典访问
    print("2. 字典访问测试:")
    try:
        env = config['global.global.env']
        print(f"config['global.global.env'] = {env}")
    except KeyError as e:
        print(f"错误: {e}")
    print()
    
    # 3. 测试get方法
    print("3. get方法测试:")
    env = config.get('global.global.env')
    port = config.get('global.global.PORT', 8000)
    missing = config.get('global.global.missing_key', '默认值')
    print(f"config.get('global.global.env') = {env}")
    print(f"config.get('global.global.PORT', 8000) = {port}")
    print(f"config.get('global.global.missing_key', '默认值') = {missing}")
    print()
    
    # 4. 测试配置信息查询
    print("4. 配置信息查询:")
    env_info = config.get_config_info('global.global.env')
    print(f"global.global.env 信息: {env_info}")
    print()
    
    # 5. 测试错误处理和智能提示
    print("5. 错误处理和智能提示:")
    try:
        wrong_key = config['global.global.wrong_key']
    except KeyError as e:
        print(f"错误信息: {e}")
        
    # 获取错误提示和建议
    error_info = config.get_config_info('global.global.wrong_key')
    print(f"错误建议: {error_info}")
    print()
    
    # 6. 性能对比演示
    print("6. 性能测试:")
    import time
    
    # 测试多次访问同一个配置键
    test_key = 'global.global.env'
    iterations = 1000
    
    start_time = time.time()
    for _ in range(iterations):
        _ = config[test_key]
    end_time = time.time()
    
    print(f"访问 '{test_key}' {iterations} 次耗时: {(end_time - start_time)*1000:.2f}ms")
    print()

    print("所有键值对格式化输出:")
    for key, value in config.items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    test_config_access()