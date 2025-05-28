#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GPU使用率修复工具
用于解决显存占用高但GPU利用率低的问题
"""

import os
import sys
import torch
import logging
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("gpu_fix.log")
    ]
)
logger = logging.getLogger("gpu_fix")

# 导入配置，确保能找到配置文件
try:
    from config import Config
    config = Config()
    logger.info(f"配置加载成功")
    
    # 修改GPU内存比例
    old_fraction = config.GPU_MEMORY_FRACTION
    config.GPU_MEMORY_FRACTION = 0.5
    logger.info(f"已将GPU内存使用比例从{old_fraction}降低到{config.GPU_MEMORY_FRACTION}")
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


def diagnose_gpu_issue():
    """诊断GPU使用问题"""
    logger.info("开始诊断GPU使用问题...")
    
    # 检查GPU是否可用
    if not torch.cuda.is_available():
        logger.error("未检测到可用的CUDA设备，无法使用GPU")
        return {
            "status": "error",
            "message": "未检测到可用的CUDA设备"
        }
    
    # 获取GPU信息
    device_count = torch.cuda.device_count()
    device_info = []
    for i in range(device_count):
        device_name = torch.cuda.get_device_name(i)
        total_mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
        
        # 获取当前内存使用情况
        try:
            allocated = torch.cuda.memory_allocated(i) / (1024**3)
            reserved = torch.cuda.memory_reserved(i) / (1024**3)
            utilization = torch.cuda.utilization(i)
            
            device_info.append({
                "device_id": i,
                "device_name": device_name,
                "total_memory_gb": f"{total_mem:.2f}",
                "allocated_memory_gb": f"{allocated:.2f}",
                "reserved_memory_gb": f"{reserved:.2f}",
                "utilization_percent": f"{utilization}%",
                "status": "normal" if utilization > 5 else "low_usage"
            })
        except Exception as e:
            device_info.append({
                "device_id": i,
                "device_name": device_name,
                "total_memory_gb": f"{total_mem:.2f}",
                "error": str(e)
            })
    
    # 分析环境变量
    env_vars = {
        "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", "未设置"),
        "PYTORCH_CUDA_ALLOC_CONF": os.environ.get("PYTORCH_CUDA_ALLOC_CONF", "未设置"),
        "TOKENIZERS_PARALLELISM": os.environ.get("TOKENIZERS_PARALLELISM", "未设置")
    }
    
    # 返回诊断结果
    return {
        "status": "completed",
        "device_count": device_count,
        "devices": device_info,
        "environment_vars": env_vars,
        "gpu_memory_fraction": config.GPU_MEMORY_FRACTION,
        "model_device": config.MODEL_DEVICE,
        "model_dtype": config.MODEL_DTYPE
    }


def optimize_gpu_settings():
    """优化GPU设置和CPU/GPU资源平衡"""
    logger.info("开始优化资源设置...")
    
    # 设置环境变量以优化资源使用
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"
    os.environ["CUDA_LAUNCH_BLOCKING"] = "0"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    # 启用cublas工作流 - 提高矩阵乘法性能
    torch.backends.cudnn.benchmark = True
    
    # 启用TF32精度（针对Ampere及更高架构）- 提高性能
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    
    # 禁用JIT分析 - 减少开销
    try:
        torch._C._jit_set_profiling_executor(False)
        torch._C._jit_set_profiling_mode(False)
        logger.info("已禁用JIT分析以提高性能")
    except:
        pass
    
    # 设置CPU和GPU协作
    try:
        # 设置OpenMP和MKL线程数 - 平衡CPU使用
        os.environ["OMP_NUM_THREADS"] = "4"
        os.environ["MKL_NUM_THREADS"] = "4"
        logger.info("已设置CPU线程数")
        
        # 设置torch线程数
        torch.set_num_threads(4)
        logger.info("已设置PyTorch线程数")
    except:
        pass
    
    # 清理缓存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.info("已清理GPU缓存")
    
    # 进行简单计算来预热设备
    if torch.cuda.is_available():
        try:
            logger.info("执行GPU预热...")
            # 创建专用CUDA流
            stream = torch.cuda.Stream()
            
            # 使用小张量执行计算操作
            with torch.cuda.stream(stream):
                x = torch.randn(1000, 1000, device="cuda")
                y = torch.randn(1000, 1000, device="cuda")
                
                # 使用混合精度执行计算
                with torch.cuda.amp.autocast(dtype=torch.float16):
                    for _ in range(5):  # 减少迭代次数，避免占用过多资源
                        z = torch.matmul(x, y)
                        z = torch.nn.functional.relu(z)
            
            # 同步CUDA流
            torch.cuda.synchronize()
            # 清理预热变量
            del x, y, z
            torch.cuda.empty_cache()
            
            logger.info("GPU预热完成")
        except Exception as e:
            logger.warning(f"GPU预热失败: {e}")
    
    # 测试CPU计算
    try:
        logger.info("执行CPU预热...")
        # 在CPU上执行计算
        x_cpu = torch.randn(500, 500)
        y_cpu = torch.randn(500, 500)
        z_cpu = torch.matmul(x_cpu, y_cpu)
        del x_cpu, y_cpu, z_cpu
        logger.info("CPU预热完成")
    except Exception as e:
        logger.warning(f"CPU预热失败: {e}")
    
    logger.info("资源优化设置完成")
    return True


def test_model_forward_pass():
    """测试模型前向传播，确保计算在GPU上执行"""
    if not RAG_ENGINE_AVAILABLE:
        logger.error("无法测试模型，RAG引擎不可用")
        return False
    
    logger.info("开始测试模型前向传播...")
    
    try:
        # 初始化RAG引擎
        logger.info("初始化RAG引擎...")
        rag = RAGEngine(config)
        
        # 检查LLM是否已正确加载
        if not rag.llm or (hasattr(rag.llm, 'model') and rag.llm.model is None):
            logger.error("LLM模型未正确加载")
            return False
        
        # 获取预热前的GPU状态
        before_allocated = torch.cuda.memory_allocated() / (1024**3)
        before_utilization = torch.cuda.utilization(0)
        
        # 执行简单生成作为前向传播测试
        logger.info("执行模型前向传播测试...")
        test_prompt = "这是一个测试。请给出简短回复。"
        
        # 记录开始时间
        import time
        start_time = time.time()
        
        # 执行生成
        response = rag.llm.generate(test_prompt, max_length=20)
        
        # 计算耗时
        elapsed = time.time() - start_time
        
        # 获取生成后的GPU状态
        after_allocated = torch.cuda.memory_allocated() / (1024**3)
        after_utilization = torch.cuda.utilization(0)
        
        logger.info(f"模型响应: {response}")
        logger.info(f"生成耗时: {elapsed:.2f}秒")
        logger.info(f"GPU内存变化: {before_allocated:.2f}GB -> {after_allocated:.2f}GB")
        logger.info(f"GPU利用率变化: {before_utilization}% -> {after_utilization}%")
        
        if after_utilization > before_utilization:
            logger.info("✅ GPU利用率提高，模型正在使用GPU计算")
        else:
            logger.warning("⚠️ GPU利用率未提高，模型可能未有效使用GPU")
        
        return True
    
    except Exception as e:
        logger.error(f"测试模型前向传播失败: {e}")
        return False


def apply_gpu_optimizations():
    """应用所有GPU优化"""
    # 步骤1: 诊断当前问题
    diagnosis = diagnose_gpu_issue()
    logger.info(f"诊断结果: {diagnosis['status']}")
    
    for device in diagnosis.get('devices', []):
        logger.info(f"设备 {device['device_id']}: {device['device_name']}")
        if 'utilization_percent' in device:
            logger.info(f"  利用率: {device['utilization_percent']}")
            logger.info(f"  已分配内存: {device['allocated_memory_gb']}GB / {device['total_memory_gb']}GB")
    
    # 步骤2: 优化GPU设置
    logger.info("应用GPU优化设置...")
    optimize_gpu_settings()
    
    # 步骤3: 测试模型
    logger.info("测试模型GPU计算...")
    test_result = test_model_forward_pass()
    
    if test_result:
        logger.info("✅ GPU优化应用成功")
    else:
        logger.warning("⚠️ GPU优化可能未完全应用，请检查日志")
    
    # 返回最终状态
    return {
        "initial_diagnosis": diagnosis,
        "optimization_applied": True,
        "test_result": test_result
    }


def main():
    """主入口点"""
    parser = argparse.ArgumentParser(description="GPU使用率和资源平衡优化工具")
    parser.add_argument("--diagnose", action="store_true", help="仅诊断GPU问题")
    parser.add_argument("--optimize", action="store_true", help="优化资源设置")
    parser.add_argument("--test", action="store_true", help="测试模型计算性能")
    parser.add_argument("--all", action="store_true", help="执行全部步骤")
    parser.add_argument("--cpu-priority", action="store_true", help="优先使用CPU资源")
    parser.add_argument("--gpu-priority", action="store_true", help="优先使用GPU资源")
    parser.add_argument("--balance-mode", choices=["auto", "cpu", "gpu", "mixed"], default="auto", 
                        help="资源平衡模式: auto(自动), cpu(CPU优先), gpu(GPU优先), mixed(混合使用)")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("资源优化工具")
    print("=" * 50)
    
    # 设置优化模式
    if args.cpu_priority:
        print("已设置CPU优先模式")
        os.environ["RESOURCE_PRIORITY"] = "cpu"
    elif args.gpu_priority:
        print("已设置GPU优先模式")
        os.environ["RESOURCE_PRIORITY"] = "gpu"
    elif args.balance_mode != "auto":
        print(f"已设置{args.balance_mode}资源平衡模式")
        os.environ["RESOURCE_PRIORITY"] = args.balance_mode
    else:
        print("使用自动平衡模式")
        os.environ["RESOURCE_PRIORITY"] = "auto"
    
    if args.diagnose or args.all:
        print("\n[1] 诊断资源使用...")
        diagnosis = diagnose_gpu_issue()
        
        print(f"  资源状态: {diagnosis['status']}")
        for device in diagnosis.get('devices', []):
            print(f"  设备 {device['device_id']}: {device['device_name']}")
            if 'utilization_percent' in device:
                print(f"    利用率: {device['utilization_percent']}")
                print(f"    已分配内存: {device['allocated_memory_gb']}GB / {device['total_memory_gb']}GB")
    
    if args.optimize or args.all:
        print("\n[2] 优化资源设置...")
        optimize_gpu_settings()
        print("  ✅ 资源设置已优化")
    
    if args.test or args.all:
        print("\n[3] 测试模型计算性能...")
        test_result = test_model_forward_pass()
        
        if test_result:
            print("  ✅ 模型计算性能测试通过")
        else:
            print("  ⚠️ 模型计算性能测试未通过，请查看日志了解详情")
    
    if not (args.diagnose or args.optimize or args.test or args.all):
        print("未指定操作，应用所有优化...")
        result = apply_gpu_optimizations()
        
        if result["test_result"]:
            print("\n✅ 资源优化应用成功！")
        else:
            print("\n⚠️ 资源优化可能未完全应用，请查看日志获取详细信息")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main() 