"""
Recommendation Engine for Algae Cultivation
Provides actionable advice based on sensor readings and algae species
"""

from typing import List, Dict
from database import AlgaeSpecies, SensorReading


class Recommendation:
    """Single recommendation with priority and action"""
    
    def __init__(self, priority: str, category: str, issue: str, action: str, 
                 target: str, severity: str, details: str = ""):
        self.priority = priority  # high, medium, low, info
        self.category = category  # ph, temperature, turbidity, harvest, nutrients
        self.issue = issue
        self.action = action
        self.target = target
        self.severity = severity  # critical, warning, action_required, ok
        self.details = details
    
    def to_dict(self):
        return {
            'priority': self.priority,
            'category': self.category,
            'issue': self.issue,
            'action': self.action,
            'target': self.target,
            'severity': self.severity,
            'details': self.details
        }


class RecommendationEngine:
    """Generate recommendations based on sensor data and species requirements"""
    
    @staticmethod
    def analyze(reading: SensorReading, species: AlgaeSpecies, tank_volume_liters: float = None) -> List[Recommendation]:
        """
        Analyze sensor readings and generate recommendations
        
        Args:
            reading: Latest sensor reading
            species: Algae species information
            tank_volume_liters: Tank volume (optional, for dosing calculations)
        
        Returns:
            List of recommendations sorted by priority
        """
        recommendations = []
        
        # pH Analysis
        recommendations.extend(RecommendationEngine._analyze_ph(reading.ph, species, tank_volume_liters))
        
        # Temperature Analysis
        recommendations.extend(RecommendationEngine._analyze_temperature(reading.temperature_c, species))
        
        # Turbidity/Harvest Analysis
        recommendations.extend(RecommendationEngine._analyze_turbidity(reading.turbidity_ntu, species))
        
        # If all is well
        if not recommendations:
            recommendations.append(Recommendation(
                priority='info',
                category='status',
                issue='All parameters optimal',
                action='Continue normal monitoring',
                target='System running well',
                severity='ok',
                details=f'pH: {reading.ph:.2f}, Temp: {reading.temperature_c:.1f}°C, Turbidity: {reading.turbidity_ntu:.1f} NTU'
            ))
        
        # Sort by severity: critical -> action_required -> warning -> ok
        severity_order = {'critical': 0, 'action_required': 1, 'warning': 2, 'ok': 3}
        recommendations.sort(key=lambda r: severity_order.get(r.severity, 4))
        
        return recommendations
    
    @staticmethod
    def _analyze_ph(ph: float, species: AlgaeSpecies, tank_volume: float = None) -> List[Recommendation]:
        """Analyze pH and provide recommendations"""
        recs = []
        
        if ph < species.ph_min:
            diff = species.ph_min - ph
            severity = 'critical' if diff > 1.0 else 'warning'
            
            # Calculate dosage if tank volume provided
            dosage = ""
            if tank_volume:
                # Rough estimate: 1g sodium bicarbonate per 10L raises pH by ~0.1
                grams_needed = (diff * 10 * tank_volume) / 10
                dosage = f" Add approximately {grams_needed:.1f}g of sodium bicarbonate."
            
            recs.append(Recommendation(
                priority='high',
                category='ph',
                issue=f'pH too low ({ph:.2f}, below {species.ph_min})',
                action=f'Add sodium bicarbonate (baking soda) to raise pH.{dosage}',
                target=f'Target: {species.ph_optimal} (Range: {species.ph_min}-{species.ph_max})',
                severity=severity,
                details=f'Low pH inhibits growth and can stress algae. Dissolve baking soda in water before adding gradually.'
            ))
        
        elif ph > species.ph_max:
            diff = ph - species.ph_max
            severity = 'critical' if diff > 1.0 else 'warning'
            
            dosage = ""
            if tank_volume:
                # Rough: 1ml vinegar per 10L lowers pH by ~0.1
                ml_needed = (diff * 10 * tank_volume) / 10
                dosage = f" Add approximately {ml_needed:.1f}ml of white vinegar."
            
            recs.append(Recommendation(
                priority='high',
                category='ph',
                issue=f'pH too high ({ph:.2f}, above {species.ph_max})',
                action=f'Add citric acid or white vinegar to lower pH.{dosage}',
                target=f'Target: {species.ph_optimal} (Range: {species.ph_min}-{species.ph_max})',
                severity=severity,
                details='High pH can precipitate nutrients. Dilute acid in water and add slowly while monitoring.'
            ))
        
        elif abs(ph - species.ph_optimal) > 0.5:
            # Not critical but not optimal
            if ph < species.ph_optimal:
                recs.append(Recommendation(
                    priority='low',
                    category='ph',
                    issue=f'pH slightly low ({ph:.2f})',
                    action='Consider small pH adjustment for optimal growth',
                    target=f'Optimal: {species.ph_optimal}',
                    severity='ok',
                    details='Growth is okay but could be improved.'
                ))
            else:
                recs.append(Recommendation(
                    priority='low',
                    category='ph',
                    issue=f'pH slightly high ({ph:.2f})',
                    action='Consider small pH adjustment for optimal growth',
                    target=f'Optimal: {species.ph_optimal}',
                    severity='ok',
                    details='Growth is okay but could be improved.'
                ))
        
        return recs
    
    @staticmethod
    def _analyze_temperature(temp_c: float, species: AlgaeSpecies) -> List[Recommendation]:
        """Analyze temperature and provide recommendations"""
        recs = []
        
        if temp_c < species.temp_min_c:
            diff = species.temp_min_c - temp_c
            severity = 'critical' if diff > 5 else 'warning'
            
            recs.append(Recommendation(
                priority='medium',
                category='temperature',
                issue=f'Temperature too low ({temp_c:.1f}°C, below {species.temp_min_c}°C)',
                action='Increase temperature: Add aquarium heater or move to warmer location',
                target=f'Target: {species.temp_optimal_c}°C (Range: {species.temp_min_c}-{species.temp_max_c}°C)',
                severity=severity,
                details=f'Low temperature slows growth rate by ~{diff * 10:.0f}%. Cold stress can inhibit photosynthesis.'
            ))
        
        elif temp_c > species.temp_max_c:
            diff = temp_c - species.temp_max_c
            severity = 'critical' if diff > 5 else 'warning'
            
            recs.append(Recommendation(
                priority='medium',
                category='temperature',
                issue=f'Temperature too high ({temp_c:.1f}°C, above {species.temp_max_c}°C)',
                action='Reduce temperature: Add cooling fan, reduce light, or use chiller',
                target=f'Target: {species.temp_optimal_c}°C (Range: {species.temp_min_c}-{species.temp_max_c}°C)',
                severity=severity,
                details=f'High temperature can kill algae. Risk of culture crash. Reduce immediately.'
            ))
        
        return recs
    
    @staticmethod
    def _analyze_turbidity(turbidity_ntu: float, species: AlgaeSpecies) -> List[Recommendation]:
        """Analyze turbidity and provide harvest recommendations"""
        recs = []
        
        harvest_threshold = species.harvest_turbidity_ntu
        
        if turbidity_ntu >= harvest_threshold:
            recs.append(Recommendation(
                priority='high',
                category='harvest',
                issue=f'Harvest threshold reached ({turbidity_ntu:.1f} NTU)',
                action='Start collection process NOW',
                target=f'Threshold: {harvest_threshold} NTU',
                severity='action_required',
                details='High density reached. Harvest to prevent nutrient depletion and maintain culture health.'
            ))
        
        elif turbidity_ntu >= harvest_threshold * 0.8:
            # Close to harvest
            remaining_ntu = harvest_threshold - turbidity_ntu
            recs.append(Recommendation(
                priority='medium',
                category='harvest',
                issue=f'Approaching harvest ({turbidity_ntu:.1f} NTU)',
                action=f'Prepare for harvest soon. {remaining_ntu:.1f} NTU remaining.',
                target=f'Threshold: {harvest_threshold} NTU',
                severity='ok',
                details=f'Estimated {species.growth_rate_days * 0.2:.1f} days until harvest at current growth rate.'
            ))
        
        elif turbidity_ntu < 50:
            # Very low density - might need nutrients
            recs.append(Recommendation(
                priority='low',
                category='nutrients',
                issue=f'Low algae density ({turbidity_ntu:.1f} NTU)',
                action='Check nutrient levels. Consider adding fertilizer if growth is slow.',
                target='Normal growth expected',
                severity='ok',
                details='Low turbidity is normal after harvest or when starting new culture.'
            ))
        
        return recs
    
    @staticmethod
    def get_action_guide(category: str) -> Dict[str, str]:
        """Get detailed action guides for different categories"""
        guides = {
            'ph_up': {
                'title': 'How to Raise pH',
                'materials': 'Sodium bicarbonate (baking soda), stirring rod, pH meter',
                'steps': [
                    '1. Dissolve 1g baking soda per 10L tank water in separate container',
                    '2. Add slowly while stirring',
                    '3. Wait 15 minutes for pH to stabilize',
                    '4. Measure pH again',
                    '5. Repeat if needed with smaller amounts'
                ],
                'caution': 'Never add powder directly. pH changes take time to stabilize.'
            },
            'ph_down': {
                'title': 'How to Lower pH',
                'materials': 'White vinegar or citric acid, stirring rod, pH meter',
                'steps': [
                    '1. Dilute 1ml vinegar in 10ml water per 10L tank',
                    '2. Add slowly while stirring',
                    '3. Wait 15 minutes for pH to stabilize',
                    '4. Measure pH again',
                    '5. Repeat if needed with smaller amounts'
                ],
                'caution': 'Too much acid can crash pH suddenly. Add in small increments.'
            },
            'temperature': {
                'title': 'Temperature Control',
                'materials': 'Aquarium heater or cooling fan',
                'steps': [
                    'For heating: Use aquarium heater with thermostat',
                    'For cooling: Add cooling fan, reduce lighting hours, use ice packs',
                    'Monitor temperature 2-3 times daily',
                    'Avoid rapid temperature changes (max 2°C per hour)'
                ],
                'caution': 'Sudden temperature changes can shock algae and cause culture crash.'
            },
            'harvest': {
                'title': 'Harvest Procedure',
                'materials': 'Collection pump, filter, clean containers',
                'steps': [
                    '1. Ensure pH and temperature are in safe range',
                    '2. Start collection system',
                    '3. Monitor turbidity during collection',
                    '4. Stop when turbidity drops to 30% of harvest level',
                    '5. Leave remaining culture as seed for next growth cycle'
                ],
                'caution': 'Never harvest complete culture. Leave 20-30% for regrowth.'
            }
        }
        return guides.get(category, {})


if __name__ == "__main__":
    """Test recommendation engine"""
    from database import db
    
    print("Testing Recommendation Engine...\n")
    
    # Mock sensor reading
    class MockReading:
        def __init__(self):
            self.ph = 6.5
            self.temperature_c = 22.0
            self.turbidity_ntu = 250
    
    # Mock species
    class MockSpecies:
        def __init__(self):
            self.name = "Chlorella"
            self.ph_min = 6.0
            self.ph_max = 7.5
            self.ph_optimal = 6.8
            self.temp_min_c = 20
            self.temp_max_c = 30
            self.temp_optimal_c = 25
            self.harvest_turbidity_ntu = 300
            self.growth_rate_days = 5
    
    reading = MockReading()
    species = MockSpecies()
    
    recommendations = RecommendationEngine.analyze(reading, species, tank_volume_liters=100)
    
    print(f"Analyzed {species.name} culture:")
    print(f"pH: {reading.ph}, Temp: {reading.temperature_c}°C, Turbidity: {reading.turbidity_ntu} NTU\n")
    print(f"Generated {len(recommendations)} recommendations:\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec.severity.upper()}] {rec.issue}")
        print(f"   Action: {rec.action}")
        print(f"   Target: {rec.target}")
        if rec.details:
            print(f"   Details: {rec.details}")
        print()
