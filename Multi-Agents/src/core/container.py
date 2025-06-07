# src/core/container.py
from typing import TypeVar, Type, Dict, Any, Callable, Optional
from abc import ABC, abstractmethod
import inspect

T = TypeVar('T')

class ServiceNotFoundError(Exception):
    """服务未找到异常"""
    pass

class CircularDependencyError(Exception):
    """循环依赖异常"""
    pass

class Container:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, bool] = {}
        self._resolving: set = set()  # 用于检测循环依赖
    
    def register_singleton(self, interface: Type[T], implementation: Any):
        """注册单例服务"""
        key = self._get_service_key(interface)
        self._services[key] = implementation
        self._singletons[key] = True
        return self
    
    def register_transient(self, interface: Type[T], factory: Callable[[], T]):
        """注册瞬态服务（每次都创建新实例）"""
        key = self._get_service_key(interface)
        self._factories[key] = factory
        self._singletons[key] = False
        return self
    
    def register_factory(self, interface: Type[T], factory: Callable[['Container'], T]):
        """注册工厂方法（支持依赖注入）"""
        key = self._get_service_key(interface)
        self._factories[key] = factory
        self._singletons[key] = False
        return self
    
    def register_instance(self, interface: Type[T], instance: T):
        """注册具体实例"""
        key = self._get_service_key(interface)
        self._services[key] = instance
        self._singletons[key] = True
        return self
    
    def get(self, interface: Type[T]) -> T:
        """获取服务实例"""
        key = self._get_service_key(interface)
        
        # 检查循环依赖
        if key in self._resolving:
            raise CircularDependencyError(f"Circular dependency detected for {key}")
        
        # 如果是已注册的单例实例，直接返回
        if key in self._services and self._singletons.get(key, False):
            return self._services[key]
        
        # 如果有工厂方法，使用工厂创建
        if key in self._factories:
            self._resolving.add(key)
            try:
                factory = self._factories[key]
                
                # 检查工厂方法签名，决定是否传入容器
                sig = inspect.signature(factory)
                if len(sig.parameters) > 0:
                    instance = factory(self)
                else:
                    instance = factory()
                
                # 如果是单例，缓存实例
                if self._singletons.get(key, False):
                    self._services[key] = instance
                
                return instance
            finally:
                self._resolving.discard(key)
        
        # 如果有非单例实例，直接返回
        if key in self._services:
            return self._services[key]
        
        raise ServiceNotFoundError(f"Service {key} not registered")
    
    def try_get(self, interface: Type[T]) -> Optional[T]:
        """尝试获取服务，失败时返回None"""
        try:
            return self.get(interface)
        except ServiceNotFoundError:
            return None
    
    def is_registered(self, interface: Type[T]) -> bool:
        """检查服务是否已注册"""
        key = self._get_service_key(interface)
        return key in self._services or key in self._factories
    
    def _get_service_key(self, interface: Type[T]) -> str:
        """获取服务键"""
        if hasattr(interface, '__name__'):
            return interface.__name__
        return str(interface)
    
    def auto_wire(self, cls: Type[T]) -> T:
        """自动装配类的依赖"""
        # 获取构造函数签名
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            # 如果参数有类型注解，尝试从容器获取
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.get(param.annotation)
                except ServiceNotFoundError:
                    # 如果有默认值，使用默认值
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default
                    else:
                        raise ServiceNotFoundError(
                            f"Cannot resolve dependency {param.annotation} for {cls.__name__}"
                        )
        
        return cls(**kwargs)

