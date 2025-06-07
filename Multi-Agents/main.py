# main_optimized.py - 优化版主执行脚本
"""优化的CircuitMind-Lite主执行脚本"""

import os
import sys
import logging
import glob
import asyncio
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional
import argparse
import time

# 导入优化后的模块
from mediator import Mediator
from agents.user_proxy import UserProxy
from agents.coder_agent import CoderAgent
from agents.reviewer import Reviewer
from agents.executor import Executor
from agents.summarizer import Summarizer
from utils.logger import setup_logger, reset_logging_system
from utils.RAG import RAGSystem
from utils.metrics import get_metrics_collector, track_experiment
from utils.retry_strategy import get_retry_strategy
from utils.llm_client_pool import get_llm_client_pool

# 导入配置系统
from src.config import get_config_manager, ConfigValidationError
from src.core.exceptions import CircuitMindError, ConfigurationError, handle_errors

class ExperimentRunner:
    """优化的实验运行器"""
    
    def __init__(self, config_manager, max_workers: int = 4):
        self.config_manager = config_manager
        self.max_workers = max_workers
        self.metrics = get_metrics_collector()
        self.retry_strategy = get_retry_strategy()
        self.client_pool = get_llm_client_pool()
        self.logger = setup_logger("ExperimentRunner")
        self.shutdown_requested = False
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """处理关闭信号"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    @handle_errors(default_return=None)
    def setup_environment(self, experiment_path: str) -> Optional[Dict[str, Any]]:
        """设置实验环境"""
        # 重置日志系统
        reset_logging_system()
        
        experiment_name = os.path.basename(experiment_path)
        config = self.config_manager.config
        
        # 检查跳过条件
        experiment_output_root = config.experiments.get_output_dir(config.current_model)
        
        counter = 1
        while True:
            experiment_output_dir = os.path.join(experiment_output_root, f"{experiment_name}_{counter}")
            if not os.path.exists(experiment_output_dir):
                break
            counter += 1
            if counter > 11:
                self.logger.warning(f"Skipping experiment {experiment_name} (too many runs)")
                return None
        
        # 创建输出目录
        os.makedirs(experiment_output_dir, exist_ok=True)
        
        # 设置日志
        log_filename = os.path.join(experiment_output_dir, "experiment.log")
        setup_logger(name='root', log_file=log_filename)
        
        self.logger.info(f"Experiment folder: {experiment_output_dir}")
        
        # 创建Verilog目录
        verilog_path = os.path.join(experiment_output_dir, "verilog_projects")
        os.makedirs(verilog_path, exist_ok=True)
        
        # 查找必需文件
        testbench_files = glob.glob(os.path.join(experiment_path, "testbench.v"))
        reference_files = glob.glob(os.path.join(experiment_path, "*_ref.v"))
        
        if not testbench_files or not reference_files:
            raise ConfigurationError(
                f"Missing required files in {experiment_path}",
                context={"testbench_found": bool(testbench_files), "reference_found": bool(reference_files)}
            )
        
        return {
            "experiment_name": experiment_name,
            "experiment_path": experiment_path,
            "output_dir": experiment_output_dir,
            "verilog_dir": verilog_path,
            "testbench_path": testbench_files[0],
            "reference_path": reference_files[0],
            "summary_file": os.path.join(experiment_output_dir, "summary.txt")
        }
    
    @handle_errors()
    def initialize_rag_system(self) -> Optional[RAGSystem]:
        """初始化RAG系统"""
        config = self.config_manager.config
        rag_config = config.rag
        
        if not rag_config.enabled:
            self.logger.info("RAG system disabled")
            return None
        
        try:
            # 准备文件列表
            knowledge_base_path = Path(rag_config.knowledge_base_path)
            file_list = [str(f) for f in knowledge_base_path.iterdir() if f.is_file()] if knowledge_base_path.exists() else []
            
            # 详细文件列表
            detail_kb_path = Path(rag_config.detail_knowledge_base_path)
            detailed_file_list = {
                "error_patterns": str(detail_kb_path / "error_patterns.json")
            }
            
            # 模型数据路径
            model_datapath = f"./knowledge_base/Model-incrementment/{config.current_model}.json"
            
            rag_system = RAGSystem(
                file_list,
                detailed_file_list,
                rag_config.embedding_model,
                rag_config.llm_model,
                rag_config.index_path,
                rag_config.data_path,
                model_datapath
            )
            
            self.logger.info("RAG system initialized successfully")
            return rag_system
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG system: {e}")
            return None
    
    @track_experiment()
    def process_single_experiment(self, experiment_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个实验"""
        experiment_name = experiment_info["experiment_name"]
        experiment_path = experiment_info["experiment_path"]
        
        self.logger.info(f"Starting experiment: {experiment_name}")
        
        if self.shutdown_requested:
            raise KeyboardInterrupt("Shutdown requested")
        
        try:
            # 开始指标跟踪
            self.metrics.start_experiment(experiment_name)
            
            # 更新配置
            config = self.config_manager.config
            config.experiments.verilog_dir = experiment_info["verilog_dir"]
            config.experiments.testbench_path = experiment_info["testbench_path"]
            config.experiments.reference_code_path = experiment_info["reference_path"]
            config.experiments.summary_file = experiment_info["summary_file"]
            
            # 初始化RAG
            rag_tool = self.initialize_rag_system()
            
            # 创建智能体
            agents = self.create_agents(config, rag_tool)
            
            # 验证API密钥
            model_config = self.config_manager.get_model_config()
            if not model_config.api_key:
                raise ConfigurationError("API key not found")
            
            self.logger.info("Successfully loaded API key")
            
            # 查找设计需求文件
            design_request_files = glob.glob(os.path.join(experiment_path, "*_Prompt.txt"))
            if not design_request_files:
                raise ConfigurationError(f"Design request file not found in {experiment_path}")
            
            # 读取设计需求
            with open(design_request_files[0], "r", encoding="utf-8") as f:
                design_requirements = f.read().strip()
            
            # 提交设计请求
            agents["user_proxy"].submit_design_request(design_requirements)
            
            # 等待实验完成（这里可以实现更复杂的协调逻辑）
            time.sleep(1)  # 简单等待，实际应该基于智能体状态
            
            result = {
                "experiment_name": experiment_name,
                "success": True,
                "output_dir": experiment_info["output_dir"]
            }
            
            self.metrics.finish_experiment(experiment_name, success=True)
            return result
            
        except Exception as e:
            self.logger.error(f"Experiment {experiment_name} failed: {str(e)}")
            self.metrics.record_error(experiment_name, type(e).__name__, str(e))
            self.metrics.finish_experiment(experiment_name, success=False, error_message=str(e))
            
            return {
                "experiment_name": experiment_name,
                "success": False,
                "error": str(e),
                "output_dir": experiment_info.get("output_dir")
            }
    
    def create_agents(self, config, rag_tool) -> Dict[str, Any]:
        """创建智能体"""
        # 使用依赖注入模式创建智能体
        mediator = Mediator()
        
        agents = {
            "user_proxy": UserProxy("UserProxy", mediator, config),
            "coder_agent": CoderAgent("CoderAgent", mediator, config, rag_tool),
            "reviewer": Reviewer("Reviewer", mediator, config, rag_tool),
            "executor": Executor("Executor", mediator, config),
            "summarizer": Summarizer("Summarizer", mediator, config)
        }
        
        # 注册智能体到指标系统
        for name, agent in agents.items():
            self.metrics.record_agent_activity(name, "initialized", role=getattr(agent, 'role', 'unknown'))
        
        return agents
    
    async def run_experiments_parallel(self, experiments: List[str]) -> List[Dict[str, Any]]:
        """并行运行实验"""
        self.logger.info(f"Starting {len(experiments)} experiments with {self.max_workers} workers")
        
        # 设置实验环境
        experiment_infos = []
        for exp_path in experiments:
            if self.shutdown_requested:
                break
            
            env_info = self.setup_environment(exp_path)
            if env_info:
                experiment_infos.append(env_info)
        
        if self.shutdown_requested:
            self.logger.info("Shutdown requested, stopping experiment setup")
            return []
        
        # 并行执行实验
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            loop = asyncio.get_event_loop()
            
            # 创建任务
            tasks = []
            for exp_info in experiment_infos:
                if self.shutdown_requested:
                    break
                
                task = loop.run_in_executor(
                    executor,
                    self.process_single_experiment,
                    exp_info
                )
                tasks.append(task)
            
            # 等待完成
            if tasks:
                try:
                    completed_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in completed_results:
                        if isinstance(result, Exception):
                            self.logger.error(f"Experiment failed with exception: {result}")
                            results.append({
                                "success": False,
                                "error": str(result),
                                "experiment_name": "unknown"
                            })
                        else:
                            results.append(result)
                            
                except KeyboardInterrupt:
                    self.logger.info("Experiments interrupted by user")
                    
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """打印执行摘要"""
        successful = sum(1 for r in results if r.get("success", False))
        total = len(results)
        
        print(f"\n{'='*60}")
        print(f"EXPERIMENT SUMMARY")
        print(f"{'='*60}")
        print(f"Total experiments: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success rate: {successful/total*100:.1f}%" if total > 0 else "N/A")
        
        # 打印系统指标
        system_stats = self.metrics.get_system_summary()
        print(f"\nSYSTEM METRICS:")
        print(f"Total LLM calls: {system_stats['total_llm_calls']}")
        print(f"Total tokens: {system_stats['total_tokens']}")
        print(f"Total errors: {system_stats['total_errors']}")
        print(f"Average experiment duration: {system_stats['average_experiment_duration']:.2f}s")
        
        # 打印客户端池统计
        pool_stats = self.client_pool.get_pool_stats()
        print(f"\nLLM CLIENT POOL:")
        print(f"Active clients: {pool_stats['total_clients']}")
        print(f"Total usage: {pool_stats['total_usage']}")
        
        # 打印重试统计
        retry_stats = self.retry_strategy.get_strategy_stats()
        print(f"\nRETRY STATISTICS:")
        print(f"Total retry attempts: {retry_stats['global_stats']['total_attempts']}")
        print(f"Successful retries: {retry_stats['global_stats']['successful_retries']}")
        print(f"Failed retries: {retry_stats['global_stats']['failed_retries']}")
        
        print(f"{'='*60}\n")

def silence_external_logs():
    """静默化外部库日志"""
    external_loggers = ["httpcore.http11", "httpcore.connection", "openai._base_client", "httpx"]
    for logger_name in external_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
        logger.addHandler(logging.NullHandler())
        logger.propagate = False

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CircuitMind-Lite - Optimized Verilog Code Generation System")
    parser.add_argument("-m", "--model", help="Model name to use", default=None)
    parser.add_argument("-k", "--key_index", type=int, help="Index of the API key to use", default=0)
    parser.add_argument("-r", "--root", type=str, help="Root directory for experiments", default=None)
    parser.add_argument("-t", "--target", action="append", help="Target experiment paths", default=[])
    parser.add_argument("-e", "--environment", type=str, help="Environment configuration", default="development")
    parser.add_argument("-w", "--workers", type=int, help="Number of parallel workers", default=4)
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    args = parser.parse_args()

    print("Starting CircuitMind-Lite (Optimized Version)")
    
    # 设置环境
    if args.environment:
        os.environ["ENVIRONMENT"] = args.environment
    
    try:
        # 初始化配置管理器
        config_manager = get_config_manager()
        config = config_manager.config
        
        print(f"Configuration loaded - Environment: {config.environment}, Debug: {config.debug}")
        
        # 处理命令行参数
        if args.model:
            if args.model in config.models:
                config_manager.switch_model(args.model)
                print(f"Switched to model: {args.model}")
            else:
                available_models = list(config.models.keys())
                print(f"Error: Model '{args.model}' not found. Available: {available_models}")
                sys.exit(1)
        
        if args.key_index > 0:
            model_config = config_manager.get_model_config()
            if args.key_index < len(model_config.api_config.api_keys):
                model_config.api_config.current_key_index = args.key_index
                print(f"Using API key index: {args.key_index}")
            else:
                print(f"Warning: Key index {args.key_index} out of range")
        
        if args.root:
            config.experiments.root_dir = args.root
        
        if args.target:
            config.experiments.target_experiments = args.target
        
        # 创建输出目录
        output_root = config.experiments.get_output_dir(config.current_model)
        os.makedirs(output_root, exist_ok=True)
        
        # 静默化外部日志
        silence_external_logs()
        
        print(f"Current model: {config.current_model}")
        print(f"Experiments root: {config.experiments.root_dir}")
        
        # 准备实验列表
        target_experiments = config.experiments.target_experiments
        
        if not target_experiments:
            # 扫描根目录
            experiments_root = Path(config.experiments.root_dir)
            if not experiments_root.exists():
                raise ConfigurationError(f"Experiments root directory does not exist: {experiments_root}")
            
            target_experiments = [str(f) for f in experiments_root.iterdir() if f.is_dir()]
        
        if not target_experiments:
            print("No experiments found to process.")
            return
        
        print(f"Found {len(target_experiments)} experiments to process")
        
        # 创建实验运行器
        max_workers = 1 if args.no_parallel else args.workers
        runner = ExperimentRunner(config_manager, max_workers=max_workers)
        
        # 运行实验
        if args.no_parallel or max_workers == 1:
            print("Running experiments sequentially...")
            results = []
            for exp_path in target_experiments:
                env_info = runner.setup_environment(exp_path)
                if env_info:
                    result = runner.process_single_experiment(env_info)
                    results.append(result)
        else:
            print(f"Running experiments in parallel with {max_workers} workers...")
            results = await runner.run_experiments_parallel(target_experiments)
        
        # 打印摘要
        runner.print_summary(results)
        
        print("All experiments completed successfully.")
        
    except ConfigValidationError as e:
        print(f"Configuration validation error: {e}")
        sys.exit(1)
    except CircuitMindError as e:
        print(f"Application error: {e}")
        logging.exception("Application error occurred")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.exception("Unexpected error occurred")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted")
        sys.exit(0)