#!/usr/bin/env python3
"""
简单的RAG配置测试
"""

def test_imports():
    """测试必要的导入"""
    try:
        import faiss
        print("✅ FAISS导入成功")
    except ImportError as e:
        print(f"❌ FAISS导入失败: {e}")
        return False
    
    try:
        from src.config import get_config_manager
        print("✅ 配置管理器导入成功")
    except ImportError as e:
        print(f"❌ 配置管理器导入失败: {e}")
        return False
    
    return True

def test_config():
    """测试RAG配置"""
    try:
        from src.config import get_config_manager
        config_manager = get_config_manager()
        rag_config = config_manager.config.rag
        
        print(f"RAG配置状态:")
        print(f"  enabled: {rag_config.enabled}")
        print(f"  ollama_host: {rag_config.ollama_host}")
        print(f"  embedding_model: {rag_config.embedding_model}")
        print(f"  llm_model: {rag_config.llm_model}")
        
        return rag_config.enabled
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_ollama_client():
    """测试Ollama客户端连接"""
    try:
        from src.config import get_config_manager
        from ollama import Client
        
        config_manager = get_config_manager()
        rag_config = config_manager.config.rag
        
        client = Client(host=rag_config.ollama_host)
        print(f"✅ Ollama客户端创建成功，host: {rag_config.ollama_host}")
        return True
    except Exception as e:
        print(f"❌ Ollama客户端测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== RAG系统测试 ===")
    
    # 测试导入
    if not test_imports():
        print("❌ 导入测试失败，请安装缺失的依赖")
        exit(1)
    
    # 测试配置
    if not test_config():
        print("❌ RAG配置测试失败或RAG未启用")
        exit(1)
    
    # 测试Ollama连接
    if not test_ollama_client():
        print("❌ Ollama连接测试失败")
        exit(1)
    
    print("✅ 所有测试通过！RAG系统配置正确") 