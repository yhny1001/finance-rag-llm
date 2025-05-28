#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
向量数据库修复工具
用于诊断和修复RAG引擎的向量数据库问题
"""

import os
import sys
import time
import json
import shutil
from pathlib import Path
import argparse
import logging
from typing import Dict, Any, List, Optional

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("vector_db_fix.log")
    ]
)
logger = logging.getLogger("vector_db_fix")

# 导入配置，确保能找到配置文件
try:
    from config import Config
    config = Config()
    logger.info(f"配置加载成功，文档目录: {config.DOCUMENTS_DIR}")
except ImportError:
    logger.error("无法导入配置，请确保config.py文件存在")
    sys.exit(1)

# 尝试导入RAG引擎
try:
    from rag_engine import RAGEngine
    RAG_ENGINE_AVAILABLE = True
    logger.info("RAG引擎导入成功")
except ImportError:
    logger.error("无法导入RAG引擎，请确保rag_engine.py文件存在")
    RAG_ENGINE_AVAILABLE = False

class VectorDBFixer:
    """向量数据库修复工具类"""
    
    def __init__(self):
        self.config = Config()
        self.rag_engine = None
        self.vector_dir = Path(self.config.VECTOR_DB_PATH).parent if hasattr(self.config, 'VECTOR_DB_PATH') else Path("vector_db")
        self.backup_dir = Path("backups/vector_db")
        
        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 文档目录
        self.doc_dir = Path(self.config.DOCUMENTS_DIR) if hasattr(self.config, 'DOCUMENTS_DIR') else Path("docs")
        
    def initialize_rag_engine(self) -> bool:
        """初始化RAG引擎"""
        if not RAG_ENGINE_AVAILABLE:
            logger.error("RAG引擎不可用，无法初始化")
            return False
            
        try:
            logger.info("初始化RAG引擎...")
            self.rag_engine = RAGEngine(self.config)
            logger.info("RAG引擎初始化成功")
            return True
        except Exception as e:
            logger.error(f"RAG引擎初始化失败: {e}")
            return False
    
    def check_vector_db_files(self) -> Dict[str, Any]:
        """检查向量数据库文件"""
        logger.info(f"检查向量数据库文件: {self.vector_dir}")
        
        results = {
            "vector_dir_exists": False,
            "index_file_exists": False,
            "docstore_file_exists": False,
            "index_file_size": 0,
            "docstore_file_size": 0,
            "status": "未检查",
            "issues": []
        }
        
        # 检查向量数据库目录
        if not self.vector_dir.exists():
            results["issues"].append(f"向量数据库目录不存在: {self.vector_dir}")
            results["status"] = "目录不存在"
            return results
            
        results["vector_dir_exists"] = True
        
        # 检查index.faiss文件
        index_file = self.vector_dir / "index.faiss"
        if index_file.exists():
            results["index_file_exists"] = True
            results["index_file_size"] = index_file.stat().st_size
            
            if results["index_file_size"] < 1000:
                results["issues"].append("索引文件过小，可能损坏或为空")
        else:
            results["issues"].append("索引文件不存在")
        
        # 检查docstore.json文件
        docstore_file = self.vector_dir / "docstore.json"
        if docstore_file.exists():
            results["docstore_file_exists"] = True
            results["docstore_file_size"] = docstore_file.stat().st_size
            
            if results["docstore_file_size"] < 1000:
                results["issues"].append("文档存储文件过小，可能损坏或为空")
                
            # 尝试解析docstore.json
            try:
                with open(docstore_file, 'r', encoding='utf-8') as f:
                    docstore_data = json.load(f)
                    results["doc_count"] = len(docstore_data.get("docstore", {}).get("docs", {}))
                    results["docstore_valid"] = True
            except Exception as e:
                results["issues"].append(f"文档存储文件解析失败: {e}")
                results["docstore_valid"] = False
        else:
            results["issues"].append("文档存储文件不存在")
        
        # 确定整体状态
        if results["index_file_exists"] and results["docstore_file_exists"] and not results["issues"]:
            results["status"] = "正常"
        elif results["index_file_exists"] and results["docstore_file_exists"]:
            results["status"] = "文件存在但可能有问题"
        else:
            results["status"] = "文件缺失"
        
        return results
    
    def check_document_files(self) -> Dict[str, Any]:
        """检查文档文件"""
        logger.info(f"检查文档文件: {self.doc_dir}")
        
        results = {
            "doc_dir_exists": False,
            "doc_count": 0,
            "doc_types": {},
            "status": "未检查",
            "issues": []
        }
        
        # 检查文档目录
        if not self.doc_dir.exists():
            results["issues"].append(f"文档目录不存在: {self.doc_dir}")
            results["status"] = "目录不存在"
            return results
            
        results["doc_dir_exists"] = True
        
        # 检查文档文件
        doc_files = []
        doc_types = {}
        for ext in ['.txt', '.pdf', '.docx', '.md']:
            files = list(self.doc_dir.rglob(f"*{ext}"))
            doc_files.extend(files)
            doc_types[ext] = len(files)
        
        results["doc_count"] = len(doc_files)
        results["doc_types"] = doc_types
        
        if results["doc_count"] == 0:
            results["issues"].append("未找到任何文档文件")
            results["status"] = "无文档"
        else:
            results["status"] = "正常"
            
        return results
    
    def backup_vector_db(self) -> bool:
        """备份向量数据库"""
        logger.info("备份向量数据库...")
        
        if not self.vector_dir.exists():
            logger.error(f"向量数据库目录不存在: {self.vector_dir}")
            return False
            
        backup_name = f"vector_db_backup_{time.strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copytree(self.vector_dir, backup_path)
            logger.info(f"向量数据库已备份到: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"备份向量数据库失败: {e}")
            return False
    
    def clean_vector_db(self) -> bool:
        """清理向量数据库"""
        logger.info("清理向量数据库...")
        
        if not self.vector_dir.exists():
            logger.warning(f"向量数据库目录不存在: {self.vector_dir}")
            return True
            
        # 先备份
        if not self.backup_vector_db():
            logger.warning("未能备份向量数据库，继续清理")
            
        # 删除向量数据库文件
        try:
            for file in self.vector_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    logger.info(f"已删除: {file}")
            
            logger.info("向量数据库清理完成")
            return True
        except Exception as e:
            logger.error(f"清理向量数据库失败: {e}")
            return False
    
    def rebuild_vector_db(self, force: bool = False) -> bool:
        """重建向量数据库"""
        logger.info(f"重建向量数据库 (force={force})...")
        
        # 初始化RAG引擎
        if not self.initialize_rag_engine():
            return False
            
        # 如果强制重建，先清理
        if force and not self.clean_vector_db():
            logger.warning("清理向量数据库失败，尝试直接重建")
            
        # 重建索引
        try:
            result = self.rag_engine.build_index(force_rebuild=force)
            if result:
                logger.info("向量数据库重建成功")
                return True
            else:
                logger.error("向量数据库重建失败")
                return False
        except Exception as e:
            logger.error(f"重建向量数据库时出错: {e}")
            return False
    
    def diagnose_system(self) -> Dict[str, Any]:
        """诊断系统"""
        logger.info("开始系统诊断...")
        
        diagnosis = {
            "vector_db": self.check_vector_db_files(),
            "documents": self.check_document_files(),
            "suggestions": [],
            "rag_engine": {"status": "未检查"}
        }
        
        # 基于问题给出建议
        if not diagnosis["vector_db"]["vector_dir_exists"]:
            diagnosis["suggestions"].append("创建向量数据库目录并重新构建索引")
        elif not diagnosis["vector_db"]["index_file_exists"] or not diagnosis["vector_db"]["docstore_file_exists"]:
            diagnosis["suggestions"].append("向量数据库文件缺失，需要重建索引")
        elif diagnosis["vector_db"]["issues"]:
            diagnosis["suggestions"].append("向量数据库文件可能损坏，建议备份后重建索引")
            
        if not diagnosis["documents"]["doc_dir_exists"]:
            diagnosis["suggestions"].append("创建文档目录并添加文档")
        elif diagnosis["documents"]["doc_count"] == 0:
            diagnosis["suggestions"].append("添加文档到文档目录")
            
        # 初始化RAG引擎并检查
        if self.initialize_rag_engine():
            try:
                rag_diagnosis = self.rag_engine.diagnose_system()
                diagnosis["rag_engine"] = rag_diagnosis
                
                # 添加RAG引擎的建议
                if "suggestions" in rag_diagnosis:
                    diagnosis["suggestions"].extend(rag_diagnosis["suggestions"])
                    
            except Exception as e:
                logger.error(f"RAG引擎诊断失败: {e}")
                diagnosis["rag_engine"] = {"status": f"诊断失败: {e}"}
                diagnosis["suggestions"].append("RAG引擎诊断失败，可能需要检查代码或依赖")
        
        # 检查GPU
        if TORCH_AVAILABLE and torch.cuda.is_available():
            diagnosis["gpu"] = {
                "available": True,
                "device_name": torch.cuda.get_device_name(0),
                "device_count": torch.cuda.device_count(),
                "memory_allocated": f"{torch.cuda.memory_allocated(0)/1024**3:.2f}GB",
                "memory_reserved": f"{torch.cuda.memory_reserved(0)/1024**3:.2f}GB"
            }
        else:
            diagnosis["gpu"] = {"available": False}
            diagnosis["suggestions"].append("未检测到可用GPU，建议使用GPU环境运行")
        
        return diagnosis
    
    def print_diagnosis(self, diagnosis: Dict[str, Any]):
        """打印诊断结果"""
        print("\n" + "="*60)
        print("向量数据库诊断报告")
        print("="*60)
        
        # 向量数据库状态
        print("\n[向量数据库状态]")
        print(f"目录: {self.vector_dir}")
        print(f"状态: {diagnosis['vector_db']['status']}")
        if diagnosis['vector_db']['vector_dir_exists']:
            print(f"索引文件: {'存在' if diagnosis['vector_db']['index_file_exists'] else '不存在'} ({diagnosis['vector_db']['index_file_size']/1024:.1f}KB)")
            print(f"文档存储: {'存在' if diagnosis['vector_db']['docstore_file_exists'] else '不存在'} ({diagnosis['vector_db']['docstore_file_size']/1024:.1f}KB)")
            if "doc_count" in diagnosis['vector_db']:
                print(f"文档数量: {diagnosis['vector_db']['doc_count']}")
                
        # 文档状态
        print("\n[文档状态]")
        print(f"目录: {self.doc_dir}")
        print(f"状态: {diagnosis['documents']['status']}")
        if diagnosis['documents']['doc_dir_exists']:
            print(f"文档数量: {diagnosis['documents']['doc_count']}")
            print("文档类型分布:")
            for ext, count in diagnosis['documents']['doc_types'].items():
                print(f"  {ext}: {count}个")
                
        # RAG引擎状态
        print("\n[RAG引擎状态]")
        if "status" in diagnosis['rag_engine']:
            print(f"状态: {diagnosis['rag_engine']['status']}")
        else:
            print("状态: 未知")
            
        if "embedding_model" in diagnosis['rag_engine']:
            print(f"嵌入模型: {diagnosis['rag_engine']['embedding_model']}")
            
        if "llm" in diagnosis['rag_engine']:
            print(f"大语言模型: {diagnosis['rag_engine']['llm']}")
            
        # GPU状态
        print("\n[GPU状态]")
        if diagnosis['gpu']['available']:
            print(f"GPU: {diagnosis['gpu']['device_name']}")
            print(f"设备数量: {diagnosis['gpu']['device_count']}")
            print(f"已分配内存: {diagnosis['gpu']['memory_allocated']}")
            print(f"已保留内存: {diagnosis['gpu']['memory_reserved']}")
        else:
            print("GPU: 不可用")
            
        # 问题
        all_issues = diagnosis['vector_db']['issues'] + diagnosis['documents']['issues']
        if "issues" in diagnosis['rag_engine']:
            all_issues.extend(diagnosis['rag_engine']['issues'])
            
        if all_issues:
            print("\n[发现的问题]")
            for i, issue in enumerate(all_issues):
                print(f"  {i+1}. {issue}")
        else:
            print("\n✅ 未发现明显问题")
                
        # 建议
        if diagnosis['suggestions']:
            print("\n[建议的解决方案]")
            for i, suggestion in enumerate(diagnosis['suggestions']):
                print(f"  {i+1}. {suggestion}")
        
        print("\n" + "="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="向量数据库修复工具")
    parser.add_argument("--diagnose", action="store_true", help="诊断系统状态")
    parser.add_argument("--backup", action="store_true", help="备份向量数据库")
    parser.add_argument("--clean", action="store_true", help="清理向量数据库")
    parser.add_argument("--rebuild", action="store_true", help="重建向量数据库")
    parser.add_argument("--force", action="store_true", help="强制重建索引")
    parser.add_argument("--all", action="store_true", help="执行所有修复步骤")
    
    args = parser.parse_args()
    
    fixer = VectorDBFixer()
    
    if args.all:
        # 执行所有步骤
        print("执行完整修复流程...")
        
        # 诊断
        diagnosis = fixer.diagnose_system()
        fixer.print_diagnosis(diagnosis)
        
        # 备份
        if fixer.backup_vector_db():
            print("✅ 向量数据库备份成功")
        else:
            print("❌ 向量数据库备份失败")
            
        # 清理
        if fixer.clean_vector_db():
            print("✅ 向量数据库清理成功")
        else:
            print("❌ 向量数据库清理失败")
            
        # 重建
        if fixer.rebuild_vector_db(force=True):
            print("✅ 向量数据库重建成功")
            
            # 最终诊断
            print("\n执行最终诊断...")
            final_diagnosis = fixer.diagnose_system()
            fixer.print_diagnosis(final_diagnosis)
        else:
            print("❌ 向量数据库重建失败")
            
        return
    
    # 单独步骤
    if args.diagnose:
        diagnosis = fixer.diagnose_system()
        fixer.print_diagnosis(diagnosis)
        
    if args.backup:
        if fixer.backup_vector_db():
            print("✅ 向量数据库备份成功")
        else:
            print("❌ 向量数据库备份失败")
            
    if args.clean:
        if fixer.clean_vector_db():
            print("✅ 向量数据库清理成功")
        else:
            print("❌ 向量数据库清理失败")
            
    if args.rebuild:
        if fixer.rebuild_vector_db(force=args.force):
            print("✅ 向量数据库重建成功")
        else:
            print("❌ 向量数据库重建失败")
            
    # 如果没有参数，显示帮助
    if not any([args.diagnose, args.backup, args.clean, args.rebuild, args.all]):
        parser.print_help()
        print("\n示例用法:")
        print("  python fix_vector_db.py --diagnose                # 诊断系统状态")
        print("  python fix_vector_db.py --backup                  # 备份向量数据库")
        print("  python fix_vector_db.py --clean                   # 清理向量数据库")
        print("  python fix_vector_db.py --rebuild                 # 重建向量数据库")
        print("  python fix_vector_db.py --rebuild --force         # 强制重建索引")
        print("  python fix_vector_db.py --all                     # 执行所有修复步骤")


if __name__ == "__main__":
    main() 