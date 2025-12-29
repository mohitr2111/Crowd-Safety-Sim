# backend/ai/stampede_predictor.py

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from collections import deque
from enum import Enum

class RiskLevel(Enum):
    """Risk levels for stampede prediction"""
    SAFE = "safe"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    IMMINENT = "imminent"

@dataclass
class DensitySnapshot:
    """Single moment of density data for a zone"""
    zone_id: str
    timestamp: int  # Simulation step
    density: float  # people/m²
    agent_count: int
    area: float
    flow_rate: float  # agents entering/leaving per step
    avg_speed: float  # m/s

@dataclass
class StampedePrediction:
    """Prediction result"""
    zone_id: str
    risk_level: RiskLevel
    probability: float  # 0-1
    time_to_stampede: Optional[int]  # steps until stampede (None if safe)
    confidence: float  # 0-1
    contributing_factors: List[str]
    recommendations: List[str]
    current_density: float
    predicted_peak_density: float

class StampedePredictor:
    """
    Predicts stampede risk using rule-based + statistical analysis
    """
    
    # Critical thresholds (based on real research)
    DENSITY_SAFE = 2.0  # p/m²
    DENSITY_MODERATE = 4.0
    DENSITY_HIGH = 5.5
    DENSITY_CRITICAL = 7.0
    DENSITY_IMMINENT = 8.5
    
    FLOW_STOPPED_THRESHOLD = 0.1  # agents/step
    SPEED_CRITICAL = 0.3  # m/s (very slow = jam)
    
    def __init__(self, history_window: int = 10):
        """
        Args:
            history_window: Number of past steps to analyze for trends
        """
        self.history_window = history_window
        self.density_history: Dict[str, deque] = {}
        self.predictions_history: List[StampedePrediction] = []
    
    def update_data(self, snapshot: DensitySnapshot):
        """Add new density data for a zone"""
        zone_id = snapshot.zone_id
        
        if zone_id not in self.density_history:
            self.density_history[zone_id] = deque(maxlen=self.history_window)
        
        self.density_history[zone_id].append(snapshot)
    
    def predict(self, zone_id: str) -> Optional[StampedePrediction]:
        """
        Predict stampede risk for a specific zone
        Returns None if insufficient data
        """
        if zone_id not in self.density_history:
            return None
        
        history = list(self.density_history[zone_id])
        
        if len(history) < 3:
            return None  # Need at least 3 data points
        
        current = history[-1]
        
        # Feature extraction
        features = self._extract_features(history)
        
        # Rule-based prediction
        risk_level, probability = self._calculate_risk(features, current)
        
        # Time prediction
        time_to_stampede = self._predict_time_to_critical(features, current)
        
        # Contributing factors
        factors = self._identify_factors(features, current)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, factors, current)
        
        # Confidence calculation
        confidence = self._calculate_confidence(len(history), features)
        
        # Predict peak density
        predicted_peak = self._predict_peak_density(features, current)
        
        prediction = StampedePrediction(
            zone_id=zone_id,
            risk_level=risk_level,
            probability=probability,
            time_to_stampede=time_to_stampede,
            confidence=confidence,
            contributing_factors=factors,
            recommendations=recommendations,
            current_density=current.density,
            predicted_peak_density=predicted_peak
        )
        
        self.predictions_history.append(prediction)
        return prediction
    
    def _extract_features(self, history: List[DensitySnapshot]) -> Dict:
        """Extract features from density history"""
        densities = [s.density for s in history]
        flows = [s.flow_rate for s in history]
        speeds = [s.avg_speed for s in history]
        
        return {
            'current_density': densities[-1],
            'density_trend': np.polyfit(range(len(densities)), densities, 1)[0],  # Linear slope
            'density_acceleration': self._calculate_acceleration(densities),
            'avg_density': np.mean(densities),
            'max_density': np.max(densities),
            'density_variance': np.var(densities),
            
            'current_flow': flows[-1],
            'flow_trend': np.polyfit(range(len(flows)), flows, 1)[0],
            'avg_flow': np.mean(flows),
            
            'current_speed': speeds[-1],
            'speed_trend': np.polyfit(range(len(speeds)), speeds, 1)[0],
            'avg_speed': np.mean(speeds),
            
            'time_above_moderate': sum(1 for d in densities if d > self.DENSITY_MODERATE),
            'time_above_high': sum(1 for d in densities if d > self.DENSITY_HIGH),
        }
    
    def _calculate_acceleration(self, values: List[float]) -> float:
        """Calculate second derivative (acceleration of change)"""
        if len(values) < 3:
            return 0.0
        
        # Calculate differences
        first_diff = np.diff(values)
        second_diff = np.diff(first_diff)
        
        return float(np.mean(second_diff))
    
    def _calculate_risk(self, features: Dict, current: DensitySnapshot) -> Tuple[RiskLevel, float]:
        """Calculate risk level and probability using rules"""
        density = features['current_density']
        trend = features['density_trend']
        acceleration = features['density_acceleration']
        flow = features['current_flow']
        speed = features['current_speed']
        
        # Rule-based classification
        score = 0.0
        
        # Density rules
        if density >= self.DENSITY_IMMINENT:
            return RiskLevel.IMMINENT, 0.95
        elif density >= self.DENSITY_CRITICAL:
            score += 0.7
        elif density >= self.DENSITY_HIGH:
            score += 0.5
        elif density >= self.DENSITY_MODERATE:
            score += 0.3
        
        # Trend rules (increasing density is dangerous)
        if trend > 0.5:  # Rapidly increasing
            score += 0.2
        elif trend > 0.2:
            score += 0.1
        
        # Acceleration rules (accelerating increase is very dangerous)
        if acceleration > 0.1:
            score += 0.15
        
        # Flow rules (stopped flow = jam)
        if abs(flow) < self.FLOW_STOPPED_THRESHOLD and density > self.DENSITY_MODERATE:
            score += 0.2
        
        # Speed rules (very slow = dangerous jam)
        if speed < self.SPEED_CRITICAL and density > self.DENSITY_MODERATE:
            score += 0.15
        
        # Time spent in danger zone
        if features['time_above_high'] > 5:
            score += 0.1
        
        # Convert score to risk level
        probability = min(score, 1.0)
        
        if probability >= 0.85:
            risk_level = RiskLevel.CRITICAL
        elif probability >= 0.65:
            risk_level = RiskLevel.HIGH
        elif probability >= 0.45:
            risk_level = RiskLevel.MODERATE
        elif probability >= 0.25:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE
        
        return risk_level, probability
    
    def _predict_time_to_critical(self, features: Dict, current: DensitySnapshot) -> Optional[int]:
        """Predict steps until critical density reached"""
        density = features['current_density']
        trend = features['density_trend']
        
        if density >= self.DENSITY_CRITICAL:
            return 0  # Already critical
        
        if trend <= 0:
            return None  # Density not increasing
        
        # Linear extrapolation
        steps_to_critical = (self.DENSITY_CRITICAL - density) / trend
        
        if steps_to_critical < 0 or steps_to_critical > 100:
            return None
        
        return int(steps_to_critical)
    
    def _identify_factors(self, features: Dict, current: DensitySnapshot) -> List[str]:
        """Identify contributing risk factors"""
        factors = []
        
        if features['current_density'] > self.DENSITY_HIGH:
            factors.append(f"High density ({features['current_density']:.1f} p/m²)")
        
        if features['density_trend'] > 0.2:
            factors.append(f"Rapidly increasing density (+{features['density_trend']:.2f} p/m²/step)")
        
        if features['density_acceleration'] > 0.05:
            factors.append("Accelerating density growth")
        
        if features['current_flow'] < self.FLOW_STOPPED_THRESHOLD:
            factors.append("Flow blocked/stopped")
        
        if features['current_speed'] < self.SPEED_CRITICAL:
            factors.append(f"Very slow movement ({features['current_speed']:.2f} m/s)")
        
        if features['time_above_high'] > 5:
            factors.append(f"Sustained high density ({features['time_above_high']} steps)")
        
        if not factors:
            factors.append("Normal conditions")
        
        return factors
    
    def _generate_recommendations(self, risk_level: RiskLevel, 
                                  factors: List[str], 
                                  current: DensitySnapshot) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if risk_level == RiskLevel.IMMINENT:
            recommendations.append("🚨 IMMEDIATE ACTION: Emergency evacuation protocol")
            recommendations.append(f"🚨 Close all entries to {current.zone_id}")
            recommendations.append("🚨 Deploy all available staff immediately")
            recommendations.append("🚨 Activate emergency exits")
        
        elif risk_level == RiskLevel.CRITICAL:
            recommendations.append(f"⚠️ URGENT: Stop new entries to {current.zone_id}")
            recommendations.append("⚠️ Open alternative routes/exits")
            recommendations.append("⚠️ Deploy crowd control staff")
            recommendations.append("⚠️ Prepare emergency response")
        
        elif risk_level == RiskLevel.HIGH:
            recommendations.append(f"⚠️ Reduce entry rate to {current.zone_id}")
            recommendations.append("⚠️ Monitor closely (check every 30 seconds)")
            recommendations.append("⚠️ Alert staff in adjacent zones")
        
        elif risk_level == RiskLevel.MODERATE:
            recommendations.append(f"Monitor {current.zone_id} for changes")
            recommendations.append("Consider rerouting some crowd flow")
        
        else:
            recommendations.append("Continue normal operations")
        
        return recommendations
    
    def _calculate_confidence(self, data_points: int, features: Dict) -> float:
        """Calculate prediction confidence"""
        # More data = higher confidence
        data_confidence = min(data_points / self.history_window, 1.0)
        
        # Clear trends = higher confidence
        trend_strength = abs(features['density_trend'])
        trend_confidence = min(trend_strength / 0.5, 1.0)
        
        # Low variance = higher confidence
        variance_confidence = 1.0 - min(features['density_variance'] / 10.0, 1.0)
        
        return (data_confidence * 0.4 + trend_confidence * 0.3 + variance_confidence * 0.3)
    
    def _predict_peak_density(self, features: Dict, current: DensitySnapshot) -> float:
        """Predict peak density in next 10 steps"""
        trend = features['density_trend']
        acceleration = features['density_acceleration']
        
        # Quadratic extrapolation
        predicted = (features['current_density'] + 
                    trend * 10 + 
                    acceleration * 10 * 10 / 2)
        
        return max(predicted, features['current_density'])
    
    def get_all_predictions(self) -> Dict[str, StampedePrediction]:
        """Get latest prediction for each zone"""
        predictions = {}
        for zone_id in self.density_history.keys():
            pred = self.predict(zone_id)
            if pred:
                predictions[zone_id] = pred
        return predictions

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Stampede Predictor\n")
    print("=" * 60)
    
    predictor = StampedePredictor(history_window=10)
    
    # Simulate a dangerous scenario: Density building up in corridor
    print("\n📊 SCENARIO: Corridor density building up over time\n")
    
    zone_id = "corridor_s"
    
    # Simulate 15 steps with increasing density
    densities = [2.0, 2.5, 3.2, 4.0, 4.8, 5.5, 6.2, 6.8, 7.3, 7.8, 8.2, 8.5, 8.8, 9.0, 9.2]
    
    for step, density in enumerate(densities):
        snapshot = DensitySnapshot(
            zone_id=zone_id,
            timestamp=step,
            density=density,
            agent_count=int(density * 50),  # Assume 50 m² area
            area=50.0,
            flow_rate=max(10 - step * 0.5, 0),  # Decreasing flow
            avg_speed=max(1.0 - step * 0.05, 0.2)  # Decreasing speed
        )
        
        predictor.update_data(snapshot)
        
        # Predict every 3 steps
        if step % 3 == 0 and step > 0:
            prediction = predictor.predict(zone_id)
            
            if prediction:
                print(f"⏱️  Step {step} (Density: {density:.1f} p/m²)")
                print(f"   Risk: {prediction.risk_level.value.upper()} ({prediction.probability:.0%})")
                print(f"   Confidence: {prediction.confidence:.0%}")
                
                if prediction.time_to_stampede is not None:
                    time_min = prediction.time_to_stampede * 0.5  # 30s/step = 0.5 min
                    print(f"   ⏰ Time to critical: {time_min:.1f} minutes")
                
                print(f"   📈 Peak density forecast: {prediction.predicted_peak_density:.1f} p/m²")
                print(f"   🔍 Factors: {', '.join(prediction.contributing_factors[:2])}")
                print(f"   💡 Action: {prediction.recommendations[0]}")
                print()
    
    print("=" * 60)
    print("✅ Stampede Predictor Test Complete")
