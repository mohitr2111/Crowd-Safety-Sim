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
    ✅ UPDATED: Enhanced predictor with lower thresholds and trend-based early warning
    """
    
    # ✅ LOWERED: Critical thresholds for earlier warnings
    DENSITY_SAFE = 1.5      # Was 2.0 - Catch issues earlier
    DENSITY_MODERATE = 2.5  # Was 4.0 - Much more sensitive
    DENSITY_HIGH = 3.5      # Was 5.5 - Earlier HIGH alerts
    DENSITY_CRITICAL = 5.0  # Was 7.0 - Align with real danger
    DENSITY_IMMINENT = 6.5  # Was 8.5 - Emergency threshold
    
    FLOW_STOPPED_THRESHOLD = 0.1
    SPEED_CRITICAL = 0.3
    
    # ✅ NEW: Trend-based thresholds
    TREND_RAPID = 0.6       # Density increase rate (p/m²/step)
    TREND_DANGEROUS = 0.8   # Very rapid increase
    
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
            return None
        
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
            'density_trend': np.polyfit(range(len(densities)), densities, 1)[0],
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
        
        first_diff = np.diff(values)
        second_diff = np.diff(first_diff)
        
        return float(np.mean(second_diff))
    
    def _calculate_risk(self, features: Dict, current: DensitySnapshot) -> Tuple[RiskLevel, float]:
        """
        ✅ UPDATED: Enhanced risk calculation with trend-based early warning
        """
        density = features['current_density']
        trend = features['density_trend']
        acceleration = features['density_acceleration']
        flow = features['current_flow']
        speed = features['current_speed']
        
        score = 0.0
        
        # ✅ UPDATED: Density scoring with lower thresholds
        if density >= self.DENSITY_IMMINENT:
            return RiskLevel.IMMINENT, 0.95
        elif density >= self.DENSITY_CRITICAL:
            score += 0.70
        elif density >= self.DENSITY_HIGH:
            score += 0.50
        elif density >= self.DENSITY_MODERATE:
            score += 0.30
        elif density >= self.DENSITY_SAFE:
            score += 0.15
        
        # ✅ ENHANCED: Trend-based scoring (catches rapid increases early)
        if trend > self.TREND_DANGEROUS:  # 0.8+ p/m²/step
            score += 0.30  # Major boost for very rapid increase
        elif trend > self.TREND_RAPID:    # 0.6+ p/m²/step
            score += 0.20  # Significant boost for rapid increase
        elif trend > 0.4:
            score += 0.15
        elif trend > 0.2:
            score += 0.10
        
        # ✅ NEW: Combined density + trend detection (CRITICAL FEATURE)
        # This catches "3.0 p/m² with rapid increase" scenarios
        if density > 2.5 and trend > self.TREND_RAPID:
            score += 0.25  # Big penalty for moderate density + rapid rise
            print(f"⚠️  EARLY WARNING: {current.zone_id} at {density:.1f} p/m² with trend +{trend:.2f}")
        
        # Acceleration scoring
        if acceleration > 0.15:
            score += 0.20
        elif acceleration > 0.10:
            score += 0.15
        elif acceleration > 0.05:
            score += 0.10
        
        # Flow rules (stopped flow = jam)
        if abs(flow) < self.FLOW_STOPPED_THRESHOLD and density > self.DENSITY_MODERATE:
            score += 0.20
        
        # Speed rules (very slow = dangerous jam)
        if speed < self.SPEED_CRITICAL and density > self.DENSITY_MODERATE:
            score += 0.15
        
        # Time spent in danger zone
        if features['time_above_high'] > 5:
            score += 0.15
        elif features['time_above_moderate'] > 8:
            score += 0.10
        
        # Convert score to risk level
        probability = min(score, 1.0)
        
        # ✅ UPDATED: More sensitive risk classification
        if probability >= 0.85:
            risk_level = RiskLevel.IMMINENT
        elif probability >= 0.70:
            risk_level = RiskLevel.CRITICAL
        elif probability >= 0.50:
            risk_level = RiskLevel.HIGH
        elif probability >= 0.30:
            risk_level = RiskLevel.MODERATE
        elif probability >= 0.15:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE
        
        return risk_level, probability
    
    def _predict_time_to_critical(self, features: Dict, current: DensitySnapshot) -> Optional[int]:
        """Predict steps until critical density reached"""
        density = features['current_density']
        trend = features['density_trend']
        
        if density >= self.DENSITY_CRITICAL:
            return 0
        
        if trend <= 0:
            return None
        
        # Linear extrapolation
        steps_to_critical = (self.DENSITY_CRITICAL - density) / trend
        
        if steps_to_critical < 0 or steps_to_critical > 100:
            return None
        
        return int(steps_to_critical)
    
    def _identify_factors(self, features: Dict, current: DensitySnapshot) -> List[str]:
        """✅ UPDATED: Identify contributing risk factors with more granularity"""
        factors = []
        
        density = features['current_density']
        trend = features['density_trend']
        
        # Density factors
        if density > self.DENSITY_CRITICAL:
            factors.append(f"CRITICAL density ({density:.1f} p/m²)")
        elif density > self.DENSITY_HIGH:
            factors.append(f"High density ({density:.1f} p/m²)")
        elif density > self.DENSITY_MODERATE:
            factors.append(f"Moderate density ({density:.1f} p/m²)")
        
        # ✅ NEW: Trend factors (key for early warning)
        if trend > self.TREND_DANGEROUS:
            factors.append(f"⚠️ VERY RAPID increase (+{trend:.2f} p/m²/step)")
        elif trend > self.TREND_RAPID:
            factors.append(f"⚠️ Rapid increase (+{trend:.2f} p/m²/step)")
        elif trend > 0.3:
            factors.append(f"Increasing density (+{trend:.2f} p/m²/step)")
        
        # Acceleration
        if features['density_acceleration'] > 0.1:
            factors.append("Accelerating growth")
        elif features['density_acceleration'] > 0.05:
            factors.append("Steady growth acceleration")
        
        # Flow
        if features['current_flow'] < self.FLOW_STOPPED_THRESHOLD:
            factors.append("Flow blocked/stopped")
        elif features['current_flow'] < 2.0:
            factors.append("Very slow flow")
        
        # Speed
        if features['current_speed'] < self.SPEED_CRITICAL:
            factors.append(f"Very slow movement ({features['current_speed']:.2f} m/s)")
        elif features['current_speed'] < 0.6:
            factors.append(f"Slow movement ({features['current_speed']:.2f} m/s)")
        
        # Duration
        if features['time_above_high'] > 5:
            factors.append(f"Sustained high density ({features['time_above_high']} steps)")
        elif features['time_above_moderate'] > 8:
            factors.append(f"Prolonged moderate density ({features['time_above_moderate']} steps)")
        
        if not factors:
            factors.append("Normal conditions")
        
        return factors
    
    def _generate_recommendations(self, risk_level: RiskLevel, 
                                  factors: List[str], 
                                  current: DensitySnapshot) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if risk_level == RiskLevel.IMMINENT:
            recommendations.append("🚨 IMMEDIATE: Emergency evacuation protocol")
            recommendations.append(f"🚨 Close ALL entries to {current.zone_id}")
            recommendations.append("🚨 Deploy all staff + security NOW")
            recommendations.append("🚨 Activate ALL emergency exits")
            recommendations.append("🚨 Call emergency services")
        
        elif risk_level == RiskLevel.CRITICAL:
            recommendations.append(f"⚠️ URGENT: Stop new entries to {current.zone_id} immediately")
            recommendations.append("⚠️ Open alternative routes/exits NOW")
            recommendations.append("⚠️ Deploy crowd control staff")
            recommendations.append("⚠️ Prepare emergency evacuation")
            recommendations.append("⚠️ Alert adjacent zones")
        
        elif risk_level == RiskLevel.HIGH:
            recommendations.append(f"⚠️ Reduce entry rate to {current.zone_id} by 50%")
            recommendations.append("⚠️ Monitor closely (every 30 seconds)")
            recommendations.append("⚠️ Alert staff in adjacent zones")
            recommendations.append("⚠️ Prepare intervention plan")
        
        elif risk_level == RiskLevel.MODERATE:
            recommendations.append(f"⚠️ Reduce entry rate to {current.zone_id} by 25%")
            recommendations.append(f"Monitor {current.zone_id} every 1 minute")
            recommendations.append("Consider rerouting some crowd flow")
        
        elif risk_level == RiskLevel.LOW:
            recommendations.append(f"Monitor {current.zone_id} periodically")
            recommendations.append("Be ready to adjust flow if needed")
        
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


# ✅ ENHANCED: Test with realistic scenario
if __name__ == "__main__":
    print("🧪 Testing UPDATED Stampede Predictor (Lowered Thresholds)\n")
    print("=" * 70)
    
    predictor = StampedePredictor(history_window=10)
    
    # ✅ NEW TEST: Rapid increase from moderate density (catches early)
    print("\n📊 SCENARIO 1: Rapid increase from 3.0 p/m² (Early Warning Test)\n")
    
    zone_id = "corridor_main"
    
    # Simulate rapid density increase starting from moderate level
    densities = [2.0, 2.3, 2.6, 3.0, 3.8, 4.6, 5.4, 6.2, 7.0, 7.8]
    
    for step, density in enumerate(densities):
        snapshot = DensitySnapshot(
            zone_id=zone_id,
            timestamp=step,
            density=density,
            agent_count=int(density * 50),
            area=50.0,
            flow_rate=max(15 - step * 1.0, 2),  # Decreasing flow
            avg_speed=max(1.0 - step * 0.08, 0.25)  # Decreasing speed
        )
        
        predictor.update_data(snapshot)
        
        # Predict at key density milestones
        if step >= 3:
            prediction = predictor.predict(zone_id)
            
            if prediction:
                print(f"⏱️  Step {step} | Density: {density:.1f} p/m²")
                print(f"   🎯 Risk: {prediction.risk_level.value.upper()} (Probability: {prediction.probability:.0%})")
                print(f"   📊 Confidence: {prediction.confidence:.0%}")
                
                if prediction.time_to_stampede is not None:
                    time_min = prediction.time_to_stampede * 0.5
                    print(f"   ⏰ Critical in: {time_min:.1f} minutes ({prediction.time_to_stampede} steps)")
                
                print(f"   📈 Peak forecast: {prediction.predicted_peak_density:.1f} p/m²")
                print(f"   🔍 Top factors:")
                for factor in prediction.contributing_factors[:3]:
                    print(f"      • {factor}")
                print(f"   💡 PRIMARY ACTION: {prediction.recommendations[0]}")
                print()
    
    print("=" * 70)
    print("✅ Updated Predictor Test Complete")
    print("\n🎯 KEY IMPROVEMENTS:")
    print("   • MODERATE risk now triggers at 2.5 p/m² (was 4.0)")
    print("   • HIGH risk at 3.5 p/m² (was 5.5)")
    print("   • Rapid trend (+0.8) from 3.0 p/m² = HIGH risk")
    print("   • Combined density+trend detection catches danger early")
