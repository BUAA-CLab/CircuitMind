import json
import numpy as np
from typing import List, Dict, Any
import faiss
from ollama import Client
import os
import re
from shutil import copyfile
from utils.logger import setup_logger, DIALOGUE_LOG_LEVEL
from src.config import get_config_manager

# Initialize Ollama client from config
config_manager = get_config_manager()
rag_config = config_manager.config.rag
ollama_client = Client(host=rag_config.ollama_host)

# Data loading and preprocessing
def load_json_data(file_paths: List[str]) -> List[Dict[str, Any]]:
    all_data = []
    for file_path in file_paths:
        if os.path.exists(file_path) == False:
            copyfile("./knowledge_base/Model-incrementment/demo.json",file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.extend(data)
    return all_data

# Text embedding
def get_embedding(text: str, model: str = "nomic-embed-text", client: Client = None) -> np.ndarray:
    if client is None:
        client = ollama_client
    response = client.embeddings(model=model, prompt=text)
    return np.array(response['embedding'])

# Extract keywords using LLM
def extract_keywords_with_llm(query: str, model: str = "mistral", client: Client = None) -> List[str]:
    if client is None:
        client = ollama_client
    prompt = f"""
    Extract keywords related to circuit design, Verilog, or hardware description from the following query.
    Query: "{query}"
    Please return the keywords as a comma-separated list, e.g., "keyword1, keyword2, keyword3".
    """
    response = client.generate(model=model, prompt=prompt)
    keywords = [kw.strip() for kw in response['response'].split(',')]
    return keywords

def extract_key_error_with_llm(query: str, model: str = "mistral", client: Client = None) -> List[str]:
    if client is None:
        client = ollama_client
    prompt = f"""
    Please extract and summarize the key error messages from the provided compilation log, removing any file directory information. Focus on the specific error types and descriptions, such as 'It was declared here as an instance name' or 'error: [variable] has already been declared in this scope.' The log is "{query}". Provide a clear and concise errors as a comma-separated list, e.g., "error_type1, error_type2, error_type3".
    """
    response = client.generate(model=model, prompt=prompt)
    key_errors= [kw.strip() for kw in response['response'].split(',')]
    return key_errors

# Build FAISS index
class VectorIndex:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)
        self.data = []
        self.dimension = dimension
        print(f"Index dimension: {self.index.d}")  # 打印索引的维度

    def add(self, vectors: np.ndarray, entries: List[Dict[str, Any]]):
        self.index.add(vectors)
        self.data.extend(entries)

    def search(self, query_vector: np.ndarray, k: int = 10) -> List[tuple]:
        distances, indices = self.index.search(query_vector.reshape(1, -1), k)
        return [(self.data[idx], distances[0][i]) for i, idx in enumerate(indices[0])]

    def save(self, index_path: str, data_path: str):
        faiss.write_index(self.index, index_path)
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(index_path: str, data_path: str) -> 'VectorIndex':
        index = faiss.read_index(index_path)
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        vector_index = VectorIndex(dimension=index.d)
        vector_index.index = index
        vector_index.data = data
        return vector_index

# Categorization and information extraction
def categorize_and_extract(entry: Dict[str, Any], query: str) -> Dict[str, Any]:
    if "practice_title" in entry:
        return {
            "class": "best_practices",
            "type": "best_practice",
            "title": entry["practice_title"],
            "description": entry["practice_description"],
            "code_example": entry["code_example"],
            "tags": entry["tags"]
        }
    elif "design_type" in entry:
        return {
            "class": "circuit_designs",
            "type": "circuit_design",
            "design_type": entry["design_type"],
            "requirements": entry["design_requirements"],
            "solution_pattern": entry["solution_pattern"],
            "tags": entry["tags"]
        }
    elif "error_type" in entry:
        return {
            "id": entry["id"],
            "class": "error_pattern",
            "type": "error_pattern",
            "error_type": entry["error_type"],
            "keywords": entry["keywords"]
        }
    return {}
# Load detailed data and find by ID with selected fields
def get_detailed_entry(detailed_data: List[Dict[str, Any]], id: int, fields: List[str] = None) -> Dict[str, Any]:
    for entry in detailed_data:
        if entry.get("id") == id:
            if fields is None:  # 如果未指定字段，返回所有字段
                return entry
            else:  # 只返回指定字段
                return {key: entry.get(key) for key in fields if key in entry}
    return {}
# Keyword filtering
def keyword_filter(results: List[tuple], keywords: List[str]) -> List[Dict[str, Any]]:
    if not keywords:
        return [r[0] for r in results]
    filtered = []
    for result, _ in results:
        tags_or_keywords = result.get("tags", []) or result.get("keywords", [])
        if any(kw.lower() in [t.lower() for t in tags_or_keywords] for kw in keywords):
            filtered.append(result)
    return filtered if filtered else [r[0] for r in results]  # Return all results if no match

# Improved matching and sorting (partial matching)
def prioritize_match(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    def get_description(entry):
        return entry.get("description", "") or entry.get("requirements", "") or entry.get("problem_description", "")
    
    def match_score(desc: str, query: str) -> float:
        desc_words = set(desc.lower().split())
        query_words = set(query.lower().split())
        common_words = desc_words & query_words
        return len(common_words) / max(len(query_words), 1)  # Calculate overlap ratio
    
    sorted_results = sorted(results, key=lambda x: match_score(get_description(x), query), reverse=True)
    return sorted_results

def prioritize_match_coder(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    def get_description_coder(entry):
        return entry.get("design_requirements", "") or entry.get("module_name", "") or entry.get("design_features", "")
    
    def match_score(desc: str, query: str) -> float:
        desc_words = set(desc.lower().split())
        query_words = set(query.lower().split())
        common_words = desc_words & query_words
        return len(common_words) / max(len(query_words), 1)  # Calculate overlap ratio
    
    sorted_results = sorted(results, key=lambda x: match_score(get_description_coder(x), query), reverse=True)
    return sorted_results

# RAG main process
class RAGSystem:
    def __init__(self, file_paths: List[str], detailed_file_path: str, 
                 embedding_model: str = None, llm_model: str = None,
                 index_path: str = None, data_path: str = None,
                 model_datapath: str = None):
        
        print("🤖 RAGSystem: Starting initialization...")
        
        # 从新配置系统获取默认值
        config_manager = get_config_manager()
        config = config_manager.config
        rag_config = config.rag
        
        print(f"🤖 RAGSystem: Config loaded, ollama_host={rag_config.ollama_host}")
        
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.index_path = index_path
        self.data_path = data_path
        
        # 创建RAGSystem实例专用的ollama客户端
        self.ollama_client = Client(host=rag_config.ollama_host)
        if model_datapath is None:
            model_name = config.current_model
            self.model_summary_data = f"./knowledge_base/Model-incrementment/{model_name}.json"
        else:
            self.model_summary_data = model_datapath
        self.model_summary_index_path = index_path.replace("vector_index.faiss","model_summary_index.faiss")
        self.model_summary_data_path = data_path.replace("vector_data.json","model_summary_data.json")
        self.logger = setup_logger(f"RAG")
        # Load detailed data
        self.error_detailed_data = load_json_data([detailed_file_path['error_patterns']])

        self._log("info",f"Loaded detailed data with {len(self.error_detailed_data)} entries")
        if os.path.exists(index_path) and os.path.exists(data_path):
            self._log("info","Loading saved index and data...")
            self.vector_index = VectorIndex.load(index_path, data_path)
        else:
            self._log("info","Building new index and data...")
            self.data = load_json_data(file_paths)
            texts = [entry.get("error_message", "") for entry in self.data]
            vectors = np.array([get_embedding(text, embedding_model, self.ollama_client) for text in texts])
            self.vector_index = VectorIndex(dimension=vectors.shape[1])
            self.vector_index.add(vectors, self.data)
            self.vector_index.save(index_path, data_path)
            self._log("info",f"Index saved to {index_path}, data saved to {data_path}")
        self._log("info",f"DEBUG:{self.model_summary_data=}")
        self.model_summary_data = load_json_data([self.model_summary_data])
        texts = [entry.get("module_name", "") for entry in self.model_summary_data]
        summary_vectors = np.array([get_embedding(text, embedding_model, self.ollama_client) for text in texts])
        self.summary_vector_index = VectorIndex(dimension=summary_vectors.shape[1])
        self.summary_vector_index.add(summary_vectors, self.model_summary_data)
        self.summary_vector_index.save(self.model_summary_index_path, self.model_summary_data_path)
        
        print("✅ RAGSystem: Initialization completed successfully!")
    
    def _log(self, level: str, message: str):
        getattr(self.logger, level)(message)
    def retrieve_reviewer(self, query: str, k: int = 10, detailed_fields: List[str] = None) -> List[Dict[str, Any]]:
        extracted_errors = extract_key_error_with_llm(query, self.llm_model, self.ollama_client)
        get_results = []
        ids = []
        for error in extracted_errors:
            self._log("info", f"{error}")
            query_vector = get_embedding(error, self.embedding_model, self.ollama_client)
            self._log("info",f"Query vector shape: {query_vector.shape}")  # 打印查询向量的维度
            self._log("info",f"Index dimension: {self.vector_index.index.d}")  # 打印索引的维度
            results_with_distances = self.vector_index.search(query_vector, k)
            # Extract keywords using LLM
            keywords = extract_keywords_with_llm(error, self.llm_model, self.ollama_client)
            
            # self._log("info",f"Keywords extracted by LLM: {keywords}")
            
            filtered_results = keyword_filter(results_with_distances, keywords)
            prioritized_results = prioritize_match(filtered_results, query)
            extracted = [categorize_and_extract(entry, query) for entry in prioritized_results]
        
            # Add detailed data based on retrieved ID with selected fields
            for result in extracted[:1]:
                if "id" in result:
                    detailed_entry = get_detailed_entry(self.error_detailed_data, result["id"], detailed_fields)
                    detailed_entry["class"] = result["class"]
                    if detailed_entry:
                        result["detailed_info"] = detailed_entry
            if extracted[0]['detailed_info']['id'] not in ids:
                ids.append(extracted[0]['detailed_info']['id'])
                get_results.append(extracted[0]["detailed_info"])
        # return extracted[:1]  # Return top result
        return get_results # 只输出详细数据不输出简化版部分
    
    def retrieve_coder(self, query, k: int = 2) -> List[Dict[str, Any]]:
        query_vector = get_embedding(query, self.embedding_model, self.ollama_client)
        results_with_distances = self.summary_vector_index.search(query_vector, k)
        result_dicts = [entry for entry, _ in results_with_distances]  # 只取字典，忽略距离
        prioritized_results = prioritize_match_coder(result_dicts, query)
        extracted = [categorize_and_extract(entry, query) for entry in prioritized_results]
        return extracted[0]['solution_pattern']

# Example usage
def main():
    file_paths = [
        "best_practices.json",
        "circuit_designs.json",
        "error_patterns.json"
    ]
    
    rag = RAGSystem(file_paths, embedding_model="nomic-embed-text", llm_model="mistral")
    
    queries = [
        "Design a circuit to store and read a single byte of data.",
        "Design a simple D flip-flop with synchronous reset",
        "Why does my testbench timeout?"
    ]
    
    for query in queries:
        # self._log("info",f"\nQuery: {query}")
        retrieved = rag.retrieve(query)
        print("Retrieved results:")
        for i, item in enumerate(retrieved, 1):
            print(f"\nResult {i}:")
            print(json.dumps(item, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()