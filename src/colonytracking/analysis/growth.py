"""Growth analysis module - calculates colony growth metrics."""

import numpy as np
from typing import List, Dict
import logging

from colonytracking.data import Colony, AnalysisResult

logger = logging.getLogger(__name__)


class GrowthAnalysis:
    """Analyze colony growth metrics."""
    
    @staticmethod
    def compute_emergence_times(colonies: List[Colony]) -> Dict[int, int]:
        """Determine emergence frame for each colony."""
        emergence_times = {}
        area_threshold = 1000
        
        for colony in colonies:
            areas = colony.get_areas()
            for frame_idx, area in enumerate(areas):
                if area > area_threshold:
                    emergence_times[colony.colony_id] = frame_idx
                    colony.emergence_frame = frame_idx
                    logger.debug(f"Colony {colony.colony_id} emerged at frame {frame_idx}")
                    break
        
        return emergence_times
    
    @staticmethod
    def compute_growth_rates(colonies: List[Colony]) -> Dict[int, float]:
        """Compute growth rate for each colony."""
        growth_rates = {}
        
        for colony in colonies:
            if colony.emergence_frame < 0 or len(colony.measurements) < 2:
                growth_rates[colony.colony_id] = 0.0
                continue
            
            diameters = colony.get_diameters()
            emergence = colony.emergence_frame
            
            if len(diameters) - emergence < 3:
                growth_rates[colony.colony_id] = 0.0
                continue
            
            timepoints = np.arange(emergence, len(diameters))
            post_emergence_diameters = diameters[emergence:]
            
            coeffs = np.polyfit(timepoints, post_emergence_diameters, 1)
            growth_rate = float(coeffs[0])
            
            growth_rates[colony.colony_id] = growth_rate
            logger.debug(f"Colony {colony.colony_id} growth rate: {growth_rate:.3f} px/frame")
        
        return growth_rates
    
    @staticmethod
    def compute_final_sizes(colonies: List[Colony]) -> Dict[int, float]:
        """Get final size for each colony."""
        final_sizes = {}
        
        for colony in colonies:
            last_measurement = colony.get_last_measurement()
            if last_measurement:
                final_sizes[colony.colony_id] = last_measurement.diameter
            else:
                final_sizes[colony.colony_id] = 0.0
        
        return final_sizes
    
    @staticmethod
    def analyze(colonies: List[Colony]) -> AnalysisResult:
        """Perform complete analysis on colony set."""
        logger.info(f"Analyzing {len(colonies)} colonies")
        
        emergence_times = GrowthAnalysis.compute_emergence_times(colonies)
        growth_rates = GrowthAnalysis.compute_growth_rates(colonies)
        final_sizes = GrowthAnalysis.compute_final_sizes(colonies)
        
        result = AnalysisResult(
            colonies=colonies,
            emergence_times=emergence_times,
            growth_rates=growth_rates,
            final_sizes=final_sizes,
        )
        
        if emergence_times:
            logger.info(f"Analysis complete. Emergence range: {min(emergence_times.values())} - {max(emergence_times.values())}")
        return result
