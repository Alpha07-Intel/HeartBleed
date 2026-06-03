import concurrent.futures
import importlib
import pkgutil
from typing import List, Type
from .models import Investigation, InputType, Profile
from ..collectors.base import BaseCollector
from ..analyzers.correlation import CorrelationEngine
from ..analyzers.dorker import generate_dorks
from ..analyzers.profiler import extract_keywords
from ..utils.mutator import get_mutations
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

    def run(self, input_type: InputType, input_value: str, mutate: bool = False) -> Investigation:
        """Runs the search process using parallel execution."""
        investigation = Investigation(input_type=input_type, input_value=input_value)
        
        # 1. Generate Dorks
        investigation.dorks = generate_dorks(input_value)
        
        # 2. Determine Targets (include mutations if requested)
        targets = [input_value]
        if mutate and input_type == InputType.USERNAME:
            mutations = get_mutations(input_value)
            if mutations:
                logger.info(f"Expanding search with mutations: {', '.join(mutations)}")
                targets.extend(mutations)
        
        # Filter collectors that support this input type
        active_collectors = [c for c in self.collectors if c.supports(input_type)]
        
        profiles: List[Profile] = []
        
        # 3. Launch Collection for each target
        for target in targets:
            if target != input_value:
                logger.info(f"Scanning mutation: {target}...")
                
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Map fetch tasks
                future_to_collector = {
                    executor.submit(c.fetch, input_type, target): c 
                    for c in active_collectors
                }
                
                for future in concurrent.futures.as_completed(future_to_collector):
                    collector = future_to_collector[future]
                    try:
                        profile = future.result()
                        if profile:
                            # Avoid duplicates if multiple mutations return same profile (unlikely but possible)
                            if not any(p.url == profile.url for p in profiles):
                                profiles.append(profile)
                                logger.info(f"[green]Found profile on {profile.platform}[/green] ({target})")
                    except Exception as e:
                        logger.error(f"Collector {collector.platform_name} failed for {target}: {e}")

        investigation.profiles = profiles
        
        # 4. Correlate Results
        if profiles:
            logger.info("Correlating discovered profiles...")
            analyzer = CorrelationEngine(input_value)
            investigation.correlations = analyzer.correlate_batch(profiles)
            
            # 5. Profile Bios (Keyword Extraction)
            bios = [p.bio for p in profiles if p.bio]
            if bios:
                logger.info("Analyzing bios for persona profiling...")
                investigation.persona_profile = extract_keywords(bios)
            
        return investigation
