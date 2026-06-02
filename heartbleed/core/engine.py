import concurrent.futures
import importlib
import pkgutil
from typing import List, Type
from .models import Investigation, InputType, Profile
from ..collectors.base import BaseCollector
from ..analyzers.correlation import CorrelationEngine
from ..utils.logger import logger
from .. import collectors

class SearchEngine:
    """Orchestrates the discovery and execution of collectors."""
    
    def __init__(self):
        self.collectors: List[BaseCollector] = self._discover_collectors()

    def _discover_collectors(self) -> List[BaseCollector]:
        """Dynamically discovers and instantiates collector classes."""
        discovered = []
        # Iterate through the collectors package
        for _, name, is_pkg in pkgutil.iter_modules(collectors.__path__):
            if is_pkg or name == "base":
                continue
            
            try:
                module = importlib.import_module(f"heartbleed.collectors.{name}")
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if (isinstance(attribute, type) and 
                        issubclass(attribute, BaseCollector) and 
                        attribute is not BaseCollector):
                        discovered.append(attribute())
                        logger.debug(f"Loaded collector: {name}")
            except Exception as e:
                logger.error(f"Failed to load collector {name}: {e}")
                
        return discovered

    def run(self, input_type: InputType, input_value: str) -> Investigation:
        """Runs the search process using parallel execution."""
        investigation = Investigation(input_type=input_type, input_value=input_value)
        
        # Filter collectors that support this input type
        active_collectors = [c for c in self.collectors if c.supports(input_type)]
        
        logger.info(f"Starting scan for {input_type.value}: {input_value} using {len(active_collectors)} collectors...")
        
        profiles: List[Profile] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Map fetch tasks
            future_to_collector = {
                executor.submit(c.fetch, input_type, input_value): c 
                for c in active_collectors
            }
            
            for future in concurrent.futures.as_completed(future_to_collector):
                collector = future_to_collector[future]
                try:
                    profile = future.result()
                    if profile:
                        profiles.append(profile)
                        logger.info(f"[green]Found profile on {profile.platform}[/green]")
                except Exception as e:
                    logger.error(f"Collector {collector.platform_name} failed: {e}")

        investigation.profiles = profiles
        
        # Correlate Results
        if profiles:
            logger.info("Correlating discovered profiles...")
            analyzer = CorrelationEngine(input_value)
            investigation.correlations = analyzer.correlate_batch(profiles)
            
        return investigation
