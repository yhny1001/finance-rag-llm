#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GPU配置和内存管理模块
用于解决内存不足和优化GPU使用效率
"""

import os
import torch
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gpu_config")

class GPUConfig:
    """GPU配置类，用于优化GPU内存使用"""
    
    # 基本GPU配置
    USE_GPU = True
    
    # 智能资源分配 - 不再强制GPU
    FORCE_GPU_COMPUTE = False   # 不强制使用GPU计算
    DEVICE_MAP = "auto"        # 自动设备映射
    OPTIMIZE_COMPUTE = True    # 优化计算性能
    STREAMING_GENERATION = True # 使用流式生成加速
    BALANCE_CPU_GPU = True     # 平衡CPU和GPU使用
    CPU_OFFLOAD = True         # 启用CPU卸载
    
    # 批处理和并行配置
    MAX_BATCH_SIZE = 1        # 最大批处理大小
    GRADIENT_ACCUMULATION_STEPS = 1  # 梯度累积步数
    
    # 优化配置
    USE_FP16 = True           # 使用FP16
    USE_8BIT = True           # 使用8位量化
    USE_4BIT = False          # 不使用4位量化
    
    # 高级优化
    MEMORY_EFFICIENT_ATTENTION = True  # 使用内存高效注意力
    FUSED_OPTIMIZERS = True            # 使用融合优化器
    FLASH_ATTENTION = True             # 使用Flash Attention
    
    @classmethod
    def optimize_gpu_memory(cls):
        """配置GPU内存管理设置"""
        if not torch.cuda.is_available():
            logger.info("GPU不可用，跳过内存优化")
            return False
        
        try:
            logger.info("开始优化GPU和CPU内存设置...")
            
            # 清理缓存
            torch.cuda.empty_cache()
            
            # 配置自动设备分配
            if not cls.FORCE_GPU_COMPUTE:
                # 设置环境变量以支持自动设备映射
                os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"
                
                # 启用CPU和GPU协作
                if cls.BALANCE_CPU_GPU:
                    # 不设置主设备，让PyTorch自动平衡
                    os.environ["CUDA_VISIBLE_DEVICES"] = ""  # 清除可能的设备限制
                    
                    # 启用并行处理
                    os.environ["OMP_NUM_THREADS"] = "4"  # 设置OpenMP线程数
                    os.environ["MKL_NUM_THREADS"] = "4"  # 设置MKL线程数
                    
                    # 禁用tokenizer并行以避免竞争
                    os.environ["TOKENIZERS_PARALLELISM"] = "false"
                    
                    logger.info("已启用CPU和GPU资源平衡模式")
            
            # 设置线程数 - 避免过多线程
            torch.set_num_threads(4)
            
            # 启用cublas工作流 - 提高矩阵乘法性能
            torch.backends.cudnn.benchmark = True
            
            # 启用TF32精度（针对Ampere及更高架构）- 提高性能
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # 启用Flash Attention和其他优化
            if cls.OPTIMIZE_COMPUTE:
                # 设置为确定性模式以优化性能
                torch.backends.cudnn.deterministic = False
                # 使用自动选择算法
                torch.backends.cudnn.enabled = True
                # 启用融合操作
                try:
                    torch._C._jit_override_can_fuse_on_cpu(True)  # 启用CPU融合
                    torch._C._jit_override_can_fuse_on_gpu(True)  # 启用GPU融合
                    torch._C._jit_set_texpr_fuser_enabled(True)
                    torch._C._jit_set_nvfuser_enabled(True)
                except:
                    logger.warning("无法启用融合操作优化")
                
                logger.info("已启用计算优化")
            
            # 设置小内存预分配用于预热 - 避免大内存分配
            try:
                # 分配小内存进行预热
                small_tensor = torch.zeros(1024 * 1024, device="cuda")
                # 执行一些计算操作以预热GPU
                _ = small_tensor + small_tensor
                _ = small_tensor * small_tensor
                _ = torch.matmul(small_tensor.view(1024, 1024), small_tensor.view(1024, 1024))
                del small_tensor
                torch.cuda.empty_cache()
                logger.info("GPU计算单元预热完成")
            except Exception as e:
                logger.warning(f"GPU预热失败: {e}")
            
            # 显示GPU信息
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                logger.info(f"可用GPU数量: {device_count}")
                
                for i in range(device_count):
                    device_name = torch.cuda.get_device_name(i)
                    total_mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                    logger.info(f"GPU {i}: {device_name}, 内存: {total_mem:.2f} GB")
                
                # 输出当前设备
                logger.info(f"当前活跃GPU设备: {torch.cuda.current_device()}")
                logger.info(f"当前GPU使用率: {torch.cuda.utilization(0)}%")
            
            # 输出CPU信息
            try:
                import psutil
                cpu_percent = psutil.cpu_percent()
                cpu_count = psutil.cpu_count()
                memory = psutil.virtual_memory()
                logger.info(f"CPU核心数: {cpu_count}, 使用率: {cpu_percent}%")
                logger.info(f"系统内存: 总计 {memory.total/(1024**3):.2f}GB, 可用 {memory.available/(1024**3):.2f}GB")
            except:
                logger.warning("无法获取CPU信息")
            
            logger.info("资源优化设置完成")
            return True
            
        except Exception as e:
            logger.error(f"设置资源优化失败: {e}")
            return False
    
    @classmethod
    def get_model_kwargs(cls):
        """获取模型加载参数"""
        model_kwargs = {
            "device_map": "auto",
            "torch_dtype": torch.float16 if cls.USE_FP16 else torch.float32,
        }
        
        # 添加量化设置
        if cls.USE_8BIT:
            model_kwargs["load_in_8bit"] = True
        elif cls.USE_4BIT:
            model_kwargs["load_in_4bit"] = True
            model_kwargs["bnb_4bit_quant_type"] = "nf4"
            model_kwargs["bnb_4bit_compute_dtype"] = torch.float16
        
        # 添加内存优化设置
        if cls.MEMORY_EFFICIENT_ATTENTION:
            model_kwargs["attn_implementation"] = "flash_attention_2" if cls.FLASH_ATTENTION else "sdpa"
        
        return model_kwargs
    
    @classmethod
    def monitor_gpu_usage(cls):
        """监控GPU使用情况"""
        if not torch.cuda.is_available():
            return "GPU不可用"
        
        try:
            device = torch.cuda.current_device()
            allocated = torch.cuda.memory_allocated(device) / (1024**3)
            reserved = torch.cuda.memory_reserved(device) / (1024**3)
            max_allocated = torch.cuda.max_memory_allocated(device) / (1024**3)
            
            return {
                "device": torch.cuda.get_device_name(device),
                "allocated_gb": f"{allocated:.2f}",
                "reserved_gb": f"{reserved:.2f}",
                "max_allocated_gb": f"{max_allocated:.2f}",
                "utilization": f"{torch.cuda.utilization(device)}%"
            }
        except:
            return "无法获取GPU使用情况"
    
    @classmethod
    def cleanup_gpu_memory(cls):
        """清理GPU内存"""
        if torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                
                # 尝试主动触发垃圾回收
                import gc
                gc.collect()
                
                logger.info("GPU内存清理完成")
                return True
            except Exception as e:
                logger.error(f"GPU内存清理失败: {e}")
                return False
        return False


def optimize_for_inference():
    """为推理优化GPU设置"""
    GPUConfig.USE_GPU = torch.cuda.is_available()
    GPUConfig.MAX_BATCH_SIZE = 1         # 单样本推理
    GPUConfig.MEMORY_EFFICIENT_ATTENTION = True
    return GPUConfig.optimize_gpu_memory()


def optimize_for_batch_processing():
    """为批处理优化GPU设置"""
    GPUConfig.USE_GPU = torch.cuda.is_available()
    GPUConfig.MAX_BATCH_SIZE = 4         # 增加批处理大小
    return GPUConfig.optimize_gpu_memory()


def balance_model_resources(model, tokenizer=None):
    """平衡模型在CPU和GPU间的资源分配
    
    Args:
        model: 需要优化的模型
        tokenizer: 可选，模型对应的tokenizer
        
    Returns:
        model: 配置后的模型
    """
    logger.info("正在优化模型资源分配...")
    
    if not torch.cuda.is_available():
        logger.warning("GPU不可用，将仅使用CPU")
        return model
    
    try:
        # 1. 检查并优化设备映射
        if hasattr(model, "hf_device_map") and model.hf_device_map:
            logger.info(f"当前设备映射: {model.hf_device_map}")
            # 保留自动映射，不做修改
        else:
            # 如果没有设备映射，设置为auto以利用所有资源
            if hasattr(model, "device"):
                logger.info(f"当前设备: {model.device}")
        
        # 2. 设置eval模式以提高推理性能
        model = model.eval()
        
        # 3. 禁用梯度计算以减少内存使用并提高速度
        for param in model.parameters():
            param.requires_grad = False
        
        # 4. 应用优化
        # 优化缓存机制
        if hasattr(model.config, "use_cache"):
            model.config.use_cache = True
            logger.info("已启用KV缓存以提高性能")
        
        # 5. 如果有tokenizer，也进行配置
        if tokenizer is not None:
            # 将tokenizer的pad_token_id设置与模型一致
            if hasattr(model.config, "pad_token_id") and model.config.pad_token_id is not None:
                tokenizer.pad_token_id = model.config.pad_token_id
            
            # 设置tokenizer合理的并行度
            if hasattr(tokenizer, "model_max_length"):
                # 增加最大长度以处理更长的输入
                tokenizer.model_max_length = min(4096, getattr(tokenizer, "model_max_length", 2048))
            
            logger.info("Tokenizer已配置")
        
        # 6. 执行一次前向传播以预热，使用混合精度
        try:
            if hasattr(model, "get_input_embeddings"):
                vocab_size = model.get_input_embeddings().weight.shape[0]
                
                # 获取当前设备
                device = next(model.parameters()).device
                logger.info(f"模型主要位于设备: {device}")
                
                # 在相同设备上创建小输入张量进行预热
                warmup_ids = torch.randint(0, vocab_size, (1, 10), device=device)
                warmup_mask = torch.ones_like(warmup_ids)
                
                # 不追踪梯度的前向传播，使用混合精度
                with torch.no_grad():
                    with torch.cuda.amp.autocast(enabled=str(device).startswith("cuda")):
                        logger.info("执行混合精度前向传播预热...")
                        outputs = model(warmup_ids, attention_mask=warmup_mask)
                        logger.info(f"前向传播预热完成，输出形状: {outputs.logits.shape}")
                
                # 清理缓存
                if str(device).startswith("cuda"):
                    torch.cuda.empty_cache()
        except Exception as e:
            logger.warning(f"模型预热失败，但不影响使用: {e}")
        
        # 7. 监测资源使用情况
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            logger.info(f"CPU使用率: {cpu_percent}%")
            logger.info(f"内存使用率: {memory_percent}%")
            
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / (1024**3)
                max_allocated = torch.cuda.max_memory_allocated() / (1024**3)
                logger.info(f"GPU内存: 当前分配 {allocated:.2f}GB, 峰值 {max_allocated:.2f}GB")
        except:
            pass
        
        logger.info("模型资源分配优化完成")
        return model
    
    except Exception as e:
        logger.error(f"优化模型资源分配失败: {e}")
        return model


def apply_generation_speedup(model):
    """应用生成加速优化，平衡CPU和GPU资源
    
    Args:
        model: 需要优化的模型
        
    Returns:
        model: 优化后的模型
    """
    if not torch.cuda.is_available() and not hasattr(model, "config"):
        return model
    
    try:
        logger.info("应用模型生成加速和资源平衡...")
        
        # 1. 启用缓存
        if hasattr(model.config, "use_cache"):
            model.config.use_cache = True
            logger.info("已启用KV缓存加速")
        
        # 2. 启用高效注意力机制 (如果可用)
        if hasattr(model.config, "attn_implementation"):
            try:
                # 检查是否在CUDA设备上
                on_gpu = next(model.parameters()).device.type == "cuda"
                
                if on_gpu:
                    # 在GPU上尝试使用Flash Attention
                    try:
                        model.config.attn_implementation = "flash_attention_2"
                        logger.info("已启用Flash Attention 2")
                    except:
                        try:
                            model.config.attn_implementation = "sdpa"
                            logger.info("已启用SDPA注意力机制")
                        except:
                            logger.warning("无法设置优化的注意力实现")
                else:
                    # 在CPU上优化注意力
                    logger.info("模型在CPU上运行，优化普通注意力机制")
            except:
                logger.warning("无法确定模型设备或设置注意力机制")
        
        # 3. 优化生成配置
        if hasattr(model, "generation_config"):
            # 保存原始配置
            original_config = {}
            if hasattr(model.generation_config, "do_sample"):
                original_config["do_sample"] = model.generation_config.do_sample
            
            # 根据设备优化生成设置
            try:
                device_type = next(model.parameters()).device.type
                
                if device_type == "cuda":
                    # GPU优化配置
                    logger.info("应用GPU优化的生成配置")
                    model.generation_config.do_sample = False  # 确定性生成更快
                    model.generation_config.num_beam_groups = 1
                    model.generation_config.diversity_penalty = 0.0
                else:
                    # CPU优化配置
                    logger.info("应用CPU优化的生成配置")
                    model.generation_config.do_sample = False
                    model.generation_config.num_beams = 1  # 减少beam search计算量
                    # 设置较小的生成长度
                    if hasattr(model.generation_config, "max_new_tokens"):
                        model.generation_config.max_new_tokens = min(
                            model.generation_config.max_new_tokens, 
                            1024
                        )
            except:
                logger.warning("无法获取模型设备类型，使用通用优化")
                # 通用优化设置
                model.generation_config.do_sample = False
        
        logger.info("模型生成加速和资源平衡优化完成")
        return model
    
    except Exception as e:
        logger.error(f"应用生成加速和资源平衡失败: {e}")
        return model


if __name__ == "__main__":
    print("GPU内存优化配置工具")
    
    if torch.cuda.is_available():
        print(f"检测到GPU: {torch.cuda.get_device_name(0)}")
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"GPU总内存: {total_memory:.2f} GB")
        
        success = optimize_for_inference()
        if success:
            print("已应用推理优化设置")
            
            # 显示当前使用情况
            usage = GPUConfig.monitor_gpu_usage()
            print(f"当前GPU使用情况: {usage}")
    else:
        print("未检测到可用GPU") 