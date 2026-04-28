"""Visualization module for generating plots."""

import numpy as np
from typing import List, Optional, Tuple
import logging

from colonytracking.data import Colony

logger = logging.getLogger(__name__)


class PlotGenerator:
    """Generate visualizations of colony growth."""
    
    @staticmethod
    def plot_area_vs_time(colonies: List[Colony], figsize: Tuple[int, int] = (10, 6),
                         time_interval_minutes: int = 30,
                         save_path: Optional[str] = None):
        """Plot area over time for each colony."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib import cm
        except ImportError:
            logger.warning("matplotlib not installed, skipping plot generation")
            return None, None
        
        fig, ax = plt.subplots(figsize=figsize)
        
        colormap = cm.get_cmap('jet')
        colors = [colormap(i / len(colonies)) for i in range(len(colonies))] if len(colonies) > 0 else []
        
        for i, colony in enumerate(colonies):
            areas = colony.get_areas()
            timepoints = np.arange(len(areas)) * time_interval_minutes
            ax.plot(timepoints, areas, 'o-', color=colors[i], label=f'Colony {colony.colony_id}', alpha=0.7)
        
        ax.set_xlabel(f'Time (minutes, {time_interval_minutes} min/frame)')
        ax.set_ylabel('Area (pixels²)')
        ax.set_title('Colony Area Over Time')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Saved area plot to {save_path}")
        
        return fig, ax
    
    @staticmethod
    def plot_diameter_vs_time(colonies: List[Colony], figsize: Tuple[int, int] = (10, 6),
                             time_interval_minutes: int = 30,
                             save_path: Optional[str] = None):
        """Plot diameter over time for each colony."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib import cm
        except ImportError:
            logger.warning("matplotlib not installed, skipping plot generation")
            return None, None
        
        fig, ax = plt.subplots(figsize=figsize)
        
        colormap = cm.get_cmap('jet')
        colors = [colormap(i / len(colonies)) for i in range(len(colonies))] if len(colonies) > 0 else []
        
        for i, colony in enumerate(colonies):
            diameters = colony.get_diameters()
            timepoints = np.arange(len(diameters)) * time_interval_minutes
            ax.plot(timepoints, diameters, 'o-', color=colors[i], label=f'Colony {colony.colony_id}', alpha=0.7)
        
        ax.set_xlabel(f'Time (minutes, {time_interval_minutes} min/frame)')
        ax.set_ylabel('Diameter (pixels)')
        ax.set_title('Colony Diameter Over Time')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Saved diameter plot to {save_path}")
        
        return fig, ax
    
    @staticmethod
    def plot_normalized_growth(colonies: List[Colony], figsize: Tuple[int, int] = (10, 6),
                              time_interval_minutes: int = 30,
                              save_path: Optional[str] = None):
        """Plot normalized growth over time."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib import cm
        except ImportError:
            logger.warning("matplotlib not installed, skipping plot generation")
            return None, None
        
        fig, ax = plt.subplots(figsize=figsize)
        
        colormap = cm.get_cmap('jet')
        colors = [colormap(i / len(colonies)) for i in range(len(colonies))] if len(colonies) > 0 else []
        
        for i, colony in enumerate(colonies):
            normalized = colony.get_normalized_growth()
            timepoints = np.arange(len(normalized)) * time_interval_minutes
            ax.plot(timepoints, normalized, 'o-', color=colors[i], label=f'Colony {colony.colony_id}', alpha=0.7)
        
        ax.set_xlabel(f'Time (minutes, {time_interval_minutes} min/frame)')
        ax.set_ylabel('Normalized Diameter (D/D_emergence)')
        ax.set_title('Normalized Colony Growth')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Saved normalized growth plot to {save_path}")
        
        return fig, ax
    
    @staticmethod
    def plot_emergence_times(colonies: List[Colony], figsize: Tuple[int, int] = (10, 6),
                            time_interval_minutes: int = 30,
                            save_path: Optional[str] = None):
        """Plot bar chart of emergence times."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib import cm
        except ImportError:
            logger.warning("matplotlib not installed, skipping plot generation")
            return None, None
        
        fig, ax = plt.subplots(figsize=figsize)
        
        colony_ids = [c.colony_id for c in colonies]
        emergence_frames = [c.emergence_frame if c.emergence_frame >= 0 else 0 for c in colonies]
        emergence_times = np.array(emergence_frames) * time_interval_minutes
        
        colormap = cm.get_cmap('jet')
        colors = [colormap(i / len(colonies)) for i in range(len(colonies))] if len(colonies) > 0 else []
        
        ax.bar(range(len(colonies)), emergence_times, color=colors, alpha=0.7)
        ax.set_xlabel('Colony ID')
        ax.set_ylabel(f'Emergence Time (minutes, {time_interval_minutes} min/frame)')
        ax.set_title('Colony Emergence Times')
        ax.set_xticks(range(len(colonies)))
        ax.set_xticklabels(colony_ids)
        ax.grid(True, alpha=0.3, axis='y')
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Saved emergence plot to {save_path}")
        
        return fig, ax
