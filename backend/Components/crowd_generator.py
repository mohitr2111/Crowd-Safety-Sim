from typing import Dict, List, Optional
import random
import numpy as np
from dataclasses import dataclass

@dataclass
class CrowdPattern:
    """Represents how crowd arrives/moves"""
    name: str
    arrival_rate_range: tuple  # (min, max) people/second
    duration: float  # seconds
    distribution_type: str  # 'normal', 'exponential', 'poisson'
    intensity_profile: str  # 'gradual', 'sudden', 'sustained'

class CrowdGenerator:
    """
    Generate realistic crowd distributions.
    
    Real-world patterns:
    - Temple pilgrimage: exponential surge at auspicious times
    - Stadium evacuation: sustained pressure on exits
    - Rally crowd: buildup then release
    - Train station: wave patterns during rush hours
    """
    
    # Real crowd patterns from historical stampedes
    REAL_PATTERNS = {
        'mahakumbh_auspicious_time': {
            'description': 'Mahakumbh pilgrimage surge (auspicious bathing time)',
            'arrival_rate_range': (100, 500),  # people/second
            'duration': 300,  # 5-minute window
            'distribution_type': 'exponential',
            'intensity_profile': 'sudden',
            'entry_zones_distribution': {
                'entrance_main': 0.6,  # 60% through main
                'entrance_side': 0.4
            }
        },
        
        'stadium_post_event': {
            'description': 'Stadium evacuation after event (everyone leaves)',
            'arrival_rate_range': (50, 200),  # people/second
            'duration': 600,  # 10 minutes
            'distribution_type': 'sustained',
            'intensity_profile': 'sustained',
            'entry_zones_distribution': {
                'zone_north': 0.25,
                'zone_south': 0.25,
                'zone_east': 0.25,
                'zone_west': 0.25
            }
        },
        
        'rally_buildup': {
            'description': 'Rally ground buildup to main event',
            'arrival_rate_range': (20, 150),  # people/second
            'duration': 1800,  # 30 minutes
            'distribution_type': 'normal',
            'intensity_profile': 'gradual',
            'entry_zones_distribution': {
                'entrance_main': 0.5,
                'entrance_side1': 0.25,
                'entrance_side2': 0.25
            }
        },
        
        'train_rush_hour': {
            'description': 'Train platform during rush hour',
            'arrival_rate_range': (30, 120),  # people/second
            'duration': 600,  # 10 minutes
            'distribution_type': 'poisson',
            'intensity_profile': 'sustained',
            'entry_zones_distribution': {
                'platform_entry': 1.0
            }
        },
        
        'itaewon_pre_stampede': {
            'description': 'Itaewon 2022 - buildup before stampede',
            'arrival_rate_range': (80, 300),  # people/second
            'duration': 180,  # 3 minutes
            'distribution_type': 'exponential',
            'intensity_profile': 'sudden',
            'goal_zone_concentration': 'narrow_alley',
            'entry_zones_distribution': {
                'entrance_main': 1.0
            }
        }
    }
    
    def __init__(self):
        self.patterns: Dict[str, CrowdPattern] = {}
    
    def generate_crowd_for_scenario(self, 
                                   scenario_zones: List[str],
                                   total_people_range: tuple,
                                   pattern: str = 'normal',
                                   goal_zone_range: Optional[tuple] = None) -> Dict:
        """
        Generate realistic crowd distribution.
        
        Args:
            scenario_zones: List of zone IDs
            total_people_range: (min, max) total crowd size
            pattern: Which arrival pattern to use
            goal_zone_range: (min, max) what % of crowd goes to primary goal
        
        Returns:
            Spawn configuration with realistic distributions
        """
        
        # Random crowd size within range
        total_people = random.randint(*total_people_range)
        
        # Select crowd pattern
        if pattern in self.REAL_PATTERNS:
            crowd_pattern = self.REAL_PATTERNS[pattern]
        else:
            crowd_pattern = self._create_custom_pattern(pattern)
        
        # Generate spawn configuration with realistic ranges
        spawn_config = []
        remaining_people = total_people
        
        # Get entrance zones
        entrance_zones = [z for z in scenario_zones if 'entrance' in z.lower() or z == 'platform_entry']
        if not entrance_zones:
            entrance_zones = scenario_zones[:len(scenario_zones)//4]  # Use first zones
        
        # Get exit zones
        exit_zones = [z for z in scenario_zones if 'exit' in z.lower()]
        primary_exit = exit_zones[0] if exit_zones else scenario_zones[-1]
        
        # Distribute crowd through entrances
        entry_dist = crowd_pattern.get('entry_zones_distribution', {})
        
        for entrance_zone in entrance_zones:
            # Each entrance gets a share
            zone_ratio = entry_dist.get(entrance_zone, 1.0 / len(entrance_zones))
            zone_people = int(total_people * zone_ratio)
            
            if zone_people > 0:
                # Add variance (real crowds aren't perfectly distributed)
                variance = int(zone_people * 0.15)  # ±15% variance
                zone_people = random.randint(max(1, zone_people - variance), 
                                            zone_people + variance)
                remaining_people -= zone_people
                
                # Agent type distribution
                agent_types = self._get_agent_type_distribution(pattern)
                
                spawn_config.append({
                    'spawn_zone': entrance_zone,
                    'goal_zone': primary_exit,
                    'count': zone_people,
                    'type_distribution': agent_types,
                    'arrival_stagger': self._get_arrival_stagger(crowd_pattern)
                })
        
        # Add remaining people to largest group
        if remaining_people > 0 and spawn_config:
            spawn_config[0]['count'] += remaining_people
        
        return {
            'total_people': total_people,
            'pattern': pattern,
            'pattern_description': crowd_pattern.get('description', ''),
            'spawn_config': spawn_config,
            'arrival_parameters': {
                'rate_range': crowd_pattern.get('arrival_rate_range', (50, 200)),
                'distribution': crowd_pattern.get('distribution_type', 'normal'),
                'intensity': crowd_pattern.get('intensity_profile', 'sustained')
            }
        }
    
    def _get_agent_type_distribution(self, pattern: str) -> Dict[str, float]:
        """Get realistic agent type mix for pattern"""
        distributions = {
            'mahakumbh_auspicious_time': {
                'normal': 0.50,  # Regular pilgrims
                'elderly': 0.25,  # Many elderly pilgrims
                'family': 0.20,  # Family groups
                'rushing': 0.05
            },
            'stadium_post_event': {
                'normal': 0.70,
                'family': 0.15,
                'elderly': 0.10,
                'rushing': 0.05
            },
            'rally_buildup': {
                'rushing': 0.40,  # Excited crowd
                'normal': 0.40,
                'family': 0.15,
                'elderly': 0.05
            },
            'train_rush_hour': {
                'rushing': 0.60,  # Commuters in hurry
                'normal': 0.30,
                'family': 0.05,
                'elderly': 0.05
            },
            'itaewon_pre_stampede': {
                'rushing': 0.50,  # Young crowd, excited
                'normal': 0.40,
                'family': 0.08,
                'elderly': 0.02
            }
        }
        
        return distributions.get(pattern, {
            'normal': 0.70,
            'family': 0.15,
            'elderly': 0.10,
            'rushing': 0.05
        })
    
    def _get_arrival_stagger(self, crowd_pattern: Dict) -> Dict:
        """Get temporal arrival pattern (people don't all arrive simultaneously)"""
        intensity = crowd_pattern.get('intensity_profile', 'sustained')
        
        if intensity == 'sudden':
            return {
                'start_delay': random.uniform(5, 15),  # Wait 5-15s before surge
                'peak_at_second': random.uniform(20, 50),  # Peak at 20-50s
                'drop_after_second': random.uniform(100, 200)  # Drop after
            }
        elif intensity == 'gradual':
            return {
                'start_delay': 0,
                'peak_at_second': float('inf'),  # No peak, sustained
                'curve': 'linear_increase'
            }
        else:  # sustained
            return {
                'start_delay': random.uniform(0, 10),
                'peak_at_second': random.uniform(50, 150),
                'sustained_until': random.uniform(300, 600)
            }
    
    def _create_custom_pattern(self, pattern_name: str) -> Dict:
        """Create custom pattern from name"""
        return {
            'description': f'Custom: {pattern_name}',
            'arrival_rate_range': (50, 200),
            'distribution_type': 'normal',
            'intensity_profile': 'sustained',
            'entry_zones_distribution': {}
        }
    
    def generate_crowd_range_visualization(self, 
                                         total_range: tuple,
                                         pattern: str) -> Dict:
        """
        Visualize crowd size range for user selection.
        
        Returns visualization hints for UI
        """
        min_crowd, max_crowd = total_range
        
        steps = [
            {
                'level': 'Light',
                'emoji': '🟢',
                'people': min_crowd + (max_crowd - min_crowd) * 0.25,
                'description': 'Off-peak hours'
            },
            {
                'level': 'Moderate',
                'emoji': '🟡',
                'people': min_crowd + (max_crowd - min_crowd) * 0.50,
                'description': 'Normal operations'
            },
            {
                'level': 'Heavy',
                'emoji': '🟠',
                'people': min_crowd + (max_crowd - min_crowd) * 0.75,
                'description': 'Peak hours'
            },
            {
                'level': 'Critical',
                'emoji': '🔴',
                'people': max_crowd,
                'description': 'Auspicious time (like Mahakumbh)'
            }
        ]
        
        return {
            'pattern': pattern,
            'range': total_range,
            'steps': steps
        }
    
    @staticmethod
    def get_realistic_ranges_for_venue(venue_type: str) -> Dict:
        """Get realistic crowd ranges for venue type"""
        ranges = {
            'temple': {
                'min': 1000,
                'max': 80000000,  # Mahakumbh scale!
                'typical_event': (500000, 5000000),
                'peak_event': (20000000, 80000000),
                'note': 'Highly variable based on auspicious timing'
            },
            'stadium': {
                'min': 1000,
                'max': 100000,
                'typical_event': (40000, 80000),
                'peak_event': (90000, 100000),
                'note': 'Fixed capacity, but evacuation surges can exceed normal density'
            },
            'train_platform': {
                'min': 500,
                'max': 10000,
                'typical_event': (2000, 5000),
                'peak_hour': (7000, 10000),
                'note': 'Rush hour patterns'
            },
            'rally_ground': {
                'min': 5000,
                'max': 1000000,
                'typical_event': (50000, 200000),
                'peak_event': (500000, 1000000),
                'note': 'Celebrity events can draw huge crowds'
            }
        }
        
        return ranges.get(venue_type, ranges['stadium'])