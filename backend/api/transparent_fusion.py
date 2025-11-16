"""
透明融合引擎 - 背景並行雙模型推理 + NPU融合
用戶完全無感知，API格式保持原樣，只提升回答質量
針對Snapdragon Elite X平台優化
"""

import asyncio
import time
from typing import Optional, Tuple, Dict, Any
from .ai_client import ai_client
from .local_llm_client import local_llm_client
from .snapdragon_config import snapdragon_config

class TransparentFusionEngine:
    """透明融合引擎 - 用戶無感知的雙模型融合"""
    
    def __init__(self):
        self.npu_client = ai_client          # NPU模型 (AnythingLLM)
        self.cpu_client = local_llm_client   # CPU模型 (Local LLM) 
        self.fusion_enabled = True
        self.stats = {
            'total_requests': 0,
            'dual_success': 0,
            'npu_only': 0,
            'cpu_only': 0,
            'fusion_success': 0,
            'fallback_used': 0,
            'avg_npu_time': 0,
            'avg_cpu_time': 0,
            'avg_fusion_time': 0
        }
        
        # 使用Snapdragon Elite X優化配置
        self.performance_config = snapdragon_config.get_fusion_config()
        self.is_snapdragon = snapdragon_config.is_snapdragon_elite_x
        
        # 日志平台信息
        if self.is_snapdragon:
            print(f"透明融合引擎: Snapdragon Elite X優化已啟用")
            print(f"並行執行模式: {self.performance_config['parallel_execution_mode']}")
            print(f"負載均衡策略: {self.performance_config['load_balancing']}")
        else:
            print("透明融合引擎: 使用通用配置")
        
        # 簡單的LRU緩存
        self.cache = {}
        self.cache_access_order = []
        
    def _get_cache_key(self, question: str, workspace_slug: Optional[str] = None) -> str:
        """生成緩存鍵"""
        return f"{hash(question)}_{workspace_slug or 'default'}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """從緩存獲取結果"""
        if not self.performance_config["enable_caching"]:
            return None
            
        if cache_key in self.cache:
            # 更新訪問順序
            self.cache_access_order.remove(cache_key)
            self.cache_access_order.append(cache_key)
            return self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, result: str):
        """保存到緩存"""
        if not self.performance_config["enable_caching"]:
            return
            
        # LRU淘汰策略
        max_size = self.performance_config["max_cache_size"]
        while len(self.cache) >= max_size and self.cache_access_order:
            oldest_key = self.cache_access_order.pop(0)
            if oldest_key in self.cache:
                del self.cache[oldest_key]
        
        self.cache[cache_key] = result
        self.cache_access_order.append(cache_key)
        
    async def process_request(self, question: str, workspace_slug: Optional[str] = None, 
                            task_type: str = "general") -> str:
        """
        統一使用 NPU 模型處理請求
        """
        self.stats['total_requests'] += 1
        
        # 檢查緩存
        cache_key = self._get_cache_key(question, workspace_slug)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        start_time = time.time()
        
        try:
            # 使用 NPU 模型
            result = await self.npu_client.call_chat_api(question, workspace_slug)
            npu_time = time.time() - start_time
            
            # 更新性能統計
            self.stats['avg_npu_time'] = (self.stats['avg_npu_time'] + npu_time) / 2
            self.stats['npu_only'] += 1
            
            # 緩存結果
            self._save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"NPU 模型錯誤: {e}")
            self.stats['fallback_used'] += 1
            return "抱歉，AI服務暫時不可用，請稍後再試。"
    
    async def _get_dual_answers_with_timing(self, question: str, 
                                          workspace_slug: Optional[str] = None) -> Tuple[str, str, bool, bool, float, float]:
        """並行獲取兩個模型的回答，返回結果、成功狀態和耗時"""
        
        async def get_npu_answer():
            start_time = time.time()
            try:
                answer = await asyncio.wait_for(
                    self.npu_client.call_chat_api(question, workspace_slug),
                    timeout=self.performance_config["max_parallel_timeout"]
                )
                elapsed = time.time() - start_time
                return answer.strip() if answer else "", True, elapsed
            except asyncio.TimeoutError:
                print(f"NPU模型超時 (>{self.performance_config['max_parallel_timeout']}s)")
                return "", False, time.time() - start_time
            except Exception as e:
                print(f"NPU模型錯誤: {e}")
                return "", False, time.time() - start_time
        
        async def get_cpu_answer():
            start_time = time.time()
            try:
                # 確保CPU模型已加載
                if not self.cpu_client.is_model_loaded():
                    print("CPU模型未加載，嘗試自動加載...")
                    await self.cpu_client.load_model()
                
                answer = await asyncio.wait_for(
                    self.cpu_client.generate(self._optimize_prompt_for_cpu(question)),
                    timeout=self.performance_config["max_parallel_timeout"]
                )
                elapsed = time.time() - start_time
                return answer.strip() if answer else "", True, elapsed
            except asyncio.TimeoutError:
                print(f"CPU模型超時 (>{self.performance_config['max_parallel_timeout']}s)")
                return "", False, time.time() - start_time
            except Exception as e:
                print(f"CPU模型錯誤: {e}")
                return "", False, time.time() - start_time
        
        # 並行執行兩個任務
        results = await asyncio.gather(
            get_npu_answer(), 
            get_cpu_answer(), 
            return_exceptions=True
        )
        
        # 處理結果
        if isinstance(results[0], Exception):
            answer_a, success_a, npu_time = "", False, 0.0
        else:
            answer_a, success_a, npu_time = results[0]
            
        if isinstance(results[1], Exception):
            answer_b, success_b, cpu_time = "", False, 0.0
        else:
            answer_b, success_b, cpu_time = results[1]
        
        return answer_a, answer_b, success_a, success_b, npu_time, cpu_time
    
    def _optimize_prompt_for_cpu(self, question: str) -> str:
        """為CPU模型優化提示詞（減少token消耗）"""
        # CPU模型通常較小，使用更簡潔的提示格式
        return f"請簡潔回答：{question}"
    
    async def _perform_npu_fusion(self, question: str, answer_a: str, answer_b: str, 
                                 workspace_slug: Optional[str] = None, 
                                 task_type: str = "general") -> str:
        """使用NPU進行融合推理"""
        
        # 根據任務類型構建融合提示詞
        fusion_prompt = self._build_fusion_prompt(task_type, question, answer_a, answer_b)
        
        try:
            # 使用NPU (AnythingLLM) 進行融合推理
            fused_answer = await asyncio.wait_for(
                self.npu_client.call_chat_api(fusion_prompt, workspace_slug),
                timeout=self.performance_config["fusion_timeout"]
            )
            return fused_answer.strip() if fused_answer else self._select_better_answer(answer_a, answer_b)
            
        except asyncio.TimeoutError:
            print(f"NPU融合推理超時 (>{self.performance_config['fusion_timeout']}s)")
            return self._select_better_answer(answer_a, answer_b)
        except Exception as e:
            print(f"NPU融合推理失敗: {e}")
            # 降級策略：返回質量較好的答案
            return self._select_better_answer(answer_a, answer_b)
    
    def _build_fusion_prompt(self, task_type: str, question: str, answer_a: str, answer_b: str) -> str:
        """根據任務類型構建融合提示詞"""
        
        if task_type == "summary":
            return f"""請基於以下兩個討論摘要，生成一個更完整準確的最終摘要：

摘要需求：{question}

摘要A：{answer_a}

摘要B：{answer_b}

請整合兩個摘要中的所有重要信息，確保涵蓋所有要點，並按邏輯順序組織。直接給出最終摘要："""

        elif task_type == "topic_generation":
            return f"""基於以下兩組討論主題建議，請生成一個更完整多樣的最終主題列表：

需求：{question}

主題建議A：{answer_a}

主題建議B：{answer_b}

請整合兩組建議，去除重複項，確保主題多樣性和完整性，按重要性排序。直接給出最終主題列表："""

        elif task_type == "single_topic":
            return f"""基於以下兩個主題建議，請生成一個更好的最終主題：

主題要求：{question}

建議A：{answer_a}

建議B：{answer_b}

請結合兩個建議的優點，生成一個更精確、有吸引力的主題。直接給出最終主題："""

        else:  # chat 或 general
            return f"""基於以下兩個AI的回答，請生成一個更好的最終回答：

問題：{question}

回答A：{answer_a}

回答B：{answer_b}

請整合兩個回答的優點，提供一個更準確、完整、有幫助的答案。直接給出最終答案："""
    
    def _select_better_answer(self, answer_a: str, answer_b: str) -> str:
        """智能選擇更好的答案（降級策略）"""
        
        if not answer_a and not answer_b:
            return "抱歉，無法生成回答。"
        elif not answer_a:
            return answer_b
        elif not answer_b:
            return answer_a
        
        # 智能質量評估：
        # 1. 長度權重（適中最好）
        # 2. 結構化權重（句號、逗號、換行）
        # 3. 內容豐富度（中文字符比例）
        # 4. 避免過短或過長的回答
        
        def calculate_quality_score(text: str) -> float:
            if not text:
                return 0.0
                
            length = len(text)
            # 長度評分：200-800字符範圍最優
            if length < 50:
                length_score = length / 50 * 0.3
            elif length < 200:
                length_score = 0.3 + (length - 50) / 150 * 0.4
            elif length <= 800:
                length_score = 0.7 + (800 - length) / 600 * 0.3
            else:
                length_score = max(0.5, 1.0 - (length - 800) / 1000 * 0.5)
            
            # 結構化評分
            structure_score = (
                min(text.count('。'), 5) * 0.1 +      # 句子數量
                min(text.count('，'), 8) * 0.05 +     # 細節豐富度
                min(text.count('\n'), 3) * 0.1 +      # 段落結構
                min(text.count('：'), 2) * 0.05       # 列舉結構
            )
            
            # 中文內容比例（相對於總字符數）
            chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
            chinese_ratio = chinese_chars / length if length > 0 else 0
            content_score = chinese_ratio * 0.3
            
            return length_score + structure_score + content_score
        
        score_a = calculate_quality_score(answer_a)
        score_b = calculate_quality_score(answer_b)
        
        # 如果分數差異很小（<10%），選擇較短的（更簡潔）
        if abs(score_a - score_b) / max(score_a, score_b, 0.1) < 0.1:
            return answer_a if len(answer_a) <= len(answer_b) else answer_b
        
        return answer_a if score_a >= score_b else answer_b
    
    def enable_fusion(self):
        """啟用融合模式"""
        self.fusion_enabled = True
    
    def disable_fusion(self):
        """禁用融合模式（回退到單一NPU模型）"""
        self.fusion_enabled = False
    
    def is_fusion_enabled(self) -> bool:
        """檢查融合模式狀態"""
        return self.fusion_enabled
        
    def get_stats(self) -> dict:
        """獲取詳細運行統計"""
        total = max(self.stats['total_requests'], 1)  # 避免除零
        
        return {
            'total_requests': self.stats['total_requests'],
            'success_rates': {
                'dual_model_success': round(self.stats['dual_success'] / total * 100, 1),
                'npu_only_success': round(self.stats['npu_only'] / total * 100, 1),
                'cpu_only_success': round(self.stats['cpu_only'] / total * 100, 1),
                'fusion_success': round(self.stats['fusion_success'] / total * 100, 1),
                'fallback_rate': round(self.stats['fallback_used'] / total * 100, 1)
            },
            'performance_metrics': {
                'avg_npu_time': round(self.stats['avg_npu_time'], 2),
                'avg_cpu_time': round(self.stats['avg_cpu_time'], 2),
                'avg_fusion_time': round(self.stats['avg_fusion_time'], 2),
                'cache_hit_rate': round(len(self.cache) / max(total, 1) * 100, 1),
                'cache_size': len(self.cache)
            },
            'fusion_enabled': self.fusion_enabled,
            'configuration': self.performance_config
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """獲取系統健康狀態"""
        return {
            'fusion_engine': {
                'status': 'healthy' if self.fusion_enabled else 'disabled',
                'fusion_enabled': self.fusion_enabled
            },
            'npu_client': {
                'status': 'connected',  # AnythingLLM連接狀態需要實際檢查
                'client_type': 'AnythingLLM'
            },
            'cpu_client': {
                'status': 'loaded' if self.cpu_client.is_model_loaded() else 'not_loaded',
                'model_info': self.cpu_client.get_model_info()
            },
            'cache': {
                'enabled': self.performance_config['enable_caching'],
                'size': len(self.cache),
                'max_size': self.performance_config['max_cache_size']
            }
        }
    
    def reset_stats(self):
        """重置統計數據"""
        self.stats = {
            'total_requests': 0,
            'dual_success': 0,
            'npu_only': 0,
            'cpu_only': 0,
            'fusion_success': 0,
            'fallback_used': 0,
            'avg_npu_time': 0,
            'avg_cpu_time': 0,
            'avg_fusion_time': 0
        }
        
    def clear_cache(self):
        """清空緩存"""
        self.cache.clear()
        self.cache_access_order.clear()

# 全局透明融合引擎實例
transparent_fusion = TransparentFusionEngine()