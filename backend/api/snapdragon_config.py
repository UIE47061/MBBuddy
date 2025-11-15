"""
Snapdragon Elite X平台優化配置
針對高通Snapdragon Elite X處理器的AI推理優化
"""

import os
import platform
from typing import Dict, Any, Optional
from utility.config import env

class SnapdragonEliteXConfig:
    """Snapdragon Elite X平台配置管理器"""
    
    def __init__(self):
        self.platform_info = self._detect_platform()
        self.is_snapdragon_elite_x = self._is_snapdragon_elite_x()
        
    def _detect_platform(self) -> Dict[str, Any]:
        """檢測平台信息"""
        return {
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "python_version": platform.python_version(),
        }
    
    def _is_snapdragon_elite_x(self) -> bool:
        """檢測是否為Snapdragon Elite X平台"""
        # 在實際部署時，這裡可以通過更精確的檢測方式
        # 目前使用環境變量或ARM64架構作為指示 - 從統一配置讀取
        if env.SNAPDRAGON_ELITE_X:
            return True
        
        machine = platform.machine().lower()
        return "arm64" in machine or "aarch64" in machine
    
    def get_npu_config(self) -> Dict[str, Any]:
        """獲取NPU（AnythingLLM）優化配置"""
        if self.is_snapdragon_elite_x:
            return {
                "max_concurrent_requests": 4,     # Elite X可同時處理多個NPU請求
                "request_timeout": 15.0,          # NPU請求超時（秒）
                "retry_attempts": 2,              # 重試次數
                "connection_pool_size": 8,        # 連接池大小
                "enable_batching": True,          # 啟用批處理
                "batch_size": 2,                  # 批處理大小
                "optimization_level": "high",     # 優化級別
                "enable_caching": True,           # 啟用結果緩存
                "cache_ttl": 300                  # 緩存生存時間（秒）
            }
        else:
            # 通用配置
            return {
                "max_concurrent_requests": 2,
                "request_timeout": 20.0,
                "retry_attempts": 1,
                "connection_pool_size": 4,
                "enable_batching": False,
                "optimization_level": "medium",
                "enable_caching": True,
                "cache_ttl": 300
            }
    
    def get_cpu_llm_config(self) -> Dict[str, Any]:
        """獲取CPU LLM（llama-cpp-python）優化配置"""
        if self.is_snapdragon_elite_x:
            return {
                # Snapdragon Elite X: 12核心 (8 P-cores + 4 E-cores)
                "n_threads": 8,                   # 使用8個性能核心
                "n_threads_batch": 4,             # 批處理使用4個核心
                "n_ctx": 4096,                    # 上下文長度
                "n_batch": 512,                   # 批處理大小
                "n_gpu_layers": 0,                # CPU模式
                "use_mlock": True,                # 鎖定內存
                "use_mmap": True,                 # 內存映射
                "rope_scaling_type": 1,           # RoPE縮放優化
                "rope_freq_base": 10000.0,
                "numa": True,                     # NUMA優化
                "low_vram": False,                # Elite X內存充足
                "f16_kv": True,                   # 使用FP16精度
                "logits_all": False,              # 節省內存
                "vocab_only": False,
                "use_mmap": True,
                "use_mlock": True,
                "embedding": False,
                "n_gqa": 8,                       # 分組查詢注意力
                # 生成參數
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 1024,
                "repeat_penalty": 1.1,
                "repeat_last_n": 64,
                "penalize_nl": True,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "mirostat": 0,
                "tfs_z": 1.0,
                "typical_p": 1.0,
            }
        else:
            # 通用配置（較保守）
            return {
                "n_threads": 4,
                "n_threads_batch": 2,
                "n_ctx": 2048,
                "n_batch": 256,
                "n_gpu_layers": 0,
                "use_mlock": False,
                "use_mmap": True,
                "numa": False,
                "low_vram": True,
                "f16_kv": False,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 512,
                "repeat_penalty": 1.1,
            }
    
    def get_fusion_config(self) -> Dict[str, Any]:
        """獲取融合系統優化配置"""
        if self.is_snapdragon_elite_x:
            return {
                "max_parallel_timeout": 30.0,      # NPU+CPU並行超時
                "fusion_timeout": 30.0,            # NPU融合推理超時
                "enable_async_optimization": True, # 異步優化
                "cpu_fallback_enabled": True,      # CPU降級策略
                "npu_priority": True,              # NPU優先策略
                "quality_threshold": 0.7,          # 回答質量閾值
                "enable_caching": True,            # 啟用緩存
                "max_cache_size": 2000,            # 最大緩存條目
                "cache_compression": True,         # 緩存壓縮
                "parallel_execution_mode": "optimized", # 並行執行模式
                "load_balancing": "intelligent",   # 智能負載均衡
                "memory_optimization": True,       # 內存優化
                "batch_fusion": True,              # 批量融合
                "fusion_algorithm": "weighted_ensemble" # 融合算法
            }
        else:
            return {
                "max_parallel_timeout": 30.0,
                "fusion_timeout": 30.0,
                "enable_async_optimization": False,
                "cpu_fallback_enabled": True,
                "npu_priority": True,
                "quality_threshold": 0.6,
                "enable_caching": True,
                "max_cache_size": 1000,
                "cache_compression": False,
                "parallel_execution_mode": "standard",
                "load_balancing": "round_robin",
                "memory_optimization": False,
                "batch_fusion": False,
                "fusion_algorithm": "simple_average"
            }
    
    def get_model_recommendations(self) -> Dict[str, Any]:
        """獲取針對平台的模型推薦"""
        if self.is_snapdragon_elite_x:
            return {
                "recommended_cpu_models": [
                    {
                        "name": "phi3-mini",
                        "description": "Microsoft Phi-3 Mini，針對Elite X優化",
                        "size": "3.8GB",
                        "performance": "excellent",
                        "recommended": True
                    },
                    {
                        "name": "qwen2-1.5b",
                        "description": "Qwen2 1.5B，超輕量級",
                        "size": "1.5GB",
                        "performance": "good",
                        "recommended": True
                    },
                    {
                        "name": "llama2-7b-chat",
                        "description": "Llama 2 7B Chat，功能完整",
                        "size": "4.1GB",
                        "performance": "very_good",
                        "recommended": False  # 對於CPU推理較重
                    }
                ],
                "optimal_quantization": "Q4_0",      # 最佳量化級別
                "max_model_size": "8GB",             # 最大模型大小
                "concurrent_models": 2               # 同時運行模型數
            }
        else:
            return {
                "recommended_cpu_models": [
                    {
                        "name": "qwen2-1.5b",
                        "description": "輕量級模型，適合普通硬件",
                        "size": "1.5GB",
                        "performance": "good",
                        "recommended": True
                    }
                ],
                "optimal_quantization": "Q4_0",
                "max_model_size": "4GB",
                "concurrent_models": 1
            }
    
    def get_performance_monitoring_config(self) -> Dict[str, Any]:
        """獲取性能監控配置"""
        return {
            "enable_detailed_logging": self.is_snapdragon_elite_x,
            "log_inference_times": True,
            "log_memory_usage": self.is_snapdragon_elite_x,
            "log_cpu_usage": True,
            "log_npu_utilization": self.is_snapdragon_elite_x,
            "performance_alerts": self.is_snapdragon_elite_x,
            "alert_thresholds": {
                "inference_time": 30.0,      # 推理時間警告閾值（秒）
                "memory_usage": 0.85,        # 內存使用警告閾值（85%）
                "cpu_usage": 0.90,           # CPU使用警告閾值（90%）
                "error_rate": 0.05           # 錯誤率警告閾值（5%）
            },
            "metrics_export": {
                "enable": True,
                "format": "prometheus",      # 指標格式
                "endpoint": "/metrics"       # 指標端點
            }
        }
    
    def get_environment_variables(self) -> Dict[str, str]:
        """獲取推薦的環境變量設置"""
        env_vars = {
            "OMP_NUM_THREADS": str(self.get_cpu_llm_config()["n_threads"]),
            "MKL_NUM_THREADS": str(self.get_cpu_llm_config()["n_threads"]),
            "OPENBLAS_NUM_THREADS": str(self.get_cpu_llm_config()["n_threads"]),
            "VECLIB_MAXIMUM_THREADS": str(self.get_cpu_llm_config()["n_threads"]),
            "NUMEXPR_NUM_THREADS": str(self.get_cpu_llm_config()["n_threads"]),
        }
        
        if self.is_snapdragon_elite_x:
            env_vars.update({
                "SNAPDRAGON_ELITE_X": "true",
                "LLAMA_CPP_ARM_NEON": "1",        # 啟用ARM NEON優化
                "GGML_USE_ACCELERATE": "1",       # 使用Accelerate框架
                "PYTORCH_ENABLE_MPS_FALLBACK": "1", # MPS降級支持
            })
        
        return env_vars
    
    def apply_optimizations(self):
        """應用平台優化設置"""
        env_vars = self.get_environment_variables()
        for key, value in env_vars.items():
            if key not in os.environ:  # 只設置尚未設置的變量
                os.environ[key] = value
    
    def get_deployment_recommendations(self) -> Dict[str, Any]:
        """獲取部署建議"""
        if self.is_snapdragon_elite_x:
            return {
                "docker": {
                    "base_image": "ubuntu:22.04",    # 推薦基礎鏡像
                    "python_version": "3.11",       # Python版本
                    "memory_limit": "16GB",         # 內存限制
                    "cpu_limit": "8.0",             # CPU限制
                    "optimization_flags": [
                        "--security-opt=apparmor:unconfined",
                        "--cap-add=SYS_NICE",        # 允許調整進程優先級
                        "--ulimit=memlock=-1:-1"     # 解除內存鎖定限制
                    ]
                },
                "system": {
                    "swap_optimization": True,       # 交換分區優化
                    "huge_pages": True,             # 大頁面支持
                    "cpu_governor": "performance",   # CPU調度策略
                    "thermal_management": True       # 熱管理
                }
            }
        else:
            return {
                "docker": {
                    "base_image": "python:3.11-slim",
                    "memory_limit": "8GB",
                    "cpu_limit": "4.0"
                },
                "system": {
                    "swap_optimization": False,
                    "huge_pages": False,
                    "cpu_governor": "powersave"
                }
            }

# 全局配置實例
snapdragon_config = SnapdragonEliteXConfig()

# 自動應用優化
snapdragon_config.apply_optimizations()