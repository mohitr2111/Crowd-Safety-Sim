from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

@dataclass
class Zone:
    """Represents a physical zone"""
    id: str
    name: str
    zone_type: str  # "zone" (crowd area), "exit", "corridor", "entrance"
    area_m2: float
    position: Tuple[float, float]  # (x, y) for visualization
    capacity: Optional[int] = None  # if None, calculate from density
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.zone_type,
            'area_m2': self.area_m2,
            'position': self.position,
            'capacity': self.capacity or int(self.area_m2 * 0.45)
        }

@dataclass
class Path:
    """Represents a connection between zones"""
    from_zone: str
    to_zone: str
    width_m: float
    flow_capacity: int  # people/second that can move through

class ScenarioBuilder:
    """
    Build custom scenarios for ANY venue.
    
    Real-world templates:
    - TEMPLE (Mahakumbh pattern): Multiple entrance → single sanctum → exits
    - STADIUM: Sections → concourse → exits
    - TRAIN_PLATFORM: Entry → platform → exits
    - RALLY_GROUND: Scattered entries → large open area → exits
    """
    
    TEMPLATE_DESCRIPTIONS = {
        'temple': 'Temple/Pilgrimage Site (like Mahakumbh)',
        'stadium': 'Sports Stadium (50k-100k capacity)',
        'train_platform': 'Railway Platform (rush hour)',
        'rally': 'Rally Ground / Outdoor Event (100k+ capacity)'
    }
    
    def __init__(self, name: str, template: str = None):
        self.name = name
        self.template = template
        self.zones: Dict[str, Zone] = {}
        self.paths: List[Path] = []
        self.description = ""
        
        if template:
            self._load_template(template)
    
    def _load_template(self, template: str):
        """Load a pre-built template"""
        templates = {
            'temple': self._create_temple_template,
            'stadium': self._create_stadium_template,
            'train_platform': self._create_train_template,
            'rally': self._create_rally_template
        }
        
        if template in templates:
            templates[template]()
    
    def _create_temple_template(self):
        """Create temple/pilgrimage site layout (Mahakumbh pattern)"""
        # Entrance area
        self.add_zone(Zone('entrance_main', 'Main Entrance', 'entrance', 400, (50, 90), 200))
        self.add_zone(Zone('queue_area', 'Queue Area', 'zone', 600, (50, 75), 250))
        
        # Sanctum (tight bottleneck - real issue!)
        self.add_zone(Zone('sanctum_approach', 'Sanctum Approach', 'corridor', 100, (50, 50), 50))
        self.add_zone(Zone('sanctum', 'Sanctum', 'zone', 150, (50, 30), 100))
        self.add_zone(Zone('sanctum_exit_area', 'Sanctum Exit', 'corridor', 100, (50, 10), 50))
        
        # Exits
        self.add_zone(Zone('exit_main', 'Main Exit', 'exit', 120, (10, 0), 80))
        self.add_zone(Zone('exit_side1', 'Side Exit 1', 'exit', 100, (40, 0), 60))
        self.add_zone(Zone('exit_side2', 'Side Exit 2', 'exit', 100, (60, 0), 60))
        self.add_zone(Zone('exit_emergency', 'Emergency Exit', 'exit', 80, (90, 0), 50))
        
        # Connections
        self.add_path(Path('entrance_main', 'queue_area', 4, 100))
        self.add_path(Path('queue_area', 'sanctum_approach', 2, 50))  # BOTTLENECK
        self.add_path(Path('sanctum_approach', 'sanctum', 2.5, 60))
        self.add_path(Path('sanctum', 'sanctum_exit_area', 2, 50))  # EXIT BOTTLENECK
        self.add_path(Path('sanctum_exit_area', 'exit_main', 2, 60))
        self.add_path(Path('sanctum_exit_area', 'exit_side1', 1.5, 40))
        self.add_path(Path('sanctum_exit_area', 'exit_side2', 1.5, 40))
        self.add_path(Path('queue_area', 'exit_emergency', 2, 50))  # Alternate route
        
        self.description = "Temple/Pilgrimage Layout (based on Mahakumbh)\nRisk: Sanctum approach and exit are severe bottlenecks"
    
    def _create_stadium_template(self):
        """Create stadium layout"""
        # Zones
        self.add_zone(Zone('zone_north', 'North Section', 'zone', 800, (50, 80), 350))
        self.add_zone(Zone('zone_south', 'South Section', 'zone', 800, (50, 20), 350))
        self.add_zone(Zone('zone_east', 'East Section', 'zone', 600, (80, 50), 250))
        self.add_zone(Zone('zone_west', 'West Section', 'zone', 600, (20, 50), 250))
        
        # Concourse
        self.add_zone(Zone('concourse', 'Central Concourse', 'zone', 300, (50, 50), 150))
        
        # Exits
        self.add_zone(Zone('exit_main', 'Main Exit', 'exit', 150, (50, 0), 100))
        self.add_zone(Zone('exit_north', 'North Exit', 'exit', 100, (30, 85), 70))
        self.add_zone(Zone('exit_south', 'South Exit', 'exit', 100, (70, 85), 70))
        
        # Connections
        self.add_path(Path('zone_north', 'concourse', 3, 80))
        self.add_path(Path('zone_south', 'concourse', 3, 80))
        self.add_path(Path('zone_east', 'concourse', 3, 80))
        self.add_path(Path('zone_west', 'concourse', 3, 80))
        self.add_path(Path('concourse', 'exit_main', 2, 60))
        self.add_path(Path('concourse', 'exit_north', 2, 50))
        self.add_path(Path('concourse', 'exit_south', 2, 50))
        
        self.description = "Sports Stadium Layout\nRisk: Single concourse bottleneck during mass exit"
    
    def _create_train_template(self):
        """Create train platform layout"""
        self.add_zone(Zone('platform_main', 'Main Platform', 'zone', 2000, (50, 50), 800))
        self.add_zone(Zone('exit_north', 'North Exit', 'exit', 150, (20, 95), 100))
        self.add_zone(Zone('exit_south', 'South Exit', 'exit', 150, (80, 95), 100))
        
        self.add_path(Path('platform_main', 'exit_north', 4, 80))
        self.add_path(Path('platform_main', 'exit_south', 4, 80))
        
        self.description = "Railway Platform Layout\nRisk: Limited exit capacity during rush hour"
    
    def _create_rally_template(self):
        """Create outdoor rally/festival ground"""
        self.add_zone(Zone('main_stage', 'Main Stage Area', 'zone', 3000, (50, 80), 1500))
        self.add_zone(Zone('mid_ground', 'Mid Ground', 'zone', 5000, (50, 50), 2000))
        self.add_zone(Zone('back_ground', 'Back Area', 'zone', 3000, (50, 20), 1500))
        
        self.add_zone(Zone('exit_main', 'Main Exit', 'exit', 300, (50, 0), 200))
        self.add_zone(Zone('exit_left', 'Left Exit', 'exit', 250, (10, 40), 150))
        self.add_zone(Zone('exit_right', 'Right Exit', 'exit', 250, (90, 40), 150))
        
        self.add_path(Path('main_stage', 'mid_ground', 8, 200))
        self.add_path(Path('mid_ground', 'back_ground', 8, 200))
        self.add_path(Path('back_ground', 'exit_main', 6, 150))
        self.add_path(Path('mid_ground', 'exit_left', 5, 100))
        self.add_path(Path('mid_ground', 'exit_right', 5, 100))
        
        self.description = "Rally/Festival Ground\nRisk: High density near stage, limited exits"
    
    def add_zone(self, zone: Zone):
        """Add a zone to the scenario"""
        self.zones[zone.id] = zone
    
    def add_path(self, path: Path):
        """Add a path between zones"""
        self.paths.append(path)
    
    def remove_zone(self, zone_id: str):
        """Remove a zone"""
        if zone_id in self.zones:
            del self.zones[zone_id]
            # Remove related paths
            self.paths = [p for p in self.paths 
                         if p.from_zone != zone_id and p.to_zone != zone_id]
    
    def modify_zone(self, zone_id: str, **kwargs):
        """Modify zone properties"""
        if zone_id in self.zones:
            zone = self.zones[zone_id]
            if 'area_m2' in kwargs:
                zone.area_m2 = kwargs['area_m2']
            if 'capacity' in kwargs:
                zone.capacity = kwargs['capacity']
            if 'name' in kwargs:
                zone.name = kwargs['name']
            if 'position' in kwargs:
                zone.position = kwargs['position']
    
    def to_dict(self) -> Dict:
        """Export scenario as dictionary"""
        return {
            'name': self.name,
            'template': self.template,
            'description': self.description,
            'zones': [zone.to_dict() for zone in self.zones.values()],
            'paths': [
                {
                    'from': path.from_zone,
                    'to': path.to_zone,
                    'width_m': path.width_m,
                    'flow_capacity': path.flow_capacity
                }
                for path in self.paths
            ]
        }
    
    def to_json(self, filepath: str = None) -> str:
        """Export as JSON"""
        json_str = json.dumps(self.to_dict(), indent=2)
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        return json_str
    
    @staticmethod
    def from_dict(data: Dict) -> 'ScenarioBuilder':
        """Import scenario from dictionary"""
        builder = ScenarioBuilder(data['name'], data.get('template'))
        builder.description = data.get('description', '')
        
        for zone_data in data.get('zones', []):
            zone = Zone(
                zone_data['id'],
                zone_data['name'],
                zone_data['type'],
                zone_data['area_m2'],
                tuple(zone_data['position']),
                zone_data.get('capacity')
            )
            builder.add_zone(zone)
        
        for path_data in data.get('paths', []):
            path = Path(
                path_data['from'],
                path_data['to'],
                path_data['width_m'],
                path_data['flow_capacity']
            )
            builder.add_path(path)
        
        return builder


# Pre-built scenarios for real case studies
REAL_CASE_SCENARIOS = {
    'mahakumbh_2024': {
        'name': 'Mahakumbh 2024, Prayagraj',
        'deaths': 121,
        'crowd_size': '80+ million pilgrims',
        'cause': 'Gate malfunction + high density',
        'template': 'temple',
        'historical_factors': [
            'Auspicious time window (limited duration)',
            'Pilgrims attempting to reach sanctum',
            'Single exit path design',
            'Underestimated crowd surge'
        ]
    },
    'mahakumbh_2013': {
        'name': 'Mahakumbh 2013, Allahabad',
        'deaths': 36,
        'crowd_size': '25 million pilgrims',
        'cause': 'Crowd surge at bathing area',
        'template': 'temple',
        'historical_factors': [
            'Similar bottleneck issues',
            'Pilgrims rushing to water',
            'Limited infrastructure'
        ]
    },
    'itaewon_2022': {
        'name': 'Itaewon Stampede, Seoul',
        'deaths': 156,
        'crowd_size': '100k+ people',
        'cause': 'False rumor + high density narrow alley',
        'template': 'rally',
        'historical_factors': [
            'Narrow alley with limited exits',
            'Rumor of overcrowding spread panic',
            'High density on narrow street',
            'Lack of crowd control'
        ]
    },
    'vijay_thalapathy_2024': {
        'name': 'Vijay Thalapathy Rally, Chennai',
        'deaths': 26,
        'crowd_size': '500k+ people',
        'cause': 'Gate closure + panic',
        'template': 'rally',
        'historical_factors': [
            'Unexpected gate closure',
            'Large unsupervised crowd',
            'Limited exit routes',
            'Panic spread quickly'
        ]
    }
}