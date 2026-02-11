import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from datetime import datetime, timedelta
import json
import math
from typing import Dict, List, Tuple, Optional
import requests
from dataclasses import dataclass
import hashlib
import time as pytime

# ========== WEATHER API INTEGRATION ==========
class WeatherAPI:
    """Integrate real-time weather data from OpenWeatherMap"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "demo_key_123456"  # In production, use real API key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
        # Weather effect multipliers
        self.weather_effects = {
            'clear': {'speed_mult': 1.0, 'safety_gap_mult': 1.0, 'color': '☀️'},
            'clouds': {'speed_mult': 0.95, 'safety_gap_mult': 1.1, 'color': '☁️'},
            'rain': {'speed_mult': 0.8, 'safety_gap_mult': 1.3, 'color': '🌧️'},
            'thunderstorm': {'speed_mult': 0.6, 'safety_gap_mult': 1.5, 'color': '⛈️'},
            'snow': {'speed_mult': 0.7, 'safety_gap_mult': 1.4, 'color': '❄️'},
            'fog': {'speed_mult': 0.6, 'safety_gap_mult': 1.6, 'color': '🌫️'},
            'mist': {'speed_mult': 0.8, 'safety_gap_mult': 1.2, 'color': '🌁'}
        }
    
    def get_weather_at_location(self, lat, lon):
        """Get weather data for specific coordinates"""
        cache_key = f"{lat:.2f}_{lon:.2f}_{datetime.now().hour}"
        
        # Check cache
        if cache_key in self.cache:
            cached_time, data = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_duration:
                return data
        
        try:
            # Simulate API call (in production, use real API)
            weather_types = ['clear', 'clouds', 'rain', 'thunderstorm', 'snow', 'fog', 'mist']
            weather = random.choice(weather_types)
            
            # Add some realism - rain more likely in certain areas
            if 8.0 < lat < 13.0 and 77.0 < lon < 80.0:  # Tamil Nadu area
                if random.random() < 0.3:
                    weather = 'rain'
            
            data = {
                'weather': weather,
                'temperature': random.uniform(20, 35),
                'humidity': random.uniform(40, 90),
                'wind_speed': random.uniform(5, 25),
                'visibility': random.uniform(1, 10),
                'effects': self.weather_effects.get(weather, self.weather_effects['clear'])
            }
            
            # Cache the result
            self.cache[cache_key] = (datetime.now(), data)
            return data
            
        except Exception as e:
            print(f"⚠️ Weather API error: {e}")
            return {
                'weather': 'clear',
                'temperature': 30,
                'humidity': 50,
                'wind_speed': 10,
                'visibility': 10,
                'effects': self.weather_effects['clear']
            }
    
    def get_weather_alert(self, weather_data):
        """Generate weather alerts based on conditions"""
        alerts = []
        
        if weather_data['weather'] in ['thunderstorm', 'heavy_rain']:
            alerts.append({
                'type': 'severe_weather',
                'severity': 'high',
                'message': f"Severe {weather_data['weather']} detected",
                'recommendation': 'Reduce speed by 40% and increase safety gap'
            })
        
        if weather_data['visibility'] < 2:
            alerts.append({
                'type': 'low_visibility',
                'severity': 'medium',
                'message': f"Low visibility ({weather_data['visibility']:.1f} km)",
                'recommendation': 'Reduce speed by 30% and increase safety gap'
            })
        
        if weather_data['wind_speed'] > 20:
            alerts.append({
                'type': 'high_wind',
                'severity': 'medium',
                'message': f"High wind speed ({weather_data['wind_speed']:.1f} km/h)",
                'recommendation': 'Reduce speed by 20%'
            })
        
        return alerts

# ========== PREDICTIVE MAINTENANCE SYSTEM ==========
@dataclass
class MaintenanceSensor:
    """Simulate train maintenance sensors"""
    train_id: int
    engine_temp: float = 85.0  # Normal: 80-90°C
    vibration_level: float = 2.5  # Normal: 1.0-3.0 mm/s
    oil_pressure: float = 45.0  # Normal: 40-50 psi
    brake_wear: float = 10.0  # Normal: 0-20% wear
    last_maintenance: datetime = None
    
    def __post_init__(self):
        if self.last_maintenance is None:
            self.last_maintenance = datetime.now() - timedelta(days=random.randint(1, 30))
    
    def update(self, speed, acceleration, time_delta=1.0):
        """Update sensor readings based on train operation"""
        # Engine temperature increases with speed
        temp_increase = (speed / 100) * 0.5 + abs(acceleration) * 0.2
        self.engine_temp += temp_increase * time_delta
        self.engine_temp = max(70, min(120, self.engine_temp))
        
        # Vibration increases with speed and poor track
        vibration_increase = (speed / 100) * 0.1 + abs(acceleration) * 0.05
        self.vibration_level += vibration_increase * time_delta
        self.vibration_level = max(1.0, min(10.0, self.vibration_level))
        
        # Oil pressure decreases slightly over time
        self.oil_pressure -= 0.01 * time_delta
        self.oil_pressure = max(20, min(50, self.oil_pressure))
        
        # Brake wear increases with deceleration
        if acceleration < 0:
            self.brake_wear += abs(acceleration) * 0.05 * time_delta
        
        # Natural degradation
        days_since_maintenance = (datetime.now() - self.last_maintenance).days
        degradation = days_since_maintenance * 0.01
        self.vibration_level += degradation
        self.oil_pressure -= degradation
    
    def get_health_score(self):
        """Calculate overall health score (0-100)"""
        scores = []
        
        # Engine temperature score
        if 80 <= self.engine_temp <= 90:
            scores.append(100)
        elif 70 <= self.engine_temp < 80 or 90 < self.engine_temp <= 100:
            scores.append(70)
        else:
            scores.append(30)
        
        # Vibration score
        if self.vibration_level <= 3.0:
            scores.append(100)
        elif 3.0 < self.vibration_level <= 5.0:
            scores.append(60)
        else:
            scores.append(20)
        
        # Oil pressure score
        if 40 <= self.oil_pressure <= 50:
            scores.append(100)
        elif 30 <= self.oil_pressure < 40 or 50 < self.oil_pressure <= 55:
            scores.append(70)
        else:
            scores.append(30)
        
        # Brake wear score
        if self.brake_wear <= 20:
            scores.append(100)
        elif 20 < self.brake_wear <= 40:
            scores.append(60)
        else:
            scores.append(20)
        
        return np.mean(scores)
    
    def check_maintenance_needed(self):
        """Check if maintenance is needed and generate alerts"""
        alerts = []
        
        if self.engine_temp > 100:
            alerts.append({
                'type': 'high_temperature',
                'severity': 'high',
                'component': 'engine',
                'value': self.engine_temp,
                'threshold': 100,
                'message': f"Engine temperature critically high: {self.engine_temp:.1f}°C",
                'recommendation': 'Immediate inspection required'
            })
        
        if self.vibration_level > 5.0:
            alerts.append({
                'type': 'high_vibration',
                'severity': 'medium',
                'component': 'bogies',
                'value': self.vibration_level,
                'threshold': 5.0,
                'message': f"High vibration detected: {self.vibration_level:.1f} mm/s",
                'recommendation': 'Inspect at next major station'
            })
        
        if self.oil_pressure < 30:
            alerts.append({
                'type': 'low_oil_pressure',
                'severity': 'high',
                'component': 'engine',
                'value': self.oil_pressure,
                'threshold': 30,
                'message': f"Low oil pressure: {self.oil_pressure:.1f} psi",
                'recommendation': 'Immediate attention required'
            })
        
        if self.brake_wear > 40:
            alerts.append({
                'type': 'brake_wear',
                'severity': 'medium',
                'component': 'brakes',
                'value': self.brake_wear,
                'threshold': 40,
                'message': f"Brake wear at {self.brake_wear:.1f}%",
                'recommendation': 'Replace brakes at next maintenance stop'
            })
        
        # Days since maintenance
        days_since = (datetime.now() - self.last_maintenance).days
        if days_since > 30:
            alerts.append({
                'type': 'scheduled_maintenance',
                'severity': 'low',
                'component': 'general',
                'value': days_since,
                'threshold': 30,
                'message': f"Scheduled maintenance overdue by {days_since - 30} days",
                'recommendation': 'Schedule maintenance at next opportunity'
            })
        
        return alerts
    
    def perform_maintenance(self, maintenance_type='minor'):
        """Perform maintenance and reset sensors"""
        if maintenance_type == 'major':
            self.engine_temp = 85.0
            self.vibration_level = 2.0
            self.oil_pressure = 45.0
            self.brake_wear = 5.0
        else:  # minor
            self.engine_temp = max(80, self.engine_temp - 5)
            self.vibration_level = max(2.0, self.vibration_level - 1.0)
            self.oil_pressure = min(45, self.oil_pressure + 5)
            self.brake_wear = max(0, self.brake_wear - 10)
        
        self.last_maintenance = datetime.now()

# ========== ENERGY EFFICIENCY OPTIMIZER ==========
class EnergyOptimizer:
    """Optimize energy consumption while maintaining throughput"""
    
    def __init__(self):
        # Energy consumption parameters (kWh/km)
        self.base_consumption = 15.0  # Base energy per km at optimal speed
        self.acceleration_cost = 2.0  # Additional energy per m/s² acceleration
        self.regeneration_efficiency = 0.7  # Energy recovery from braking
        self.ideal_speed = 80.0  # Most energy-efficient speed (km/h)
        
        # Historical data for optimization
        self.energy_history = []
        self.speed_history = []
        self.efficiency_scores = []
    
    def calculate_energy_consumption(self, speed_kmh, acceleration_ms2, distance_km):
        """Calculate energy consumption for given parameters"""
        # Base consumption increases with speed^2 (air resistance)
        speed_factor = (speed_kmh / self.ideal_speed) ** 2
        
        # Acceleration energy
        accel_energy = abs(acceleration_ms2) * self.acceleration_cost
        
        # Total energy for distance
        energy = (self.base_consumption * speed_factor + accel_energy) * distance_km
        
        # Regeneration from braking
        if acceleration_ms2 < 0:
            regen_energy = abs(acceleration_ms2) * self.regeneration_efficiency
            energy = max(0, energy - regen_energy)
        
        return energy
    
    def get_optimal_speed_profile(self, current_speed, target_speed, distance_remaining):
        """Calculate most energy-efficient speed profile"""
        # Simple algorithm: accelerate/decelerate gradually
        if current_speed < target_speed:
            # Accelerate gradually
            optimal_accel = min(1.0, (target_speed - current_speed) / 10)
        elif current_speed > target_speed:
            # Decelerate gradually (allow regeneration)
            optimal_accel = max(-1.0, (target_speed - current_speed) / 10)
        else:
            optimal_accel = 0
        
        # Adjust based on distance remaining
        if distance_remaining < 1000:  # Less than 1km
            optimal_accel = max(optimal_accel, -1.5)  # More aggressive slowing
        
        return {
            'target_speed': target_speed,
            'optimal_acceleration': optimal_accel,
            'estimated_energy': self.calculate_energy_consumption(
                target_speed, optimal_accel, distance_remaining/1000
            ),
            'efficiency_score': self.calculate_efficiency_score(target_speed, optimal_accel)
        }
    
    def calculate_efficiency_score(self, speed, acceleration):
        """Calculate energy efficiency score (0-100)"""
        # Ideal: speed near 80 km/h, minimal acceleration
        speed_score = 100 - abs(speed - self.ideal_speed)
        accel_score = 100 - abs(acceleration) * 20
        
        # Combine scores
        efficiency = (speed_score * 0.7 + accel_score * 0.3)
        return max(0, min(100, efficiency))
    
    def record_energy_data(self, speed, acceleration, energy_used):
        """Record energy data for learning"""
        self.speed_history.append(speed)
        self.energy_history.append(energy_used)
        efficiency = self.calculate_efficiency_score(speed, acceleration)
        self.efficiency_scores.append(efficiency)
        
        # Keep history manageable
        if len(self.energy_history) > 1000:
            self.energy_history.pop(0)
            self.speed_history.pop(0)
            self.efficiency_scores.pop(0)
    
    def get_energy_report(self):
        """Generate energy efficiency report"""
        if not self.energy_history:
            return None
        
        avg_efficiency = np.mean(self.efficiency_scores) if self.efficiency_scores else 0
        total_energy = np.sum(self.energy_history) if self.energy_history else 0
        
        return {
            'average_efficiency': avg_efficiency,
            'total_energy_consumed': total_energy,
            'energy_per_km': total_energy / max(1, len(self.energy_history)),
            'recommendations': self.generate_energy_recommendations()
        }
    
    def generate_energy_recommendations(self):
        """Generate energy-saving recommendations"""
        recommendations = []
        
        avg_speed = np.mean(self.speed_history) if self.speed_history else 0
        
        if avg_speed > self.ideal_speed * 1.2:
            recommendations.append(f"Reduce average speed from {avg_speed:.1f} to {self.ideal_speed:.1f} km/h for better efficiency")
        
        # Check for aggressive acceleration patterns
        if len(self.speed_history) > 10:
            speed_changes = np.diff(self.speed_history[-10:])
            if np.max(np.abs(speed_changes)) > 15:
                recommendations.append("Reduce aggressive acceleration/deceleration")
        
        if avg_speed < self.ideal_speed * 0.8:
            recommendations.append(f"Increase average speed from {avg_speed:.1f} to {self.ideal_speed:.1f} km/h for optimal efficiency")
        
        return recommendations

# ========== PASSENGER INFORMATION SYSTEM ==========
class PassengerInformationSystem:
    """Provide real-time passenger information and predictions"""
    
    def __init__(self):
        self.predictions = {}
        self.passenger_counts = {}
        self.arrival_history = {}
        self.prediction_accuracy = []
    
    def predict_arrival_time(self, train_id, current_position, current_speed, 
                           route, stations, weather_factor=1.0):
        """Predict precise arrival time at next station"""
        if not route or len(route) < 2:
            return None
        
        # Find next station
        next_station = None
        station_distance = 0
        for i, station_code in enumerate(route):
            if station_code in stations:
                station_pos = stations[station_code]['position'] if 'position' in stations[station_code] else i * 100
                if station_pos > current_position:
                    next_station = station_code
                    station_distance = station_pos - current_position
                    break
        
        if not next_station:
            return None
        
        # Calculate time considering various factors
        base_time = station_distance / max(1, current_speed)  # seconds
        
        # Adjust for weather
        weather_adjusted_time = base_time * weather_factor
        
        # Add buffer for safety and operations
        buffer_time = 120  # 2 minutes buffer
        
        total_seconds = weather_adjusted_time + buffer_time
        
        # Predict arrival time
        arrival_time = datetime.now() + timedelta(seconds=total_seconds)
        
        # Store prediction
        prediction_id = f"{train_id}_{next_station}"
        self.predictions[prediction_id] = {
            'train_id': train_id,
            'station': next_station,
            'predicted_arrival': arrival_time,
            'prediction_time': datetime.now(),
            'estimated_delay': buffer_time,
            'confidence': self.calculate_confidence(current_speed, station_distance)
        }
        
        return self.predictions[prediction_id]
    
    def calculate_confidence(self, speed, distance):
        """Calculate prediction confidence (0-100)"""
        if distance == 0:
            return 100
        
        # More confidence for shorter distances and stable speeds
        distance_factor = min(100, 100 - (distance / 1000))
        speed_factor = 100 - abs(speed - 80)  # 80 km/h is typical
        
        confidence = (distance_factor * 0.6 + speed_factor * 0.4)
        return max(0, min(100, confidence))
    
    def update_actual_arrival(self, train_id, station, actual_arrival):
        """Update with actual arrival time to improve predictions"""
        prediction_id = f"{train_id}_{station}"
        
        if prediction_id in self.predictions:
            prediction = self.predictions[prediction_id]
            predicted_time = prediction['predicted_arrival']
            
            # Calculate accuracy
            time_diff = abs((actual_arrival - predicted_time).total_seconds())
            accuracy = max(0, 100 - (time_diff / 60))  # 1 minute error = 1% accuracy loss
            
            self.prediction_accuracy.append(accuracy)
            
            # Store in history
            history_key = f"{train_id}_{station[:3]}"
            if history_key not in self.arrival_history:
                self.arrival_history[history_key] = []
            
            self.arrival_history[history_key].append({
                'predicted': predicted_time,
                'actual': actual_arrival,
                'accuracy': accuracy
            })
            
            # Keep history manageable
            if len(self.prediction_accuracy) > 1000:
                self.prediction_accuracy.pop(0)
    
    def get_passenger_alerts(self, train_id, delay_minutes, next_station):
        """Generate passenger alerts"""
        alerts = []
        
        if delay_minutes > 15:
            alerts.append({
                'type': 'delay_alert',
                'severity': 'high' if delay_minutes > 30 else 'medium',
                'message': f"Train {train_id} delayed by {delay_minutes} minutes",
                'station': next_station,
                'recommended_action': 'Consider alternative transport if urgent'
            })
        
        # Platform change alerts (simulated)
        if random.random() < 0.05:
            alerts.append({
                'type': 'platform_change',
                'severity': 'low',
                'message': f"Platform changed for Train {train_id}",
                'new_platform': random.choice(['1A', '2B', '3C']),
                'station': next_station
            })
        
        return alerts
    
    def get_prediction_report(self):
        """Get prediction accuracy report"""
        if not self.prediction_accuracy:
            return {'average_accuracy': 0, 'total_predictions': 0}
        
        avg_accuracy = np.mean(self.prediction_accuracy)
        total_predictions = len(self.prediction_accuracy)
        
        accuracy_band = ''
        if avg_accuracy >= 95:
            accuracy_band = 'Excellent'
        elif avg_accuracy >= 90:
            accuracy_band = 'Good'
        elif avg_accuracy >= 80:
            accuracy_band = 'Fair'
        else:
            accuracy_band = 'Needs Improvement'
        
        return {
            'average_accuracy': avg_accuracy,
            'accuracy_band': accuracy_band,
            'total_predictions': total_predictions,
            'recent_accuracy': np.mean(self.prediction_accuracy[-10:]) if len(self.prediction_accuracy) >= 10 else avg_accuracy
        }

# ========== ENHANCED RAILWAY ENVIRONMENT ==========
class EnhancedRailwayEnv(gym.Env):
    """Enhanced railway environment with all new features"""
    
    metadata = {'render.modes': ['human', 'rgb_array']}
    
    def __init__(self, route_length=2000, num_stations=8, num_trains=10):
        super(EnhancedRailwayEnv, self).__init__()
        
        # Action space: 0=Emergency Stop, 1=Decelerate, 2=Maintain, 3=Accelerate, 4=Full Speed
        self.action_space = spaces.Discrete(5)
        
        # Enhanced observation space with all features
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([route_length, 40, 500, 1, 1, 1, 100, 1, 10, 3, 1, 100, 100, 100], dtype=np.float32),
            dtype=np.float32
        )
        
        # Environment parameters
        self.route_length = route_length
        self.num_stations = num_stations
        self.num_trains = num_trains
        
        # Initialize new systems
        self.weather_api = WeatherAPI()
        self.energy_optimizer = EnergyOptimizer()
        self.passenger_system = PassengerInformationSystem()
        
        # Throughput tracking
        self.trains_completed = 0
        self.total_delay = 0
        self.total_energy = 0
        self.total_collisions = 0
        self.start_time = datetime.now()
        
        # Indian railway stations with coordinates
        self.stations = self._load_indian_stations()
        self.station_positions = np.linspace(0, route_length, num_stations + 1)[1:]
        
        # Assign positions to stations
        for i, (code, station) in enumerate(self.stations.items()):
            if i < len(self.station_positions):
                station['position'] = self.station_positions[i]
        
        # Multiple trains with maintenance sensors
        self.trains = []
        self.current_train_idx = 0
        self.maintenance_sensors = {}
        
        # Track conditions
        self.track_conditions = {
            0: {'name': 'Excellent', 'effect': 1.0, 'color': '🟢'},
            1: {'name': 'Good', 'effect': 0.9, 'color': '🟡'},
            2: {'name': 'Fair', 'effect': 0.7, 'color': '🟠'},
            3: {'name': 'Poor', 'effect': 0.5, 'color': '🔴'}
        }
        
        # Signals and blocks for section control
        self.sections = self._create_sections()
        self.signals = {section: 'GREEN' for section in self.sections}
        self.section_occupancy = {i: 0 for i in range(len(self.sections))}
        
        # Throughput optimization parameters
        self.target_headway = 5  # minutes between trains
        self.max_section_capacity = 2  # max trains per section
        self.throughput_target = 25  # trains per hour target
        
        # Communication buffer for multi-agent
        self.communication_messages = []
        
        # Initialize
        self.reset()
    
    def _load_indian_stations(self):
        """Load Indian railway stations"""
        return {
            'MAS': {'name': 'Chennai Central', 'lat': 13.0827, 'lon': 80.2707, 'importance': 10},
            'AJJ': {'name': 'Arakkonam Junction', 'lat': 13.0846, 'lon': 79.6725, 'importance': 8},
            'KPD': {'name': 'Katpadi Junction', 'lat': 12.9702, 'lon': 79.1590, 'importance': 8},
            'JTJ': {'name': 'Jolarpettai Junction', 'lat': 12.5667, 'lon': 78.5667, 'importance': 7},
            'SA': {'name': 'Salem Junction', 'lat': 11.6643, 'lon': 78.1460, 'importance': 8},
            'ED': {'name': 'Erode Junction', 'lat': 11.3420, 'lon': 77.7172, 'importance': 7},
            'TUP': {'name': 'Tiruppur', 'lat': 11.1075, 'lon': 77.3398, 'importance': 6},
            'CBE': {'name': 'Coimbatore Junction', 'lat': 11.0168, 'lon': 76.9558, 'importance': 9}
        }
    
    def _create_sections(self):
        """Create railway sections for throughput control"""
        section_length = self.route_length / 10
        return [(i * section_length, (i + 1) * section_length) for i in range(10)]
    
    def _get_current_section(self, position):
        """Get current railway section"""
        for idx, (start, end) in enumerate(self.sections):
            if start <= position < end:
                return idx
        return len(self.sections) - 1
    
    def _update_signals_and_occupancy(self):
        """Update signal status and section occupancy based on train positions"""
        self.signals = {section: 'GREEN' for section in range(len(self.sections))}
        
        section_counts = {i: 0 for i in range(len(self.sections))}
        
        for train in self.trains:
            section_idx = self._get_current_section(train['position'])
            section_counts[section_idx] += 1
            
            if section_counts[section_idx] >= self.max_section_capacity:
                self.signals[section_idx] = 'RED'
            elif section_counts[section_idx] >= self.max_section_capacity - 1:
                self.signals[section_idx] = 'YELLOW'
            
            for ahead in range(1, 3):
                if section_idx + ahead < len(self.sections):
                    if self.signals[section_idx + ahead] == 'GREEN':
                        self.signals[section_idx + ahead] = 'YELLOW'
        
        self.section_occupancy = section_counts
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Reset tracking
        self.trains_completed = 0
        self.total_delay = 0
        self.total_energy = 0
        self.total_collisions = 0
        self.start_time = datetime.now()
        self.communication_messages = []
        
        # Initialize multiple trains with sensors
        self.trains = []
        self.maintenance_sensors = {}
        
        for i in range(self.num_trains):
            # Create maintenance sensor for each train
            sensor = MaintenanceSensor(train_id=i+1)
            self.maintenance_sensors[i] = sensor
            
            train = {
                'id': i + 1,
                'position': i * 100,  # Staggered start
                'speed': random.uniform(15, 25),
                'acceleration': 0,
                'distance_to_next': random.uniform(100, 300),
                'time_pressure': random.uniform(0, 0.3),
                'weather': self._get_weather_at_position(i * 100),
                'track_condition': random.choice([0, 1, 2, 3]),
                'energy': 100.0,
                'station_idx': 0,
                'arrival_times': [],
                'delay': 0,
                'passengers': random.randint(50, 300),
                'status': 'RUNNING',
                'route': list(self.stations.keys())[:self.num_stations],
                'section_history': [],
                'completion_time': None,
                'energy_consumed': 0,
                'maintenance_alerts': [],
                'weather_alerts': [],
                'passenger_alerts': []
            }
            self.trains.append(train)
        
        # Set current train
        self.current_train_idx = 0
        
        # Update signals and occupancy
        self._update_signals_and_occupancy()
        
        # Get initial state for the first train
        return self._get_state(0), {}
    
    def _get_weather_at_position(self, position):
        """Get weather at specific position"""
        # Convert position to approximate lat/lon (simple mapping)
        lat = 13.0 - (position / self.route_length) * 5  # From Chennai to Coimbatore
        lon = 80.0 - (position / self.route_length) * 3
        
        weather_data = self.weather_api.get_weather_at_location(lat, lon)
        return weather_data
    
    def _get_state(self, train_idx):
        """Get observation state for a specific train"""
        train = self.trains[train_idx]
        sensor = self.maintenance_sensors.get(train_idx)
        
        # Calculate station proximity
        if train['station_idx'] < len(train['route']):
            station_code = train['route'][train['station_idx']]
            station_pos = self.station_positions[train['station_idx']]
            station_proximity = 1 - min(1, abs(train['position'] - station_pos) / 200)
        else:
            station_proximity = 0
        
        # Calculate signal status
        current_section = self._get_current_section(train['position'])
        signal_map = {'GREEN': 0, 'YELLOW': 1, 'RED': 2}
        signal_status = signal_map.get(self.signals.get(current_section, 'GREEN'), 0)
        
        # Calculate section density
        section_density = self.section_occupancy[current_section] / self.max_section_capacity
        
        # Calculate section occupancy
        section_occupancy = section_density
        
        # Weather effect
        weather_effect = train['weather']['effects']['speed_mult']
        
        # Maintenance health
        maintenance_health = sensor.get_health_score() if sensor else 100
        
        # Energy efficiency
        efficiency_profile = self.energy_optimizer.get_optimal_speed_profile(
            train['speed'], train['speed'], 
            self.route_length - train['position']
        )
        energy_efficiency = efficiency_profile['efficiency_score'] if efficiency_profile else 50
        
        # Passenger prediction confidence
        arrival_prediction = self.passenger_system.predict_arrival_time(
            train['id'], train['position'], train['speed'],
            train['route'], self.stations, weather_effect
        )
        prediction_confidence = arrival_prediction['confidence'] if arrival_prediction else 50
        
        return np.array([
            train['position'] / self.route_length,  # Normalized position
            train['speed'] / 40.0,  # Normalized speed
            train['distance_to_next'] / 500.0,  # Normalized distance
            train['time_pressure'],
            weather_effect,  # Weather effect
            train['track_condition'] / 3.0,  # Normalized track condition
            train['energy'] / 100.0,  # Normalized energy
            station_proximity,
            section_density,  # Current section density
            signal_status / 2.0,  # Normalized signal status
            section_occupancy,  # Section occupancy
            maintenance_health / 100.0,  # Maintenance health
            energy_efficiency / 100.0,  # Energy efficiency
            prediction_confidence / 100.0  # Prediction confidence
        ], dtype=np.float32)
    
    def step(self, actions):
        """Step environment for multiple agents"""
        if isinstance(actions, int):
            actions = [actions] * self.num_trains
        
        states = []
        rewards = []
        dones = []
        infos = []
        
        for agent_id, action in enumerate(actions):
            train = self.trains[agent_id]
            sensor = self.maintenance_sensors.get(agent_id)
            
            # Store old state for reward calculation
            old_position = train['position']
            old_speed = train['speed']
            old_energy = train['energy']
            
            # Apply action with weather consideration
            weather_mult = train['weather']['effects']['speed_mult']
            safety_gap_mult = train['weather']['effects']['safety_gap_mult']
            
            if action == 0:  # Emergency stop
                train['acceleration'] = -5.0
            elif action == 1:  # Decelerate
                train['acceleration'] = -1.5 * safety_gap_mult
            elif action == 2:  # Maintain
                train['acceleration'] = 0.0
            elif action == 3:  # Accelerate
                train['acceleration'] = 1.5 * weather_mult
            elif action == 4:  # Full speed
                train['acceleration'] = 3.0 * weather_mult
            
            # Apply physics with weather effects
            train['speed'] += train['acceleration']
            
            # Track effect
            track_mult = self.track_conditions[train['track_condition']]['effect']
            max_speed = 40 * weather_mult * track_mult
            
            # Apply speed limits
            train['speed'] = np.clip(train['speed'], 0, max_speed)
            
            # Update position
            train['position'] += train['speed']
            
            # Update distance to next train (for multi-agent coordination)
            if agent_id < self.num_trains - 1:
                next_train = self.trains[agent_id + 1]
                train['distance_to_next'] = max(0, next_train['position'] - train['position'])
            else:
                train['distance_to_next'] = random.uniform(100, 300)
            
            # Update energy with optimization
            distance_km = train['speed'] / 3600  # Distance in km for this step
            energy_used = self.energy_optimizer.calculate_energy_consumption(
                train['speed'] * 3.6,  # Convert to km/h
                train['acceleration'],
                distance_km
            )
            
            if train['acceleration'] < 0:  # Regenerative braking
                energy_regen = abs(train['acceleration']) * 0.05
                train['energy'] = min(100, train['energy'] - energy_used + energy_regen)
            else:
                train['energy'] = max(0, train['energy'] - energy_used)
            
            train['energy_consumed'] += energy_used
            self.total_energy += energy_used
            
            # Record energy data
            self.energy_optimizer.record_energy_data(
                train['speed'] * 3.6,
                train['acceleration'],
                energy_used
            )
            
            # Update maintenance sensor
            if sensor:
                sensor.update(train['speed'], train['acceleration'])
                maintenance_alerts = sensor.check_maintenance_needed()
                train['maintenance_alerts'] = maintenance_alerts
            
            # Update time pressure
            train['time_pressure'] = min(1.0, train['time_pressure'] + 0.01)
            
            # Check station arrival
            arrival_reward = self._check_station_arrival(train, agent_id)
            
            # Check for completion
            done = train['position'] >= self.route_length or train['station_idx'] >= len(train['route'])
            
            # Calculate rewards
            reward = arrival_reward
            
            # Throughput reward
            position_reward = (train['position'] - old_position) / 10
            reward += position_reward
            
            # Speed maintenance reward
            if 0.4 < train['speed'] / max_speed < 0.8:
                reward += 2
            
            # Headway maintenance with weather adjustment
            safe_distance = 50 * safety_gap_mult
            if train['distance_to_next'] < safe_distance:
                headway_penalty = -20 * (safe_distance - train['distance_to_next']) / safe_distance
                reward += headway_penalty
            elif safe_distance <= train['distance_to_next'] <= safe_distance * 2:
                reward += 5
            else:
                reward -= 2
            
            # Energy efficiency reward
            energy_profile = self.energy_optimizer.get_optimal_speed_profile(
                old_speed, train['speed'],
                self.route_length - old_position
            )
            if energy_profile and energy_profile['efficiency_score'] > 80:
                reward += 5
            
            energy_change = train['energy'] - old_energy
            if energy_change > 0:
                reward += energy_change * 2
            elif abs(train['acceleration']) < 0.5:
                reward += 3
            
            # Maintenance reward/penalty
            if sensor:
                health_score = sensor.get_health_score()
                if health_score < 70:
                    reward -= (100 - health_score) / 10
                elif health_score > 90:
                    reward += 2
            
            # Section occupancy reward
            current_section = self._get_current_section(train['position'])
            if self.section_occupancy[current_section] < self.max_section_capacity:
                reward += 2
            else:
                reward -= 5
            
            # Signal compliance
            if self.signals[current_section] == 'RED' and train['speed'] > 5:
                reward -= 50
                self.total_collisions += 1
            elif self.signals[current_section] == 'YELLOW' and train['speed'] > max_speed * 0.7:
                reward -= 20
            
            # Passenger comfort
            if abs(train['acceleration']) < 0.5:
                reward += 2
            
            # Throughput bonus for completion
            if done and train.get('completion_time') is None:
                train['completion_time'] = datetime.now()
                self.trains_completed += 1
                completion_bonus = 100
                reward += completion_bonus
                
                expected_time = self.route_length / 25 * 3600
                actual_time = (train['completion_time'] - self.start_time).total_seconds()
                if actual_time < expected_time:
                    time_bonus = (expected_time - actual_time) / 10
                    reward += time_bonus
            
            # Update signals and occupancy
            self._update_signals_and_occupancy()
            
            # Track section history
            train['section_history'].append(current_section)
            
            # Get next state
            next_state = self._get_state(agent_id)
            
            # Generate passenger alerts
            passenger_alerts = self.passenger_system.get_passenger_alerts(
                train['id'], train['delay'], 
                train['route'][train['station_idx']] if train['station_idx'] < len(train['route']) else 'TERMINAL'
            )
            train['passenger_alerts'] = passenger_alerts
            
            # Weather alerts
            weather_alerts = self.weather_api.get_weather_alert(train['weather'])
            train['weather_alerts'] = weather_alerts
            
            # Prepare info dictionary
            info = {
                'train_id': train['id'],
                'position': train['position'],
                'speed': train['speed'],
                'speed_kmh': train['speed'] * 3.6,
                'distance_to_next': train['distance_to_next'],
                'energy': train['energy'],
                'energy_consumed': train['energy_consumed'],
                'current_station': train['station_idx'],
                'weather': train['weather']['weather'],
                'weather_effects': train['weather']['effects'],
                'track_condition': self.track_conditions[train['track_condition']]['name'],
                'signal_status': self.signals[current_section],
                'delay': train['delay'],
                'section': current_section,
                'section_occupancy': self.section_occupancy[current_section],
                'throughput': self._calculate_throughput(),
                'collisions': self.total_collisions,
                'maintenance_alerts': train['maintenance_alerts'],
                'weather_alerts': train['weather_alerts'],
                'passenger_alerts': train['passenger_alerts'],
                'maintenance_health': sensor.get_health_score() if sensor else 100,
                'energy_efficiency': self.energy_optimizer.calculate_efficiency_score(
                    train['speed'] * 3.6, train['acceleration']
                ),
                'prediction_accuracy': self.passenger_system.get_prediction_report()['average_accuracy']
            }
            
            # Add collision avoided flag if applicable
            if train['distance_to_next'] < 50 and train['speed'] < 10:
                info['collision_avoided'] = True
            
            # Add energy saved flag if applicable
            if energy_change > 0:
                info['energy_saved'] = energy_change
            
            # Add weather alert flag
            if weather_alerts:
                info['weather_alert'] = True
                info['weather_severity'] = weather_alerts[0]['severity'] if weather_alerts else 'none'
            
            # Add maintenance alert flag
            if train['maintenance_alerts']:
                info['maintenance_alert'] = True
                info['maintenance_issue'] = train['maintenance_alerts'][0]['type'] if train['maintenance_alerts'] else 'none'
            
            states.append(next_state)
            rewards.append(reward)
            dones.append(done)
            infos.append(info)
        
        # Rotate current train index
        self.current_train_idx = (self.current_train_idx + 1) % self.num_trains
        
        # Convert to numpy arrays
        states_array = np.array(states)
        rewards_array = np.array(rewards)
        dones_array = np.array(dones)
        
        return states_array, rewards_array, dones_array, False, infos
    
    def _calculate_throughput(self):
        """Calculate current throughput in trains per hour"""
        if self.trains_completed == 0:
            return 0
        
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time == 0:
            return 0
        
        return (self.trains_completed / elapsed_time) * 3600
    
    def _check_station_arrival(self, train, agent_id):
        """Check if train has arrived at a station"""
        reward = 0
        
        if train['station_idx'] < len(train['route']):
            station_code = train['route'][train['station_idx']]
            station_pos = self.station_positions[train['station_idx']]
            
            if train['position'] >= station_pos:
                # Station arrival bonus
                arrival_bonus = 100
                
                # Punctuality bonus/penalty
                schedule_time = (train['station_idx'] + 1) * 0.5
                actual_time = train['time_pressure'] * 2
                time_diff = abs(actual_time - schedule_time)
                
                if time_diff < 0.1:
                    punctuality_bonus = 50
                    train['delay'] = 0
                elif time_diff < 0.25:
                    punctuality_bonus = 20
                    train['delay'] = time_diff * 60
                else:
                    punctuality_bonus = -30
                    train['delay'] = time_diff * 60
                
                self.total_delay += train['delay']
                
                # Passenger satisfaction
                passenger_bonus = train['passengers'] * 0.1
                
                # Smooth stopping bonus
                if train['speed'] < 5:
                    stopping_bonus = 20
                else:
                    stopping_bonus = -20
                
                reward = arrival_bonus + punctuality_bonus + passenger_bonus + stopping_bonus
                
                # Update passenger system
                self.passenger_system.update_actual_arrival(
                    train['id'], station_code, datetime.now()
                )
                
                # Perform maintenance if needed
                sensor = self.maintenance_sensors.get(agent_id)
                if sensor and sensor.get_health_score() < 70:
                    # Perform minor maintenance
                    sensor.perform_maintenance('minor')
                
                # Update train state
                train['station_idx'] += 1
                train['arrival_times'].append(datetime.now())
                train['time_pressure'] = 0
                
                # Update weather
                train['weather'] = self._get_weather_at_position(train['position'])
                
                # Random track condition change
                if random.random() < 0.1:
                    train['track_condition'] = random.choice([0, 1, 2, 3])
        
        return reward
    
    def render(self, mode='human'):
        """Render the environment"""
        if mode == 'human':
            train = self.trains[self.current_train_idx]
            sensor = self.maintenance_sensors.get(self.current_train_idx)
            
            print(f"\n{'='*90}")
            print(f"🚆 TRAIN {train['id']} - ENHANCED AI CONTROL SYSTEM")
            print(f"{'='*90}")
            
            # Basic info
            print(f"📍 Position: {train['position']:.1f}m / {self.route_length}m")
            print(f"🚀 Speed: {train['speed']:.1f} m/s ({train['speed']*3.6:.1f} km/h)")
            print(f"📏 Distance to next train: {train['distance_to_next']:.1f}m")
            
            # Weather info
            print(f"🌤️ Weather: {train['weather']['effects']['color']} {train['weather']['weather'].upper()}")
            print(f"   Temp: {train['weather']['temperature']:.1f}°C | "
                  f"Visibility: {train['weather']['visibility']:.1f} km | "
                  f"Wind: {train['weather']['wind_speed']:.1f} km/h")
            print(f"   Speed Multiplier: {train['weather']['effects']['speed_mult']:.2f} | "
                  f"Safety Gap Multiplier: {train['weather']['effects']['safety_gap_mult']:.2f}")
            
            # Track condition
            track_info = self.track_conditions[train['track_condition']]
            print(f"🛤️ Track: {track_info['color']} {track_info['name']} "
                  f"(Speed factor: {track_info['effect']:.1f})")
            
            # Energy and signals
            current_section = self._get_current_section(train['position'])
            print(f"⚡ Energy: {train['energy']:.1f}% | Consumed: {train['energy_consumed']:.1f} kWh")
            print(f"🚦 Signal: {self.signals[current_section]} "
                  f"(Section {current_section + 1}/{len(self.sections)})")
            print(f"👥 Section Occupancy: {self.section_occupancy[current_section]}/{self.max_section_capacity}")
            
            # Maintenance info
            if sensor:
                health = sensor.get_health_score()
                health_color = '🟢' if health >= 90 else '🟡' if health >= 70 else '🔴'
                print(f"🔧 Maintenance Health: {health_color} {health:.1f}/100")
                print(f"   Engine Temp: {sensor.engine_temp:.1f}°C | "
                      f"Vibration: {sensor.vibration_level:.1f} mm/s | "
                      f"Oil Pressure: {sensor.oil_pressure:.1f} psi")
            
            # Station info
            if train['station_idx'] < len(train['route']):
                station_code = train['route'][train['station_idx']]
                station_name = self.stations[station_code]['name']
                station_pos = self.station_positions[train['station_idx']]
                distance_to_station = abs(station_pos - train['position'])
                print(f"🚉 Next Station: {station_name} ({distance_to_station:.1f}m away)")
            else:
                print(f"🚉 Next Station: TERMINAL")
            
            print(f"⏱️ Delay: {train['delay']:.1f} minutes")
            print(f"👥 Passengers: {train['passengers']}")
            
            # Alerts
            if train['maintenance_alerts']:
                print(f"\n⚠️ MAINTENANCE ALERTS:")
                for alert in train['maintenance_alerts'][:2]:
                    print(f"   • {alert['message']}")
            
            if train['weather_alerts']:
                print(f"\n⚠️ WEATHER ALERTS:")
                for alert in train['weather_alerts'][:2]:
                    print(f"   • {alert['message']}")
            
            if train['passenger_alerts']:
                print(f"\nℹ️ PASSENGER ALERTS:")
                for alert in train['passenger_alerts'][:2]:
                    print(f"   • {alert['message']}")
            
            # Throughput info
            print(f"\n📊 ENHANCED THROUGHPUT METRICS:")
            print(f"  Trains Completed: {self.trains_completed}")
            print(f"  Current Throughput: {self._calculate_throughput():.1f} trains/hour")
            print(f"  Target Throughput: {self.throughput_target} trains/hour")
            print(f"  Total Delay: {self.total_delay:.1f} minutes")
            print(f"  Total Energy: {self.total_energy:.1f} kWh")
            print(f"  Collisions: {self.total_collisions}")
            
            # Energy efficiency report
            energy_report = self.energy_optimizer.get_energy_report()
            if energy_report:
                print(f"  Energy Efficiency: {energy_report['average_efficiency']:.1f}%")
            
            # Prediction accuracy
            pred_report = self.passenger_system.get_prediction_report()
            print(f"  Prediction Accuracy: {pred_report['average_accuracy']:.1f}% ({pred_report['accuracy_band']})")
            
            print(f"{'='*90}")
    
    def get_train_info(self, train_idx):
        """Get detailed information about a train"""
        if train_idx < len(self.trains):
            train = self.trains[train_idx]
            sensor = self.maintenance_sensors.get(train_idx)
            
            # Calculate ETA
            eta = None
            if train['station_idx'] < len(train['route']):
                station_pos = self.station_positions[train['station_idx']]
                distance = station_pos - train['position']
                if train['speed'] > 0:
                    eta = distance / train['speed'] / 60
            
            # Get arrival prediction
            arrival_prediction = self.passenger_system.predict_arrival_time(
                train['id'], train['position'], train['speed'],
                train['route'], self.stations, train['weather']['effects']['speed_mult']
            )
            
            return {
                'id': train['id'],
                'position': train['position'],
                'speed': train['speed'],
                'speed_kmh': train['speed'] * 3.6,
                'distance_to_next': train['distance_to_next'],
                'energy': train['energy'],
                'energy_consumed': train['energy_consumed'],
                'current_station_idx': train['station_idx'],
                'current_station': train['route'][train['station_idx']] if train['station_idx'] < len(train['route']) else 'TERMINAL',
                'next_station': train['route'][train['station_idx'] + 1] if train['station_idx'] + 1 < len(train['route']) else 'TERMINAL',
                'weather': train['weather'],
                'track_condition': self.track_conditions[train['track_condition']],
                'delay': train['delay'],
                'passengers': train['passengers'],
                'status': train['status'],
                'eta_minutes': eta,
                'arrival_times': train['arrival_times'],
                'section': self._get_current_section(train['position']),
                'section_history': train['section_history'][-10:] if len(train['section_history']) > 10 else train['section_history'],
                'maintenance_health': sensor.get_health_score() if sensor else 100,
                'maintenance_alerts': train['maintenance_alerts'],
                'weather_alerts': train['weather_alerts'],
                'passenger_alerts': train['passenger_alerts'],
                'arrival_prediction': arrival_prediction,
                'energy_efficiency': self.energy_optimizer.calculate_efficiency_score(
                    train['speed'] * 3.6, train['acceleration']
                )
            }
        return None
    
    def get_all_trains_info(self):
        """Get information for all trains"""
        return [self.get_train_info(i) for i in range(len(self.trains))]
    
    def get_environment_stats(self):
        """Get environment statistics including all features"""
        current_throughput = self._calculate_throughput()
        efficiency = (current_throughput / self.throughput_target) * 100 if self.throughput_target > 0 else 0
        
        # Maintenance statistics
        maintenance_scores = []
        for sensor in self.maintenance_sensors.values():
            maintenance_scores.append(sensor.get_health_score())
        avg_maintenance_health = np.mean(maintenance_scores) if maintenance_scores else 100
        
        # Energy statistics
        energy_report = self.energy_optimizer.get_energy_report()
        
        # Prediction statistics
        pred_report = self.passenger_system.get_prediction_report()
        
        return {
            'total_trains': len(self.trains),
            'trains_completed': self.trains_completed,
            'route_length': self.route_length,
            'stations': len(self.station_positions),
            'sections': len(self.sections),
            'average_speed': np.mean([t['speed'] for t in self.trains]),
            'average_energy': np.mean([t['energy'] for t in self.trains]),
            'total_passengers': sum([t['passengers'] for t in self.trains]),
            'current_throughput': current_throughput,
            'target_throughput': self.throughput_target,
            'efficiency_percentage': efficiency,
            'avg_delay': self.total_delay / max(1, self.trains_completed),
            'total_delay': self.total_delay,
            'total_energy': self.total_energy,
            'collisions': self.total_collisions,
            'section_occupancy': self.section_occupancy,
            'avg_maintenance_health': avg_maintenance_health,
            'energy_efficiency': energy_report['average_efficiency'] if energy_report else 0,
            'prediction_accuracy': pred_report['average_accuracy'],
            'total_maintenance_alerts': sum(len(t['maintenance_alerts']) for t in self.trains),
            'total_weather_alerts': sum(len(t['weather_alerts']) for t in self.trains)
        }
    
    def get_enhanced_analysis(self):
        """Enhanced analysis with all features"""
        stats = self.get_environment_stats()
        
        # Section utilization
        section_utilization = {}
        for section, count in self.section_occupancy.items():
            utilization = (count / self.max_section_capacity) * 100
            section_utilization[f'section_{section+1}'] = {
                'trains': count,
                'capacity': self.max_section_capacity,
                'utilization': utilization
            }
        
        # Bottlenecks
        bottlenecks = []
        for section, count in self.section_occupancy.items():
            if count >= self.max_section_capacity:
                bottlenecks.append(f"Section {section+1} at {count}/{self.max_section_capacity} capacity")
        
        # Maintenance analysis
        maintenance_analysis = []
        for train_id, sensor in self.maintenance_sensors.items():
            if sensor.get_health_score() < 70:
                maintenance_analysis.append(f"Train {train_id+1}: Health {sensor.get_health_score():.1f}% - Needs attention")
        
        # Energy analysis
        energy_analysis = []
        if energy_report := self.energy_optimizer.get_energy_report():
            if energy_report['average_efficiency'] < 70:
                energy_analysis.append(f"Energy efficiency low: {energy_report['average_efficiency']:.1f}%")
            for rec in energy_report.get('recommendations', []):
                energy_analysis.append(rec)
        
        return {
            'overall_stats': stats,
            'section_utilization': section_utilization,
            'bottlenecks': bottlenecks,
            'maintenance_analysis': maintenance_analysis,
            'energy_analysis': energy_analysis,
            'weather_conditions': self._get_weather_summary(),
            'recommendations': self._generate_enhanced_recommendations()
        }
    
    def _get_weather_summary(self):
        """Get summary of weather conditions"""
        weather_types = {}
        for train in self.trains:
            w_type = train['weather']['weather']
            weather_types[w_type] = weather_types.get(w_type, 0) + 1
        
        return weather_types
    
    def _generate_enhanced_recommendations(self):
        """Generate enhanced recommendations"""
        recommendations = []
        stats = self.get_environment_stats()
        
        # Throughput recommendations
        if stats['current_throughput'] < stats['target_throughput'] * 0.8:
            recommendations.append("Increase train frequency to meet throughput target")
        
        # Maintenance recommendations
        if stats['avg_maintenance_health'] < 80:
            recommendations.append("Schedule maintenance for trains with health < 80%")
        
        # Energy recommendations
        if stats['energy_efficiency'] < 75:
            recommendations.append("Optimize speed profiles for better energy efficiency")
        
        # Weather-based recommendations
        weather_summary = self._get_weather_summary()
        if 'rain' in weather_summary or 'thunderstorm' in weather_summary:
            recommendations.append("Increase safety gaps in rainy/thunderstorm areas")
        
        # Passenger service recommendations
        if stats['avg_delay'] > 15:
            recommendations.append("Improve punctuality to enhance passenger satisfaction")
        
        return recommendations
    
    def send_communication(self, message):
        """Send communication between agents"""
        self.communication_messages.append({
            **message,
            'timestamp': datetime.now()
        })
        
        # Keep buffer manageable
        if len(self.communication_messages) > 100:
            self.communication_messages.pop(0)
    
    def get_communications(self):
        """Get recent communications"""
        return self.communication_messages[-10:] if self.communication_messages else []

# ========== TEST FUNCTION ==========
if __name__ == "__main__":
    print("🧪 Testing Enhanced Railway Environment with All Features...")
    
    env = EnhancedRailwayEnv(num_trains=5)
    states, _ = env.reset()
    
    print(f"Initial State Shape: {states.shape}")
    print(f"Action Space: {env.action_space}")
    print(f"Observation Space: {env.observation_space}")
    print(f"Number of Trains/Agents: {env.num_trains}")
    
    # Test a few steps
    for step in range(3):
        actions = [env.action_space.sample() for _ in range(env.num_trains)]
        next_states, rewards, dones, _, infos = env.step(actions)
        
        print(f"\nStep {step + 1}:")
        print(f"  Actions: {actions}")
        print(f"  Average Reward: {np.mean(rewards):.2f}")
        print(f"  Throughput: {infos[0].get('throughput', 0):.1f} trains/hour")
        print(f"  Maintenance Health: {infos[0].get('maintenance_health', 100):.1f}%")
        print(f"  Energy Efficiency: {infos[0].get('energy_efficiency', 0):.1f}%")
        
        if any(dones):
            print("  Some trains completed!")
            break
    
    # Get enhanced analysis
    analysis = env.get_enhanced_analysis()
    print(f"\n📊 Enhanced Analysis:")
    print(f"  Current Throughput: {analysis['overall_stats']['current_throughput']:.1f} trains/hour")
    print(f"  Maintenance Health: {analysis['overall_stats']['avg_maintenance_health']:.1f}%")
    print(f"  Energy Efficiency: {analysis['overall_stats']['energy_efficiency']:.1f}%")
    print(f"  Prediction Accuracy: {analysis['overall_stats']['prediction_accuracy']:.1f}%")
    print(f"  Bottlenecks: {len(analysis['bottlenecks'])} sections")
    print(f"  Maintenance Alerts: {len(analysis['maintenance_analysis'])} trains")
    
    print("\n✅ Enhanced environment test complete!")
