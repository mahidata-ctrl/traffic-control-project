import streamlit as st
import time
import streamlit.components.v1 as components
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import requests
import json
from geopy.distance import geodesic
import pytz
from dateutil import parser
import threading
import queue
import asyncio
import aiohttp
import warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="🚆 AI-Powered Railway Throughput Optimizer",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Feature-specific styles */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
    }
    
    .feature-card h4 {
        margin: 0 0 10px 0;
        color: white;
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .feature-card .status {
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 10px;
        display: inline-block;
        margin-top: 10px;
    }
    
    .status-active {
        background: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
    }
    
    .status-warning {
        background: rgba(241, 196, 15, 0.2);
        color: #f1c40f;
    }
    
    .status-critical {
        background: rgba(231, 76, 60, 0.2);
        color: #e74c3c;
    }
    
    /* Alert panels */
    .alert-panel {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid;
        animation: pulse 2s infinite;
    }
    
    .alert-critical {
        border-left-color: #e74c3c;
        background: rgba(231, 76, 60, 0.1);
    }
    
    .alert-warning {
        border-left-color: #f39c12;
        background: rgba(243, 156, 18, 0.1);
    }
    
    .alert-info {
        border-left-color: #3498db;
        background: rgba(52, 152, 219, 0.1);
    }
    
    .alert-success {
        border-left-color: #2ecc71;
        background: rgba(46, 204, 113, 0.1);
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    /* Multi-agent communication panel */
    .communication-panel {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(0, 219, 222, 0.3);
        max-height: 300px;
        overflow-y: auto;
    }
    
    .message {
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-left: 3px solid;
        font-size: 12px;
    }
    
    .message-gap {
        border-left-color: #00dbde;
    }
    
    .message-weather {
        border-left-color: #3498db;
    }
    
    .message-maintenance {
        border-left-color: #e74c3c;
    }
    
    .message-energy {
        border-left-color: #2ecc71;
    }
    
    /* Passenger info panel */
    .passenger-panel {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    
    .passenger-panel h5 {
        margin: 0 0 10px 0;
        color: #00dbde;
    }
    
    /* Maintenance panel */
    .maintenance-gauge {
        width: 100%;
        height: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        position: relative;
        margin: 10px 0;
    }
    
    .gauge-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    .gauge-healthy {
        background: linear-gradient(90deg, #2ecc71, #27ae60);
    }
    
    .gauge-warning {
        background: linear-gradient(90deg, #f1c40f, #f39c12);
    }
    
    .gauge-critical {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
    }
    
    /* Weather widget */
    .weather-widget {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    
    .weather-icon {
        font-size: 40px;
        text-align: center;
        margin: 10px 0;
    }
    
    /* Energy efficiency widget */
    .energy-widget {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ========== ENHANCED INDIAN RAILWAYS DATA ==========
class EnhancedIndianRailwaysData:
    """Complete Indian Railways dataset with enhanced features"""
    
    ZONES = {
        'NR': 'Northern Railway',
        'WR': 'Western Railway',
        'SR': 'Southern Railway',
        'ER': 'Eastern Railway',
        'CR': 'Central Railway',
        'NER': 'North Eastern Railway',
        'NFR': 'Northeast Frontier Railway',
        'ECR': 'East Central Railway',
        'SCR': 'South Central Railway',
        'SWR': 'South Western Railway',
        'NWR': 'North Western Railway',
        'WCR': 'West Central Railway',
        'SECR': 'South East Central Railway'
    }
    
    POPULAR_TRAINS = [
        {
            'train_no': '12673', 'name': 'CHERAN SF EXP', 'type': 'Superfast',
            'source': 'MAS', 'dest': 'CBE', 'zone': 'SR',
            'speed_range': (75, 110), 'route': ['MAS', 'AJJ', 'KPD', 'JTJ', 'SA', 'CBE'],
            'typical_passengers': 800,
            'energy_per_km': 15.5,
            'maintenance_interval': 30
        },
        {
            'train_no': '12671', 'name': 'NILGIRI EXP', 'type': 'Superfast',
            'source': 'MAS', 'dest': 'MTP', 'zone': 'SR',
            'speed_range': (70, 100), 'route': ['MAS', 'KPD', 'SA', 'ED', 'CBE', 'MTP'],
            'typical_passengers': 750,
            'energy_per_km': 16.0,
            'maintenance_interval': 28
        },
        {
            'train_no': '12675', 'name': 'KOVAI EXP', 'type': 'Superfast',
            'source': 'MAS', 'dest': 'CBE', 'zone': 'SR',
            'speed_range': (80, 110), 'route': ['MAS', 'KPD', 'SA', 'CBE'],
            'typical_passengers': 700,
            'energy_per_km': 14.8,
            'maintenance_interval': 32
        },
        {
            'train_no': '12431', 'name': 'RAJDHANI EXP', 'type': 'Rajdhani',
            'source': 'NDLS', 'dest': 'HWH', 'zone': 'NR',
            'speed_range': (90, 130), 'route': ['NDLS', 'CNB', 'ALD', 'MGS', 'HWH'],
            'typical_passengers': 900,
            'energy_per_km': 18.0,
            'maintenance_interval': 25
        },
        {
            'train_no': '12007', 'name': 'SHATABDI EXP', 'type': 'Shatabdi',
            'source': 'MAS', 'dest': 'SBC', 'zone': 'SR',
            'speed_range': (85, 120), 'route': ['MAS', 'KPD', 'KJM', 'SBC'],
            'typical_passengers': 600,
            'energy_per_km': 16.5,
            'maintenance_interval': 20
        }
    ]
    
    STATIONS = {
        'MAS': {'name': 'Chennai Central', 'lat': 13.0827, 'lon': 80.2707, 'zone': 'SR', 'platforms': 12},
        'AJJ': {'name': 'Arakkonam Junction', 'lat': 13.0846, 'lon': 79.6725, 'zone': 'SR', 'platforms': 6},
        'KPD': {'name': 'Katpadi Junction', 'lat': 12.9702, 'lon': 79.1590, 'zone': 'SR', 'platforms': 5},
        'JTJ': {'name': 'Jolarpettai Junction', 'lat': 12.5667, 'lon': 78.5667, 'zone': 'SR', 'platforms': 4},
        'SA': {'name': 'Salem Junction', 'lat': 11.6643, 'lon': 78.1460, 'zone': 'SR', 'platforms': 5},
        'ED': {'name': 'Erode Junction', 'lat': 11.3420, 'lon': 77.7172, 'zone': 'SR', 'platforms': 6},
        'TUP': {'name': 'Tiruppur', 'lat': 11.1075, 'lon': 77.3398, 'zone': 'SR', 'platforms': 3},
        'CBE': {'name': 'Coimbatore Junction', 'lat': 11.0168, 'lon': 76.9558, 'zone': 'SR', 'platforms': 7},
        'NDLS': {'name': 'New Delhi', 'lat': 28.6423, 'lon': 77.2211, 'zone': 'NR', 'platforms': 16},
        'SBC': {'name': 'Bangalore City', 'lat': 12.9774, 'lon': 77.5695, 'zone': 'SR', 'platforms': 10}
    }
    
    TRAIN_TYPES = {
        'Rajdhani': {'color': '#FF0000', 'icon': '👑', 'priority': 1, 'energy_factor': 1.2},
        'Shatabdi': {'color': '#0000FF', 'icon': '⚡', 'priority': 2, 'energy_factor': 1.1},
        'Duronto': {'color': '#008000', 'icon': '🚀', 'priority': 3, 'energy_factor': 1.15},
        'Garib Rath': {'color': '#800080', 'icon': '💰', 'priority': 4, 'energy_factor': 0.9},
        'Superfast': {'color': '#DC143C', 'icon': '🚅', 'priority': 5, 'energy_factor': 1.0},
        'Express': {'color': '#228B22', 'icon': '🚂', 'priority': 6, 'energy_factor': 0.95},
        'Passenger': {'color': '#808080', 'icon': '🚃', 'priority': 7, 'energy_factor': 0.85}
    }
    
    WEATHER_ICONS = {
        'clear': '☀️',
        'clouds': '☁️',
        'rain': '🌧️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'fog': '🌫️',
        'mist': '🌁'
    }

# ========== ENHANCED LIVE TRAIN SIMULATOR ==========
class EnhancedLiveTrainSimulator:
    """Enhanced simulator with all new features"""
    
    def __init__(self, num_trains=20):
        self.num_trains = num_trains
        self.trains = []
        self.last_update = datetime.now()
        self.running = True
        
        # Enhanced tracking
        self.throughput_history = []
        self.delay_history = []
        self.energy_history = []
        self.maintenance_alerts_history = []
        self.weather_alerts_history = []
        self.communication_history = []
        self.passenger_predictions = []
        
        self.throughput_target = 25
        
        # Multi-agent communication
        self.agent_messages = []
        self.communication_stats = {
            'gap_adjustments': 0,
            'weather_warnings': 0,
            'maintenance_alerts': 0,
            'energy_savings': 0
        }
        
        # Predictive maintenance
        self.maintenance_sensors = {}
        
        # Energy optimization
        self.energy_optimizer = {
            'total_energy': 0,
            'regenerated_energy': 0,
            'efficiency_score': 85.0
        }
        
        # Passenger predictions
        self.passenger_system = {
            'predictions': {},
            'accuracy': 94.7,
            'total_predictions': 0,
            'accurate_predictions': 0
        }
        
        self._initialize_trains()
        
        # Start background thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _initialize_trains(self):
        """Initialize trains with enhanced features"""
        self.trains = []
        
        for i in range(self.num_trains):
            train_info = random.choice(EnhancedIndianRailwaysData.POPULAR_TRAINS)
            route = train_info['route']
            
            if len(route) >= 2:
                current_idx = random.randint(0, len(route) - 2)
                current_station = route[current_idx]
                next_station = route[current_idx + 1]
                
                if current_station in EnhancedIndianRailwaysData.STATIONS:
                    base_lat = EnhancedIndianRailwaysData.STATIONS[current_station]['lat']
                    base_lon = EnhancedIndianRailwaysData.STATIONS[current_station]['lon']
                    
                    lat_offset = random.uniform(-0.3, 0.3)
                    lon_offset = random.uniform(-0.3, 0.3)
                    
                    # Initialize maintenance sensor
                    self.maintenance_sensors[i] = {
                        'engine_temp': random.uniform(80, 95),
                        'vibration': random.uniform(2.0, 4.0),
                        'oil_pressure': random.uniform(35, 50),
                        'brake_wear': random.uniform(5, 25),
                        'last_maintenance': datetime.now() - timedelta(days=random.randint(1, 40)),
                        'health_score': random.uniform(70, 98)
                    }
                    
                    # Weather at location
                    weather_types = ['clear', 'clouds', 'rain', 'fog']
                    weather_weights = [0.6, 0.2, 0.15, 0.05]
                    weather = random.choices(weather_types, weights=weather_weights)[0]
                    
                    weather_effects = {
                        'clear': {'speed_mult': 1.0, 'safety_gap_mult': 1.0},
                        'clouds': {'speed_mult': 0.95, 'safety_gap_mult': 1.1},
                        'rain': {'speed_mult': 0.8, 'safety_gap_mult': 1.3},
                        'fog': {'speed_mult': 0.6, 'safety_gap_mult': 1.6}
                    }
                    
                    train = {
                        'train_no': train_info['train_no'],
                        'name': train_info['name'],
                        'type': train_info['type'],
                        'source': train_info['source'],
                        'destination': train_info['dest'],
                        'current_station': current_station,
                        'next_station': next_station,
                        'route': route,
                        'current_idx': current_idx,
                        'speed': random.randint(*train_info['speed_range']),
                        'delay': random.randint(0, 45),
                        'status': 'Running',
                        'latitude': base_lat + lat_offset,
                        'longitude': base_lon + lon_offset,
                        'last_update': datetime.now(),
                        'color': EnhancedIndianRailwaysData.TRAIN_TYPES[train_info['type']]['color'],
                        'icon': EnhancedIndianRailwaysData.TRAIN_TYPES[train_info['type']]['icon'],
                        'zone': train_info['zone'],
                        'passengers': train_info['typical_passengers'] + random.randint(-100, 100),
                        'coach_count': random.randint(12, 24),
                        'section': random.randint(1, 10),
                        'section_occupancy': random.randint(1, 3),
                        'throughput_impact': random.uniform(0.8, 1.2),
                        'weather': weather,
                        'weather_effects': weather_effects[weather],
                        'energy_consumption': train_info['energy_per_km'],
                        'maintenance_due': (datetime.now() - self.maintenance_sensors[i]['last_maintenance']).days > train_info['maintenance_interval'],
                        'agent_id': i,
                        'communication_partners': []
                    }
                    self.trains.append(train)
        
        self._update_throughput_metrics()
        self._initialize_passenger_predictions()
    
    def _initialize_passenger_predictions(self):
        """Initialize passenger predictions for all trains"""
        for train in self.trains:
            # Predict arrival at next station
            prediction_id = f"{train['train_no']}_{train['next_station']}"
            current_time = datetime.now()
            
            # Calculate predicted arrival (current time + random ETA)
            eta_minutes = random.randint(15, 90)
            predicted_arrival = current_time + timedelta(minutes=eta_minutes)
            
            self.passenger_system['predictions'][prediction_id] = {
                'train_no': train['train_no'],
                'train_name': train['name'],
                'current_station': train['current_station'],
                'next_station': train['next_station'],
                'predicted_arrival': predicted_arrival,
                'prediction_time': current_time,
                'confidence': random.uniform(85, 99),
                'delay_prediction': random.randint(0, 20),
                'platform_prediction': random.choice(['1A', '2B', '3C', '4D', '5E'])
            }
            
            self.passenger_system['total_predictions'] += 1
    
    def _update_throughput_metrics(self):
        """Calculate and update throughput metrics"""
        total_trains = len(self.trains)
        avg_speed = np.mean([t['speed'] for t in self.trains]) if self.trains else 0
        avg_delay = np.mean([t['delay'] for t in self.trains]) if self.trains else 0
        
        # Enhanced throughput calculation
        speed_factor = avg_speed / 100
        delay_factor = 1 - (avg_delay / 120)
        weather_factor = np.mean([t['weather_effects']['speed_mult'] for t in self.trains]) if self.trains else 1.0
        
        throughput = self.throughput_target * speed_factor * delay_factor * weather_factor
        
        self.throughput_history.append(throughput)
        self.delay_history.append(avg_delay)
        
        # Update energy efficiency
        total_energy = sum([t['energy_consumption'] * t['speed'] / 100 for t in self.trains])
        self.energy_optimizer['total_energy'] = total_energy
        self.energy_optimizer['efficiency_score'] = 85 + random.uniform(-5, 5)
        
        if len(self.throughput_history) > 100:
            self.throughput_history.pop(0)
            self.delay_history.pop(0)
    
    def simulate_multi_agent_communication(self):
        """Simulate communication between agents"""
        if len(self.trains) < 2:
            return
        
        # Randomly select agents to communicate
        if random.random() < 0.3:  # 30% chance of communication each update
            sender_idx = random.randint(0, len(self.trains) - 1)
            receiver_idx = random.choice([i for i in range(len(self.trains)) if i != sender_idx])
            
            sender = self.trains[sender_idx]
            receiver = self.trains[receiver_idx]
            
            # Determine message type
            message_types = ['gap_adjustment', 'weather_warning', 'maintenance_alert', 'energy_saving']
            weights = [0.4, 0.3, 0.2, 0.1]
            message_type = random.choices(message_types, weights=weights)[0]
            
            message = {
                'sender': sender['agent_id'],
                'sender_name': sender['name'],
                'receiver': receiver['agent_id'],
                'receiver_name': receiver['name'],
                'type': message_type,
                'timestamp': datetime.now(),
                'data': self._generate_message_data(message_type, sender, receiver)
            }
            
            self.agent_messages.append(message)
            self.communication_history.append(message)
            self.communication_stats[f"{message_type}s"] += 1
            
            # Keep history manageable
            if len(self.agent_messages) > 50:
                self.agent_messages.pop(0)
            if len(self.communication_history) > 100:
                self.communication_history.pop(0)
    
    def _generate_message_data(self, message_type, sender, receiver):
        """Generate message data based on type"""
        if message_type == 'gap_adjustment':
            distance = abs(sender['section'] - receiver['section']) * 10 + random.uniform(0, 5)
            return {
                'current_gap': distance,
                'suggested_gap': distance + random.uniform(-2, 2),
                'reason': 'Optimizing throughput',
                'urgency': 'medium' if distance < 15 else 'low'
            }
        elif message_type == 'weather_warning':
            return {
                'weather': sender['weather'],
                'severity': 'high' if sender['weather'] in ['rain', 'fog'] else 'medium',
                'location_section': sender['section'],
                'recommendation': f"Reduce speed by {int((1 - sender['weather_effects']['speed_mult']) * 100)}%"
            }
        elif message_type == 'maintenance_alert':
            sensor = self.maintenance_sensors.get(sender['agent_id'], {})
            return {
                'health_score': sensor.get('health_score', 85),
                'issue': random.choice(['High temperature', 'Vibration alert', 'Oil pressure low']),
                'recommendation': 'Inspect at next station',
                'urgency': 'high' if sensor.get('health_score', 85) < 70 else 'medium'
            }
        else:  # energy_saving
            return {
                'current_speed': sender['speed'],
                'suggested_speed': sender['speed'] + random.uniform(-5, 0),
                'estimated_savings': random.uniform(0.5, 2.0),
                'reason': 'Optimal energy efficiency'
            }
    
    def update_maintenance_sensors(self):
        """Update maintenance sensors for all trains"""
        for agent_id, sensor in self.maintenance_sensors.items():
            if agent_id < len(self.trains):
                train = self.trains[agent_id]
                
                # Degrade sensors based on operation
                speed_factor = train['speed'] / 100
                
                # Engine temperature increases with speed
                sensor['engine_temp'] += speed_factor * random.uniform(0.1, 0.3)
                sensor['engine_temp'] = min(120, max(70, sensor['engine_temp']))
                
                # Vibration increases with speed and time
                sensor['vibration'] += speed_factor * random.uniform(0.05, 0.15)
                sensor['vibration'] = min(10, max(1, sensor['vibration']))
                
                # Oil pressure decreases over time
                sensor['oil_pressure'] -= random.uniform(0.01, 0.05)
                sensor['oil_pressure'] = max(20, sensor['oil_pressure'])
                
                # Brake wear increases with deceleration events
                if random.random() < 0.2:
                    sensor['brake_wear'] += random.uniform(0.1, 0.5)
                    sensor['brake_wear'] = min(100, sensor['brake_wear'])
                
                # Calculate health score
                temp_score = 100 - abs(sensor['engine_temp'] - 85) * 2
                vib_score = 100 - (sensor['vibration'] - 2) * 10
                oil_score = sensor['oil_pressure'] * 2
                brake_score = 100 - sensor['brake_wear']
                
                sensor['health_score'] = max(0, min(100, (temp_score + vib_score + oil_score + brake_score) / 4))
                
                # Generate maintenance alert if needed
                if sensor['health_score'] < 70 and random.random() < 0.1:
                    alert = {
                        'agent_id': agent_id,
                        'train_no': train['train_no'],
                        'train_name': train['name'],
                        'issue': 'Maintenance required',
                        'health_score': sensor['health_score'],
                        'timestamp': datetime.now(),
                        'recommendation': 'Schedule maintenance at next major station'
                    }
                    self.maintenance_alerts_history.append(alert)
    
    def update_passenger_predictions(self):
        """Update and improve passenger predictions"""
        for prediction_id, prediction in self.passenger_system['predictions'].items():
            # Update prediction accuracy based on various factors
            time_diff = (datetime.now() - prediction['prediction_time']).total_seconds() / 60
            
            # Accuracy decreases with time
            time_decay = min(10, time_diff / 10)
            
            # Weather effect
            train = next((t for t in self.trains if t['train_no'] == prediction['train_no']), None)
            if train:
                weather_effect = 1.0 if train['weather'] == 'clear' else 0.9
                prediction['confidence'] = max(60, prediction['confidence'] - time_decay) * weather_effect
                
                # Update arrival prediction based on current speed
                if random.random() < 0.3:  # 30% chance to update
                    adjustment = random.randint(-5, 5)
                    prediction['predicted_arrival'] += timedelta(minutes=adjustment)
                    prediction['delay_prediction'] = max(0, prediction['delay_prediction'] + adjustment)
            
            # Record if prediction was accurate (simulated)
            if random.random() < prediction['confidence'] / 100:
                self.passenger_system['accurate_predictions'] += 1
            
            self.passenger_system['accuracy'] = (
                self.passenger_system['accurate_predictions'] / 
                max(1, self.passenger_system['total_predictions']) * 100
            )
    
    def _update_loop(self):
        """Background thread to update all features"""
        while self.running:
            time.sleep(5)  # Update every 5 seconds
            
            # Update train positions
            self.update_positions()
            
            # Simulate multi-agent communication
            self.simulate_multi_agent_communication()
            
            # Update maintenance sensors
            self.update_maintenance_sensors()
            
            # Update passenger predictions
            self.update_passenger_predictions()
            
            # Update throughput metrics
            self._update_throughput_metrics()
            
            # Update weather (random changes)
            if random.random() < 0.1:  # 10% chance to change weather
                for train in self.trains:
                    if random.random() < 0.2:  # 20% chance per train
                        new_weather = random.choice(['clear', 'clouds', 'rain', 'fog'])
                        train['weather'] = new_weather
                        
                        # Record weather alert
                        if new_weather in ['rain', 'fog']:
                            alert = {
                                'train_no': train['train_no'],
                                'location': f"Section {train['section']}",
                                'weather': new_weather,
                                'timestamp': datetime.now(),
                                'effect': 'Speed reduction recommended'
                            }
                            self.weather_alerts_history.append(alert)
            
            self.last_update = datetime.now()
    
    def update_positions(self):
        """Update train positions with enhanced logic"""
        for train in self.trains:
            # Move train with weather effects
            speed_mult = train['weather_effects']['speed_mult']
            base_speed_change = random.uniform(-2, 3) * speed_mult
            
            # Adjust speed based on maintenance
            sensor = self.maintenance_sensors.get(train['agent_id'], {})
            maintenance_factor = sensor.get('health_score', 100) / 100
            
            train['speed'] = max(40, min(130, train['speed'] + base_speed_change * maintenance_factor))
            
            # Update position
            lat_change = random.uniform(-0.01, 0.01)
            lon_change = random.uniform(-0.01, 0.01)
            
            train['latitude'] += lat_change
            train['longitude'] += lon_change
            
            # Update delay
            delay_change = random.randint(-2, 4)
            train['delay'] = max(0, train['delay'] + delay_change)
            
            # Update status based on delay
            if train['delay'] > 60:
                train['status'] = 'Heavily Delayed'
            elif train['delay'] > 30:
                train['status'] = 'Delayed'
            elif train['delay'] > 15:
                train['status'] = 'Slightly Delayed'
            else:
                train['status'] = 'On Time'
            
            # Update section
            train['section'] = random.randint(1, 10)
            train['section_occupancy'] = random.randint(1, 3)
            
            # Update timestamp
            train['last_update'] = datetime.now()
            
            # Update energy consumption
            energy_used = train['energy_consumption'] * (train['speed'] / 100) * (1/maintenance_factor)
            self.energy_optimizer['total_energy'] += energy_used
            
            # Regeneration from braking
            if base_speed_change < 0:
                regen = abs(base_speed_change) * 0.1
                self.energy_optimizer['regenerated_energy'] += regen
    
    # ... [Rest of the methods from previous version with enhancements] ...
    def get_all_trains(self, filters=None):
        """Get all trains with optional filtering"""
        trains = self.trains.copy()
        
        if filters:
            if filters.get('train_types'):
                trains = [t for t in trains if t['type'] in filters['train_types']]
            if filters.get('speed_range'):
                min_speed, max_speed = filters['speed_range']
                trains = [t for t in trains if min_speed <= t['speed'] <= max_speed]
            if filters.get('delay_filter') != 'Any':
                max_delay = {'On Time': 5, 'Up to 15 min': 15, 'Up to 30 min': 30, 'Up to 1 hr': 60}.get(filters['delay_filter'], 999)
                trains = [t for t in trains if t['delay'] <= max_delay]
            if filters.get('zone'):
                trains = [t for t in trains if t['zone'] == filters['zone']]
            if filters.get('section'):
                trains = [t for t in trains if t['section'] == filters['section']]
        
        return trains
    
    def get_enhanced_analysis(self):
        """Get enhanced analysis with all features"""
        throughput_analysis = self.get_throughput_analysis()
        
        # Maintenance analysis
        maintenance_needed = []
        for agent_id, sensor in self.maintenance_sensors.items():
            if sensor['health_score'] < 70:
                train = self.trains[agent_id] if agent_id < len(self.trains) else None
                if train:
                    maintenance_needed.append({
                        'train_no': train['train_no'],
                        'train_name': train['name'],
                        'health_score': sensor['health_score'],
                        'issues': self._get_maintenance_issues(sensor)
                    })
        
        # Energy analysis
        total_consumed = self.energy_optimizer['total_energy']
        total_regen = self.energy_optimizer['regenerated_energy']
        efficiency = self.energy_optimizer['efficiency_score']
        
        # Weather analysis
        weather_distribution = {}
        for train in self.trains:
            weather = train['weather']
            weather_distribution[weather] = weather_distribution.get(weather, 0) + 1
        
        # Communication analysis
        recent_comms = self.communication_history[-10:] if self.communication_history else []
        
        return {
            'throughput_analysis': throughput_analysis,
            'maintenance_analysis': {
                'trains_needing_maintenance': len(maintenance_needed),
                'details': maintenance_needed[:5],
                'avg_health_score': np.mean([s['health_score'] for s in self.maintenance_sensors.values()]) if self.maintenance_sensors else 100
            },
            'energy_analysis': {
                'total_consumed_kwh': total_consumed,
                'regenerated_kwh': total_regen,
                'net_consumption': total_consumed - total_regen,
                'efficiency_score': efficiency,
                'savings_percentage': (total_regen / max(1, total_consumed)) * 100
            },
            'weather_analysis': {
                'distribution': weather_distribution,
                'alerts': self.weather_alerts_history[-5:] if self.weather_alerts_history else []
            },
            'communication_analysis': {
                'stats': self.communication_stats,
                'recent_messages': recent_comms,
                'total_messages': len(self.communication_history)
            },
            'passenger_analysis': {
                'prediction_accuracy': self.passenger_system['accuracy'],
                'total_predictions': self.passenger_system['total_predictions'],
                'recent_predictions': list(self.passenger_system['predictions'].values())[-3:]
            }
        }
    
    def _get_maintenance_issues(self, sensor):
        """Get maintenance issues from sensor data"""
        issues = []
        if sensor['engine_temp'] > 100:
            issues.append(f"High engine temperature: {sensor['engine_temp']:.1f}°C")
        if sensor['vibration'] > 5.0:
            issues.append(f"High vibration: {sensor['vibration']:.1f} mm/s")
        if sensor['oil_pressure'] < 30:
            issues.append(f"Low oil pressure: {sensor['oil_pressure']:.1f} psi")
        if sensor['brake_wear'] > 40:
            issues.append(f"Brake wear: {sensor['brake_wear']:.1f}%")
        return issues
    
    def get_throughput_analysis(self):
        """Get throughput analysis"""
        current_throughput = self.throughput_history[-1] if self.throughput_history else 0
        avg_throughput = np.mean(self.throughput_history) if self.throughput_history else 0
        
        section_counts = {}
        for train in self.trains:
            section = train['section']
            section_counts[section] = section_counts.get(section, 0) + 1
        
        bottlenecks = []
        for section, count in section_counts.items():
            if count > 2:
                bottlenecks.append(f"Section {section}: {count} trains")
        
        efficiency = (current_throughput / self.throughput_target) * 100 if self.throughput_target > 0 else 0
        
        return {
            'current_throughput': current_throughput,
            'avg_throughput': avg_throughput,
            'target_throughput': self.throughput_target,
            'efficiency_percentage': efficiency,
            'total_trains': len(self.trains),
            'section_distribution': section_counts,
            'bottlenecks': bottlenecks,
            'throughput_history': self.throughput_history[-20:],
            'delay_history': self.delay_history[-20:]
        }

# ========== INITIALIZE ENHANCED SIMULATOR ==========
@st.cache_resource
def get_enhanced_simulator():
    return EnhancedLiveTrainSimulator(num_trains=20)

simulator = get_enhanced_simulator()

# ========== SIDEBAR WITH ENHANCED FEATURES ==========
with st.sidebar:
    # Logo and Title
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 40px; margin-bottom: -10px;">🤖</div>
            <div style="font-size: 10px; color: #94a3b8;">ENHANCED AI</div>
        </div>
        """, unsafe_allow_html=True)
    with col_title:
        st.markdown("<h2 style='margin: 0;'>Railway AI Control</h2>", unsafe_allow_html=True)
        st.markdown("<p style='margin: 0; font-size: 12px; color: #94a3b8;'>Multi-Agent • Predictive • Green</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feature Status
    st.subheader("🚀 Active Features")
    
    col_feat1, col_feat2 = st.columns(2)
    with col_feat1:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 MARL</h4>
            <div style="font-size: 12px; color: rgba(255,255,255,0.9);">
                20 agents communicating
            </div>
            <div class="status status-active">ACTIVE</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_feat2:
        st.markdown("""
        <div class="feature-card">
            <h4>🌤️ Weather AI</h4>
            <div style="font-size: 12px; color: rgba(255,255,255,0.9);">
                Real-time adaptation
            </div>
            <div class="status status-active">ACTIVE</div>
        </div>
        """, unsafe_allow_html=True)
    
    col_feat3, col_feat4 = st.columns(2)
    with col_feat3:
        st.markdown("""
        <div class="feature-card">
            <h4>🔧 Predictive Maint</h4>
            <div style="font-size: 12px; color: rgba(255,255,255,0.9);">
                Health monitoring
            </div>
            <div class="status status-active">ACTIVE</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_feat4:
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Energy AI</h4>
            <div style="font-size: 12px; color: rgba(255,255,255,0.9);">
                Green optimization
            </div>
            <div class="status status-active">ACTIVE</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h4>👥 Passenger AI</h4>
        <div style="font-size: 12px; color: rgba(255,255,255,0.9);">
            Real-time predictions
        </div>
        <div class="status status-active">{:.1f}% accuracy</div>
    </div>
    """.format(simulator.passenger_system['accuracy']), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Multi-Agent Communication Panel
    st.subheader("📡 Live Agent Communications")
    
    comm_messages = st.container(height=200)
    
    with comm_messages:
        recent_messages = simulator.agent_messages[-5:] if simulator.agent_messages else []
        for msg in reversed(recent_messages):
            message_class = f"message-{msg['type'].split('_')[0]}"
            
            st.markdown(f"""
            <div class="message {message_class}">
                <strong>{msg['sender_name']}</strong> → {msg['receiver_name']}<br>
                <small>Type: {msg['type'].replace('_', ' ').title()}</small><br>
                <small>{msg['timestamp'].strftime('%H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown(f"**Total Messages:** {len(simulator.communication_history)}")
    
    st.markdown("---")
    
    # Maintenance Alerts
    st.subheader("⚠️ Maintenance Alerts")
    
    maintenance_container = st.container(height=150)
    
    with maintenance_container:
        maintenance_needed = []
        for agent_id, sensor in simulator.maintenance_sensors.items():
            if sensor['health_score'] < 70:
                train = simulator.trains[agent_id] if agent_id < len(simulator.trains) else None
                if train:
                    maintenance_needed.append((train['name'], sensor['health_score']))
        
        if maintenance_needed:
            for train_name, health in maintenance_needed[:3]:
                st.error(f"**{train_name}**: Health {health:.1f}%")
        else:
            st.success("✅ All trains healthy")
    
    st.markdown("---")
    
    # Weather Overview
    st.subheader("🌤️ Weather Overview")
    
    # Weather distribution
    weather_dist = {}
    for train in simulator.trains:
        weather = train['weather']
        weather_dist[weather] = weather_dist.get(weather, 0) + 1
    
    for weather, count in list(weather_dist.items())[:3]:
        icon = EnhancedIndianRailwaysData.WEATHER_ICONS.get(weather, '☀️')
        st.markdown(f"{icon} **{weather.title()}**: {count} trains")
    
    st.markdown("---")
    
    # Quick Controls
    st.subheader("⚡ Quick Controls")
    
    col_control1, col_control2 = st.columns(2)
    with col_control1:
        if st.button("🔄 Boost All", use_container_width=True):
            for train in simulator.trains:
                train['speed'] = min(130, train['speed'] + 10)
            st.success("All trains accelerated!")
    
    with col_control2:
        if st.button("🛑 Safe Mode", use_container_width=True):
            for train in simulator.trains:
                train['speed'] = max(60, train['speed'] - 15)
            st.info("Safe mode activated")
    
    if st.button("🔧 Perform Maintenance", use_container_width=True):
        for sensor in simulator.maintenance_sensors.values():
            sensor['health_score'] = min(100, sensor['health_score'] + 20)
        st.success("Maintenance performed on all trains")
    
    st.markdown("---")
    
    # System Info
    st.subheader("📊 System Stats")
    
    analysis = simulator.get_enhanced_analysis()
    
    st.metric("Agents", f"{simulator.num_trains}")
    st.metric("Throughput", f"{analysis['throughput_analysis']['current_throughput']:.1f}")
    st.metric("Energy Eff", f"{analysis['energy_analysis']['efficiency_score']:.1f}%")
    st.metric("Pred Accuracy", f"{analysis['passenger_analysis']['prediction_accuracy']:.1f}%")

# ========== MAIN DASHBOARD ==========
st.title("🚆 Enhanced AI-Powered Railway Control System")
st.markdown("<span class='live-pulse'></span> <span style='color: #ff0000; font-weight: bold;'>LIVE</span> Multi-Agent RL • Weather AI • Predictive Maintenance • Green Railways • Passenger AI", 
            unsafe_allow_html=True)

# Add moving train animation
st.markdown("<div class='moving-train'>🚅</div>", unsafe_allow_html=True)

# Initialize session state
if 'selected_train' not in st.session_state:
    st.session_state.selected_train = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# ========== ENHANCED DASHBOARD TABS ==========
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤖 Multi-Agent Control", 
    "🌤️ Weather AI", 
    "🔧 Predictive Maintenance", 
    "⚡ Green Railways", 
    "👥 Passenger AI",
    "📊 Unified Dashboard"
])

with tab1:
    # MULTI-AGENT CONTROL TAB
    st.subheader("🤖 Multi-Agent Reinforcement Learning Control")
    
    col_agent1, col_agent2 = st.columns(2)
    
    with col_agent1:
        st.markdown("### 🎯 Agent Coordination")
        
        # Agent communication network visualization
        st.markdown("#### 📡 Communication Network")
        
        # Create agent network visualization
        agent_connections = []
        for msg in simulator.communication_history[-20:]:
            agent_connections.append({
                'from': msg['sender'],
                'to': msg['receiver'],
                'type': msg['type']
            })
        
        # Display agent status
        st.markdown("#### 🤖 Agent Status")
        
        for i, train in enumerate(simulator.trains[:5]):  # Show first 5 agents
            sensor = simulator.maintenance_sensors.get(i, {})
            health = sensor.get('health_score', 100)
            
            col_agent_a, col_agent_b, col_agent_c = st.columns([2, 1, 1])
            with col_agent_a:
                st.markdown(f"**{train['name']}**")
                st.markdown(f"*Agent {i} • {train['type']}*")
            
            with col_agent_b:
                st.markdown(f"**{train['speed']}** km/h")
            
            with col_agent_c:
                health_color = "#2ecc71" if health >= 80 else "#f39c12" if health >= 70 else "#e74c3c"
                st.markdown(f"<span style='color: {health_color};'>**{health:.0f}%**</span>", unsafe_allow_html=True)
        
        # Agent communication statistics
        st.markdown("#### 📊 Communication Stats")
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Gap Adjust", simulator.communication_stats['gap_adjustments'])
        with col_stat2:
            st.metric("Weather Warn", simulator.communication_stats['weather_warnings'])
        with col_stat3:
            st.metric("Maint Alerts", simulator.communication_stats['maintenance_alerts'])
    
    with col_agent2:
        st.markdown("### 🎮 Agent Control Panel")
        
        # Select agent to control
        selected_agent = st.selectbox(
            "Select Agent:",
            options=[f"Agent {i}: {train['name']}" for i, train in enumerate(simulator.trains)],
            index=0
        )
        
        agent_id = int(selected_agent.split(":")[0].replace("Agent ", ""))
        
        if agent_id < len(simulator.trains):
            train = simulator.trains[agent_id]
            sensor = simulator.maintenance_sensors.get(agent_id, {})
            
            # Agent information
            st.markdown(f"**Selected:** {train['name']} ({train['train_no']})")
            st.markdown(f"**Position:** Section {train['section']}")
            st.markdown(f"**Status:** {train['status']}")
            st.markdown(f"**Delay:** {train['delay']} minutes")
            
            # Control sliders
            st.markdown("#### ⚙️ Control Parameters")
            
            target_speed = st.slider(
                "Target Speed (km/h):",
                min_value=40,
                max_value=130,
                value=int(train['speed']),
                key=f"agent_speed_{agent_id}"
            )
            
            safety_gap = st.slider(
                "Safety Gap (relative):",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1,
                key=f"agent_gap_{agent_id}"
            )
            
            # Communication controls
            st.markdown("#### 📡 Send Message")
            
            col_msg1, col_msg2 = st.columns(2)
            with col_msg1:
                message_type = st.selectbox(
                    "Message Type:",
                    ["gap_adjustment", "weather_warning", "maintenance_alert", "energy_saving"],
                    key=f"msg_type_{agent_id}"
                )
            
            with col_msg2:
                if st.button("📤 Send Broadcast", use_container_width=True):
                    # Send message to all other agents
                    for other_id in range(len(simulator.trains)):
                        if other_id != agent_id:
                            message = {
                                'sender': agent_id,
                                'sender_name': train['name'],
                                'receiver': other_id,
                                'receiver_name': simulator.trains[other_id]['name'],
                                'type': message_type,
                                'timestamp': datetime.now(),
                                'data': simulator._generate_message_data(message_type, train, simulator.trains[other_id])
                            }
                            simulator.agent_messages.append(message)
                            simulator.communication_history.append(message)
                    
                    st.success(f"Message broadcast to {len(simulator.trains)-1} agents")
            
            # Apply controls
            if st.button("🔄 Apply Controls", type="primary", use_container_width=True):
                train['speed'] = target_speed
                st.success(f"Controls applied to Agent {agent_id}")
        
        # Multi-agent coordination strategies
        st.markdown("### 🎯 Coordination Strategies")
        
        strategy = st.selectbox(
            "Select Coordination Strategy:",
            [
                "Gap Optimization",
                "Weather Adaptation",
                "Energy Saving Convoy",
                "Priority-based Scheduling",
                "Dynamic Headway"
            ]
        )
        
        if st.button("🚀 Apply Strategy", use_container_width=True):
            if strategy == "Gap Optimization":
                # Optimize gaps between trains
                for i in range(len(simulator.trains) - 1):
                    simulator.trains[i]['speed'] = max(60, simulator.trains[i]['speed'] - 5)
                st.success("Gap optimization applied")
            
            elif strategy == "Weather Adaptation":
                # Adjust for weather
                for train in simulator.trains:
                    if train['weather'] in ['rain', 'fog']:
                        train['speed'] = max(60, train['speed'] * 0.8)
                st.success("Weather adaptation applied")
            
            elif strategy == "Energy Saving Convoy":
                # Create energy-saving convoy
                base_speed = 80
                for i, train in enumerate(simulator.trains):
                    train['speed'] = base_speed - (i * 2)
                st.success("Energy-saving convoy formed")
            
            elif strategy == "Priority-based Scheduling":
                # Prioritize certain trains
                for train in simulator.trains:
                    if train['type'] in ['Rajdhani', 'Shatabdi']:
                        train['speed'] = min(130, train['speed'] + 10)
                st.success("Priority scheduling applied")
            
            elif strategy == "Dynamic Headway":
                # Dynamic headway adjustment
                for train in simulator.trains:
                    if train['section_occupancy'] > 2:
                        train['speed'] = max(60, train['speed'] - 10)
                st.success("Dynamic headway adjustment applied")

with tab2:
    # WEATHER AI TAB
    st.subheader("🌤️ Weather AI Integration")
    
    col_weather1, col_weather2 = st.columns(2)
    
    with col_weather1:
        st.markdown("### 📍 Real-time Weather Map")
        
        # Create weather map
        m = folium.Map(location=[22.5937, 79.9629], zoom_start=5, tiles="CartoDB dark_matter")
        
        # Add weather zones
        weather_zones = {
            'North': {'lat': 28.0, 'lon': 77.0, 'weather': 'clear', 'size': 100},
            'South': {'lat': 13.0, 'lon': 80.0, 'weather': 'rain', 'size': 150},
            'East': {'lat': 22.0, 'lon': 88.0, 'weather': 'clouds', 'size': 120},
            'West': {'lat': 19.0, 'lon': 73.0, 'weather': 'clear', 'size': 100},
            'Central': {'lat': 23.0, 'lon': 82.0, 'weather': 'fog', 'size': 80}
        }
        
        weather_colors = {
            'clear': '#f1c40f',
            'clouds': '#95a5a6',
            'rain': '#3498db',
            'fog': '#7f8c8d'
        }
        
        weather_icons = {
            'clear': '☀️',
            'clouds': '☁️',
            'rain': '🌧️',
            'fog': '🌫️'
        }
        
        for zone_name, zone_data in weather_zones.items():
            color = weather_colors.get(zone_data['weather'], '#95a5a6')
            icon = weather_icons.get(zone_data['weather'], '☀️')
            
            folium.CircleMarker(
                location=[zone_data['lat'], zone_data['lon']],
                radius=zone_data['size'] / 10,
                popup=f"{zone_name}: {zone_data['weather'].upper()}",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.3
            ).add_to(m)
            
            folium.Marker(
                location=[zone_data['lat'], zone_data['lon']],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 24px;">{icon}</div>'
                ),
                tooltip=f"{zone_name}: {zone_data['weather']}"
            ).add_to(m)
        
        # Add trains with weather effects
        for train in simulator.trains[:15]:  # Limit for performance
            color = weather_colors.get(train['weather'], '#95a5a6')
            
            folium.CircleMarker(
                location=[train['latitude'], train['longitude']],
                radius=5,
                popup=f"{train['name']}<br>Weather: {train['weather']}<br>Speed Factor: {train['weather_effects']['speed_mult']:.2f}",
                color=color,
                fill=True,
                fill_color=color
            ).add_to(m)
        
        folium_static(m, width=400, height=400)
        
        # Weather legend
        st.markdown("#### 🎨 Weather Legend")
        col_leg1, col_leg2 = st.columns(2)
        with col_leg1:
            st.markdown("☀️ **Clear**: Normal operations")
            st.markdown("☁️ **Clouds**: -5% speed")
        with col_leg2:
            st.markdown("🌧️ **Rain**: -20% speed, +30% gap")
            st.markdown("🌫️ **Fog**: -40% speed, +60% gap")
    
    with col_weather2:
        st.markdown("### 📊 Weather Impact Analysis")
        
        # Weather distribution
        weather_dist = {}
        for train in simulator.trains:
            weather = train['weather']
            weather_dist[weather] = weather_dist.get(weather, 0) + 1
        
        if weather_dist:
            fig_weather = px.pie(
                values=list(weather_dist.values()),
                names=list(weather_dist.keys()),
                color=list(weather_dist.keys()),
                color_discrete_map=weather_colors,
                hole=0.4,
                title='Weather Distribution Across Trains'
            )
            fig_weather.update_layout(height=300)
            st.plotly_chart(fig_weather, use_container_width=True)
        
        # Weather alerts
        st.markdown("#### ⚠️ Active Weather Alerts")
        
        weather_alerts = simulator.weather_alerts_history[-5:] if simulator.weather_alerts_history else []
        
        if weather_alerts:
            for alert in reversed(weather_alerts):
                st.warning(f"**{alert['train_no']}** in {alert['location']}: {alert['weather'].upper()} - {alert['effect']}")
        else:
            st.success("✅ No active weather alerts")
        
        # Weather adaptation statistics
        st.markdown("#### 📈 Adaptation Statistics")
        
        col_adapt1, col_adapt2, col_adapt3 = st.columns(3)
        with col_adapt1:
            avg_speed_mult = np.mean([t['weather_effects']['speed_mult'] for t in simulator.trains])
            st.metric("Avg Speed Multiplier", f"{avg_speed_mult:.2f}")
        
        with col_adapt2:
            avg_gap_mult = np.mean([t['weather_effects']['safety_gap_mult'] for t in simulator.trains])
            st.metric("Avg Safety Gap Multiplier", f"{avg_gap_mult:.2f}")
        
        with col_adapt3:
            affected_trains = sum(1 for t in simulator.trains if t['weather'] in ['rain', 'fog'])
            st.metric("Affected Trains", affected_trains)
        
        # Weather prediction and recommendations
        st.markdown("#### 💡 AI Weather Recommendations")
        
        recommendations = []
        
        # Check for severe weather areas
        rain_trains = [t for t in simulator.trains if t['weather'] == 'rain']
        fog_trains = [t for t in simulator.trains if t['weather'] == 'fog']
        
        if rain_trains:
            recommendations.append(f"Reduce speed for {len(rain_trains)} trains in rainy areas")
        
        if fog_trains:
            recommendations.append(f"Increase safety gaps for {len(fog_trains)} trains in foggy areas")
        
        # Check section congestion with bad weather
        sections_with_bad_weather = {}
        for train in simulator.trains:
            if train['weather'] in ['rain', 'fog']:
                section = train['section']
                sections_with_bad_weather[section] = sections_with_bad_weather.get(section, 0) + 1
        
        for section, count in sections_with_bad_weather.items():
            if count >= 2:
                recommendations.append(f"Section {section}: Multiple trains in bad weather - consider rerouting")
        
        if recommendations:
            for rec in recommendations[:3]:
                st.info(rec)
        else:
            st.success("✅ Weather conditions optimal for current operations")

with tab3:
    # PREDICTIVE MAINTENANCE TAB
    st.subheader("🔧 Predictive Maintenance System")
    
    col_maint1, col_maint2 = st.columns(2)
    
    with col_maint1:
        st.markdown("### 📊 Train Health Dashboard")
        
        # Create health gauges for top 5 trains
        trains_with_health = []
        for i, train in enumerate(simulator.trains):
            sensor = simulator.maintenance_sensors.get(i, {})
            if sensor:
                trains_with_health.append({
                    'train': train,
                    'health': sensor.get('health_score', 100),
                    'sensor': sensor
                })
        
        # Sort by health (lowest first)
        trains_with_health.sort(key=lambda x: x['health'])
        
        for train_data in trains_with_health[:5]:
            train = train_data['train']
            health = train_data['health']
            sensor = train_data['sensor']
            
            st.markdown(f"**{train['name']}** ({train['train_no']})")
            
            # Health gauge
            gauge_color = "gauge-healthy" if health >= 80 else "gauge-warning" if health >= 70 else "gauge-critical"
            
            st.markdown(f"""
            <div class="maintenance-gauge">
                <div class="gauge-fill {gauge_color}" style="width: {health}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8;">
                <span>Health: {health:.1f}%</span>
                <span>{'✅ Good' if health >= 80 else '⚠️ Warning' if health >= 70 else '❌ Critical'}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Sensor details (collapsible)
            with st.expander("Sensor Details"):
                col_sens1, col_sens2 = st.columns(2)
                with col_sens1:
                    st.metric("Engine Temp", f"{sensor['engine_temp']:.1f}°C", 
                             delta="Normal" if 80 <= sensor['engine_temp'] <= 90 else "High" if sensor['engine_temp'] > 90 else "Low")
                    st.metric("Vibration", f"{sensor['vibration']:.1f} mm/s",
                             delta="Normal" if sensor['vibration'] <= 3.0 else "High")
                
                with col_sens2:
                    st.metric("Oil Pressure", f"{sensor['oil_pressure']:.1f} psi",
                             delta="Normal" if 40 <= sensor['oil_pressure'] <= 50 else "Low" if sensor['oil_pressure'] < 40 else "High")
                    st.metric("Brake Wear", f"{sensor['brake_wear']:.1f}%",
                             delta="Normal" if sensor['brake_wear'] <= 20 else "High")
            
            st.markdown("---")
        
        # Maintenance statistics
        st.markdown("### 📈 Maintenance Statistics")
        
        health_scores = [s.get('health_score', 100) for s in simulator.maintenance_sensors.values()]
        if health_scores:
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                avg_health = np.mean(health_scores)
                st.metric("Avg Health", f"{avg_health:.1f}%")
            
            with col_stat2:
                critical_trains = sum(1 for h in health_scores if h < 70)
                st.metric("Critical", critical_trains)
            
            with col_stat3:
                days_since_maint = np.mean([(datetime.now() - s.get('last_maintenance', datetime.now())).days 
                                          for s in simulator.maintenance_sensors.values()])
                st.metric("Days Since Maint", f"{days_since_maint:.0f}")
    
    with col_maint2:
        st.markdown("### ⚠️ Maintenance Alerts")
        
        # Generate current alerts
        current_alerts = []
        for i, sensor in simulator.maintenance_sensors.items():
            if sensor['health_score'] < 70:
                train = simulator.trains[i] if i < len(simulator.trains) else None
                if train:
                    issues = []
                    if sensor['engine_temp'] > 100:
                        issues.append(f"Engine temp: {sensor['engine_temp']:.1f}°C")
                    if sensor['vibration'] > 5.0:
                        issues.append(f"Vibration: {sensor['vibration']:.1f} mm/s")
                    if sensor['oil_pressure'] < 30:
                        issues.append(f"Oil pressure: {sensor['oil_pressure']:.1f} psi")
                    if sensor['brake_wear'] > 40:
                        issues.append(f"Brake wear: {sensor['brake_wear']:.1f}%")
                    
                    if issues:
                        current_alerts.append({
                            'train': train,
                            'health': sensor['health_score'],
                            'issues': issues,
                            'urgency': 'high' if sensor['health_score'] < 60 else 'medium'
                        })
        
        if current_alerts:
            st.markdown(f"#### 🔴 {len(current_alerts)} Trains Need Attention")
            
            for alert in current_alerts[:3]:  # Show top 3
                alert_class = "alert-critical" if alert['urgency'] == 'high' else "alert-warning"
                
                st.markdown(f"""
                <div class="alert-panel {alert_class}">
                    <strong>{alert['train']['name']}</strong> ({alert['train']['train_no']})<br>
                    Health: {alert['health']:.1f}% • Urgency: {alert['urgency'].upper()}<br>
                    Issues: {', '.join(alert['issues'])}<br>
                    <small>Recommendation: Schedule maintenance at next major station</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-panel alert-success">
                <strong>✅ All Systems Normal</strong><br>
                No maintenance alerts at this time. All trains operating within normal parameters.
            </div>
            """, unsafe_allow_html=True)
        
        # Predictive maintenance recommendations
        st.markdown("### 💡 Predictive Recommendations")
        
        recommendations = []
        
        # Check for preventive maintenance
        for i, sensor in simulator.maintenance_sensors.items():
            days_since = (datetime.now() - sensor.get('last_maintenance', datetime.now())).days
            if days_since > 30:
                train = simulator.trains[i] if i < len(simulator.trains) else None
                if train:
                    recommendations.append(f"**{train['name']}**: Scheduled maintenance overdue by {days_since - 30} days")
        
        # Check for deteriorating conditions
        for i, sensor in simulator.maintenance_sensors.items():
            if 70 <= sensor['health_score'] < 80:
                train = simulator.trains[i] if i < len(simulator.trains) else None
                if train:
                    recommendations.append(f"**{train['name']}**: Health at {sensor['health_score']:.1f}% - Monitor closely")
        
        if recommendations:
            for rec in recommendations[:3]:
                st.info(rec)
        else:
            st.success("✅ All maintenance schedules up to date")
        
        # Maintenance actions
        st.markdown("### 🛠️ Maintenance Actions")
        
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🔄 Perform Minor Maintenance", use_container_width=True):
                for sensor in simulator.maintenance_sensors.values():
                    sensor['health_score'] = min(100, sensor['health_score'] + 15)
                    sensor['engine_temp'] = max(70, sensor['engine_temp'] - 5)
                    sensor['vibration'] = max(1.0, sensor['vibration'] - 1.0)
                st.success("Minor maintenance performed on all trains")
        
        with col_act2:
            if st.button("🔧 Schedule Major Maintenance", use_container_width=True):
                # Identify worst trains
                worst_trains = []
                for i, sensor in simulator.maintenance_sensors.items():
                    if sensor['health_score'] < 75:
                        train = simulator.trains[i] if i < len(simulator.trains) else None
                        if train:
                            worst_trains.append(train['name'])
                
                if worst_trains:
                    st.warning(f"Scheduled major maintenance for: {', '.join(worst_trains[:3])}")
                else:
                    st.info("No trains currently need major maintenance")
        
        # Maintenance prediction chart
        st.markdown("### 📉 Health Trend Prediction")
        
        # Simulate health degradation prediction
        prediction_data = []
        current_time = datetime.now()
        
        for i in range(7):  # Next 7 days
            day = current_time + timedelta(days=i)
            predicted_health = []
            
            for sensor in simulator.maintenance_sensors.values():
                # Simple degradation model
                daily_degradation = random.uniform(0.5, 2.0)
                health = max(0, sensor['health_score'] - (daily_degradation * i))
                predicted_health.append(health)
            
            if predicted_health:
                avg_health = np.mean(predicted_health)
                prediction_data.append({
                    'day': day.strftime('%a'),
                    'avg_health': avg_health,
                    'critical_count': sum(1 for h in predicted_health if h < 70)
                })
        
        if prediction_data:
            df_pred = pd.DataFrame(prediction_data)
            
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=df_pred['day'],
                y=df_pred['avg_health'],
                mode='lines+markers',
                name='Avg Health',
                line=dict(color='#00dbde', width=3)
            ))
            
            fig_pred.add_trace(go.Bar(
                x=df_pred['day'],
                y=df_pred['critical_count'] * 10,  # Scale for visualization
                name='Critical Trains (scaled)',
                marker_color='#e74c3c',
                opacity=0.3
            ))
            
            fig_pred.update_layout(
                title='7-Day Health Prediction',
                yaxis_title='Health Score / Critical Count',
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            st.plotly_chart(fig_pred, use_container_width=True)

with tab4:
    # GREEN RAILWAYS TAB
    st.subheader("⚡ Energy Efficiency & Green Railways")
    
    col_energy1, col_energy2 = st.columns(2)
    
    with col_energy1:
        st.markdown("### 📊 Energy Consumption Dashboard")
        
        # Energy statistics
        energy_analysis = simulator.get_enhanced_analysis()['energy_analysis']
        
        col_energy_stat1, col_energy_stat2 = st.columns(2)
        with col_energy_stat1:
            st.metric("Total Consumption", f"{energy_analysis['total_consumed_kwh']:.0f} kWh")
            st.metric("Regenerated", f"{energy_analysis['regenerated_kwh']:.1f} kWh")
        
        with col_energy_stat2:
            st.metric("Net Consumption", f"{energy_analysis['net_consumption']:.0f} kWh")
            st.metric("Efficiency Score", f"{energy_analysis['efficiency_score']:.1f}%")
        
        # Energy savings
        savings = energy_analysis['savings_percentage']
        st.markdown(f"#### 💰 Energy Savings: {savings:.1f}%")
        
        # Savings gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=savings,
            title={'text': "Energy Recovery", 'font': {'color': 'white'}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 30], 'tickcolor': 'white'},
                'bar': {'color': '#2ecc71'},
                'steps': [
                    {'range': [0, 10], 'color': 'rgba(231, 76, 60, 0.3)'},
                    {'range': [10, 20], 'color': 'rgba(241, 196, 15, 0.3)'},
                    {'range': [20, 30], 'color': 'rgba(46, 204, 113, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': savings
                }
            }
        ))
        
        fig_gauge.update_layout(
            height=250,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # CO2 savings calculation
        co2_per_kwh = 0.85  # kg CO2 per kWh (Indian grid average)
        co2_saved = energy_analysis['regenerated_kwh'] * co2_per_kwh
        
        st.markdown("#### 🌱 Environmental Impact")
        col_env1, col_env2 = st.columns(2)
        with col_env1:
            st.metric("CO₂ Saved", f"{co2_saved:.1f} kg")
        with col_env2:
            # Equivalent trees
            trees_equivalent = co2_saved / 21.77  # Average tree absorbs 21.77 kg CO2 per year
            st.metric("Equivalent Trees", f"{trees_equivalent:.1f}")
    
    with col_energy2:
        st.markdown("### 🎯 Energy Optimization Strategies")
        
        # Current optimization status
        st.markdown("#### ⚡ Active Optimizations")
        
        optimizations = [
            {"name": "Regenerative Braking", "status": "active", "savings": "15-20%"},
            {"name": "Optimal Speed Profiles", "status": "active", "savings": "10-15%"},
            {"name": "Aerodynamic Design", "status": "passive", "savings": "5-8%"},
            {"name": "Energy-Efficient Routing", "status": "active", "savings": "8-12%"},
            {"name": "Smart Acceleration", "status": "active", "savings": "12-18%"}
        ]
        
        for opt in optimizations:
            status_color = "#2ecc71" if opt['status'] == 'active' else "#95a5a6"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 8px 12px; margin: 5px 0; background: rgba(255,255,255,0.05); 
                        border-radius: 8px; border-left: 3px solid {status_color};">
                <div>
                    <strong>{opt['name']}</strong><br>
                    <small style="color: #94a3b8;">Savings: {opt['savings']}</small>
                </div>
                <div style="color: {status_color};">
                    {opt['status'].upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Energy optimization controls
        st.markdown("#### 🎮 Optimization Controls")
        
        optimization_mode = st.selectbox(
            "Select Optimization Mode:",
            ["Maximum Efficiency", "Balanced", "Performance Priority", "Custom"]
        )
        
        if optimization_mode == "Maximum Efficiency":
            st.info("⚡ Mode: Maximum energy savings with moderate speed reductions")
            target_efficiency = 95
        elif optimization_mode == "Balanced":
            st.info("⚖️ Mode: Balance between energy savings and throughput")
            target_efficiency = 85
        elif optimization_mode == "Performance Priority":
            st.warning("🚀 Mode: Maximum throughput with basic energy optimization")
            target_efficiency = 75
        else:  # Custom
            target_efficiency = st.slider("Target Efficiency:", 50, 100, 85)
            st.info(f"🎯 Custom mode: Targeting {target_efficiency}% efficiency")
        
        if st.button("🔄 Apply Optimization", type="primary", use_container_width=True):
            # Apply optimization to trains
            for train in simulator.trains:
                # Adjust speed based on target efficiency
                efficiency_factor = target_efficiency / 100
                optimal_speed = 80 * efficiency_factor  # 80 km/h is optimal for efficiency
                
                # Gradually adjust to optimal speed
                speed_diff = optimal_speed - train['speed']
                if abs(speed_diff) > 5:
                    adjustment = speed_diff * 0.3  # 30% adjustment
                    train['speed'] = max(40, min(130, train['speed'] + adjustment))
            
            simulator.energy_optimizer['efficiency_score'] = target_efficiency
            st.success(f"Applied {optimization_mode} mode to all trains")
        
        # Energy consumption by train type
        st.markdown("#### 📈 Consumption by Train Type")
        
        consumption_by_type = {}
        for train in simulator.trains:
            train_type = train['type']
            energy = train['energy_consumption'] * (train['speed'] / 100)
            consumption_by_type[train_type] = consumption_by_type.get(train_type, 0) + energy
        
        if consumption_by_type:
            df_consumption = pd.DataFrame({
                'Train Type': list(consumption_by_type.keys()),
                'Energy (kWh)': list(consumption_by_type.values())
            })
            
            fig_consumption = px.bar(
                df_consumption,
                x='Train Type',
                y='Energy (kWh)',
                color='Train Type',
                color_discrete_map={t: EnhancedIndianRailwaysData.TRAIN_TYPES[t]['color'] 
                                   for t in consumption_by_type.keys() 
                                   if t in EnhancedIndianRailwaysData.TRAIN_TYPES}
            )
            fig_consumption.update_layout(
                height=250,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=False
            )
            st.plotly_chart(fig_consumption, use_container_width=True)
        
        # Energy saving tips
        st.markdown("#### 💡 Energy Saving Tips")
        
        tips = [
            "Maintain optimal speed of 80 km/h for best efficiency",
            "Use gradual acceleration and regenerative braking",
            "Reduce idle time at stations",
            "Optimize train weight distribution",
            "Regular maintenance improves energy efficiency by 5-10%"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")

with tab5:
    # PASSENGER AI TAB
    st.subheader("👥 Passenger Information System")
    
    col_pass1, col_pass2 = st.columns(2)
    
    with col_pass1:
        st.markdown("### 🚉 Real-time Arrival Predictions")
        
        # Show predictions for next arrivals
        predictions = list(simulator.passenger_system['predictions'].values())
        
        if predictions:
            # Sort by predicted arrival time
            predictions.sort(key=lambda x: x['predicted_arrival'])
            
            for pred in predictions[:5]:  # Show next 5 arrivals
                time_until = pred['predicted_arrival'] - datetime.now()
                minutes_until = max(0, time_until.total_seconds() / 60)
                
                confidence_color = "#2ecc71" if pred['confidence'] >= 90 else "#f39c12" if pred['confidence'] >= 80 else "#e74c3c"
                
                st.markdown(f"""
                <div class="passenger-panel">
                    <h5>{pred['train_name']} ({pred['train_no']})</h5>
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>To:</strong> {pred['next_station']}<br>
                            <strong>From:</strong> {pred['current_station']}<br>
                            <strong>Platform:</strong> {pred['platform_prediction']}
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 20px; font-weight: bold;">
                                {int(minutes_until)} min
                            </div>
                            <div style="font-size: 12px;">
                                Arrival: {pred['predicted_arrival'].strftime('%H:%M')}
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; display: flex; justify-content: space-between; 
                                align-items: center;">
                        <div style="color: {confidence_color};">
                            {pred['confidence']:.1f}% confidence
                        </div>
                        <div style="color: {'#e74c3c' if pred['delay_prediction'] > 10 else '#f39c12' if pred['delay_prediction'] > 5 else '#2ecc71'};">
                            {pred['delay_prediction']} min delay
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No arrival predictions available")
        
        # Passenger alerts
        st.markdown("### ⚠️ Passenger Alerts")
        
        # Generate sample alerts
        alerts = [
            {"type": "delay", "train": "12673", "station": "MAS", "message": "Delayed by 15 minutes", "severity": "medium"},
            {"type": "platform", "train": "12007", "station": "SBC", "message": "Platform changed to 3C", "severity": "low"},
            {"type": "crowding", "train": "12671", "station": "KPD", "message": "High passenger density", "severity": "medium"}
        ]
        
        for alert in alerts:
            severity_color = {"high": "#e74c3c", "medium": "#f39c12", "low": "#3498db"}[alert['severity']]
            
            st.markdown(f"""
            <div class="alert-panel" style="border-left-color: {severity_color};">
                <strong>Train {alert['train']} at {alert['station']}</strong><br>
                {alert['message']}<br>
                <small>Severity: {alert['severity'].upper()}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col_pass2:
        st.markdown("### 📊 Prediction Accuracy Analytics")
        
        # Accuracy statistics
        accuracy = simulator.passenger_system['accuracy']
        total_pred = simulator.passenger_system['total_predictions']
        accurate_pred = simulator.passenger_system['accurate_predictions']
        
        col_acc1, col_acc2, col_acc3 = st.columns(3)
        with col_acc1:
            st.metric("Accuracy", f"{accuracy:.1f}%")
        with col_acc2:
            st.metric("Total Predictions", total_pred)
        with col_acc3:
            st.metric("Accurate", accurate_pred)
        
        # Accuracy trend
        st.markdown("#### 📈 Accuracy Over Time")
        
        # Simulate accuracy data
        accuracy_data = []
        for i in range(24):  # Last 24 hours
            hour = datetime.now() - timedelta(hours=23-i)
            # Simulate accuracy with some variation
            base_accuracy = 94.7
            variation = random.uniform(-3, 3)
            hour_accuracy = max(80, min(99, base_accuracy + variation))
            accuracy_data.append({'hour': hour.strftime('%H:00'), 'accuracy': hour_accuracy})
        
        df_accuracy = pd.DataFrame(accuracy_data)
        
        fig_accuracy = px.line(
            df_accuracy,
            x='hour',
            y='accuracy',
            title='Prediction Accuracy (Last 24 Hours)',
            markers=True
        )
        
        fig_accuracy.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_tickangle=-45
        )
        
        fig_accuracy.add_hrect(
            y0=95, y1=100, line_width=0,
            fillcolor="rgba(46, 204, 113, 0.2)",
            annotation_text="Excellent", annotation_position="top left"
        )
        
        fig_accuracy.add_hrect(
            y0=90, y1=95, line_width=0,
            fillcolor="rgba(241, 196, 15, 0.2)",
            annotation_text="Good", annotation_position="top left"
        )
        
        st.plotly_chart(fig_accuracy, use_container_width=True)
        
        # Passenger satisfaction metrics
        st.markdown("### 😊 Passenger Satisfaction")
        
        satisfaction_metrics = {
            "Punctuality": 88.5,
            "Information Accuracy": accuracy,
            "Comfort": 92.3,
            "Safety": 96.7,
            "Overall Satisfaction": 91.2
        }
        
        for metric, score in satisfaction_metrics.items():
            col_metric1, col_metric2 = st.columns([2, 3])
            with col_metric1:
                st.markdown(f"**{metric}:**")
            with col_metric2:
                st.progress(score/100, text=f"{score:.1f}%")
        
        # Passenger information controls
        st.markdown("### 🎮 Passenger Information Controls")
        
        info_refresh_rate = st.select_slider(
            "Information Refresh Rate:",
            options=["Real-time", "1 minute", "5 minutes", "15 minutes"],
            value="Real-time"
        )
        
        alert_threshold = st.slider(
            "Delay Alert Threshold (minutes):",
            min_value=5,
            max_value=60,
            value=15,
            step=5
        )
        
        if st.button("📱 Update Passenger Apps", use_container_width=True):
            st.success(f"Updated passenger information with {info_refresh_rate} refresh rate")
        
        # Passenger prediction improvement
        st.markdown("### 🔧 Prediction Improvement")
        
        improvement_options = st.multiselect(
            "Enable Prediction Enhancements:",
            ["Weather Integration", "Historical Patterns", "Real-time Traffic", "Machine Learning", "Crowd-sourced Data"],
            default=["Weather Integration", "Historical Patterns", "Machine Learning"]
        )
        
        if st.button("🚀 Improve Predictions", type="primary", use_container_width=True):
            # Simulate improvement
            improvement_factor = len(improvement_options) * 0.5
            new_accuracy = min(99, accuracy + improvement_factor)
            simulator.passenger_system['accuracy'] = new_accuracy
            
            st.success(f"Prediction accuracy improved to {new_accuracy:.1f}%")

with tab6:
    # UNIFIED DASHBOARD TAB
    st.subheader("📊 Unified AI Control Dashboard")
    
    # Top metrics row
    col_uni1, col_uni2, col_uni3, col_uni4 = st.columns(4)
    
    analysis = simulator.get_enhanced_analysis()
    throughput = analysis['throughput_analysis']
    
    with col_uni1:
        st.markdown("""
        <div class="throughput-metric">
            <h3>THROUGHPUT</h3>
            <div class="value">{:.1f}</div>
            <div>trains/hour</div>
            <div class="trend {}">
                {} {:.1f} vs target
            </div>
        </div>
        """.format(
            throughput['current_throughput'],
            "trend-up" if throughput['efficiency_percentage'] >= 100 else "trend-down",
            "📈" if throughput['efficiency_percentage'] >= 100 else "📉",
            throughput['current_throughput'] - throughput['target_throughput']
        ), unsafe_allow_html=True)
    
    with col_uni2:
        st.markdown("""
        <div class="throughput-metric">
            <h3>ENERGY EFF</h3>
            <div class="value">{:.1f}%</div>
            <div>efficiency score</div>
            <div style="font-size: 12px; margin-top: 5px;">
                {} saved
            </div>
        </div>
        """.format(
            analysis['energy_analysis']['efficiency_score'],
            f"{analysis['energy_analysis']['savings_percentage']:.1f}%"
        ), unsafe_allow_html=True)
    
    with col_uni3:
        st.markdown("""
        <div class="throughput-metric">
            <h3>PREDICTION ACC</h3>
            <div class="value">{:.1f}%</div>
            <div>passenger info</div>
            <div style="font-size: 12px; margin-top: 5px;">
                {} predictions
            </div>
        </div>
        """.format(
            analysis['passenger_analysis']['prediction_accuracy'],
            analysis['passenger_analysis']['total_predictions']
        ), unsafe_allow_html=True)
    
    with col_uni4:
        maint_health = analysis['maintenance_analysis']['avg_health_score']
        health_color = "#2ecc71" if maint_health >= 80 else "#f39c12" if maint_health >= 70 else "#e74c3c"
        
        st.markdown("""
        <div class="throughput-metric" style="background: linear-gradient(135deg, {}40, {}80);">
            <h3>MAINT HEALTH</h3>
            <div class="value" style="color: {};">{:.1f}%</div>
            <div>average health</div>
            <div style="font-size: 12px; margin-top: 5px;">
                {} trains need attention
            </div>
        </div>
        """.format(
            health_color, health_color, health_color,
            maint_health,
            analysis['maintenance_analysis']['trains_needing_maintenance']
        ), unsafe_allow_html=True)
    
    # Middle section - Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Throughput trend
        if throughput['throughput_history']:
            fig_throughput = go.Figure()
            
            fig_throughput.add_trace(go.Scatter(
                x=list(range(len(throughput['throughput_history']))),
                y=throughput['throughput_history'],
                mode='lines',
                name='Throughput',
                line=dict(color='#00dbde', width=3)
            ))
            
            fig_throughput.add_trace(go.Scatter(
                x=[0, len(throughput['throughput_history'])-1],
                y=[throughput['target_throughput'], throughput['target_throughput']],
                mode='lines',
                name='Target',
                line=dict(color='#fc00ff', width=2, dash='dash')
            ))
            
            fig_throughput.update_layout(
                title='Throughput Trend',
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            st.plotly_chart(fig_throughput, use_container_width=True)
    
    with col_chart2:
        # System health radar chart
        categories = ['Throughput', 'Energy Eff', 'Prediction', 'Maintenance', 'Communication']
        
        values = [
            throughput['efficiency_percentage'] / 100,
            analysis['energy_analysis']['efficiency_score'] / 100,
            analysis['passenger_analysis']['prediction_accuracy'] / 100,
            analysis['maintenance_analysis']['avg_health_score'] / 100,
            min(1.0, len(simulator.communication_history) / 100)  # Communication activity
        ]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            line_color='#00dbde',
            fillcolor='rgba(0, 219, 222, 0.3)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title='System Health Radar',
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Bottom section - Alerts and Recommendations
    st.markdown("### ⚠️ System Alerts & Recommendations")
    
    col_alert1, col_alert2, col_alert3 = st.columns(3)
    
    with col_alert1:
        st.markdown("#### 🔴 Critical Alerts")
        
        critical_alerts = []
        
        # Check throughput
        if throughput['efficiency_percentage'] < 80:
            critical_alerts.append(f"Throughput below target: {throughput['efficiency_percentage']:.1f}%")
        
        # Check maintenance
        if analysis['maintenance_analysis']['trains_needing_maintenance'] > 5:
            critical_alerts.append(f"{analysis['maintenance_analysis']['trains_needing_maintenance']} trains need maintenance")
        
        # Check energy
        if analysis['energy_analysis']['efficiency_score'] < 70:
            critical_alerts.append(f"Energy efficiency low: {analysis['energy_analysis']['efficiency_score']:.1f}%")
        
        if critical_alerts:
            for alert in critical_alerts[:2]:
                st.error(alert)
        else:
            st.success("✅ No critical alerts")
    
    with col_alert2:
        st.markdown("#### 🟡 Warnings")
        
        warnings = []
        
        # Check bottlenecks
        if throughput['bottlenecks']:
            warnings.append(f"{len(throughput['bottlenecks'])} sections congested")
        
        # Check prediction accuracy
        if analysis['passenger_analysis']['prediction_accuracy'] < 90:
            warnings.append(f"Prediction accuracy: {analysis['passenger_analysis']['prediction_accuracy']:.1f}%")
        
        # Check weather
        if analysis['weather_analysis']['alerts']:
            warnings.append(f"Weather alerts active")
        
        if warnings:
            for warning in warnings[:2]:
                st.warning(warning)
        else:
            st.success("✅ No warnings")
    
    with col_alert3:
        st.markdown("#### 🔵 Recommendations")
        
        recommendations = []
        
        # Throughput recommendations
        if throughput['efficiency_percentage'] < 90:
            recommendations.append("Increase train frequency in bottleneck sections")
        
        # Energy recommendations
        if analysis['energy_analysis']['efficiency_score'] < 80:
            recommendations.append("Optimize speed profiles for better energy efficiency")
        
        # Maintenance recommendations
        if analysis['maintenance_analysis']['trains_needing_maintenance'] > 0:
            recommendations.append("Schedule maintenance for low-health trains")
        
        # Communication recommendations
        if len(simulator.communication_history) < 50:
            recommendations.append("Increase inter-agent communication for better coordination")
        
        if recommendations:
            for rec in recommendations[:2]:
                st.info(rec)
        else:
            st.success("✅ System operating optimally")
    
    # AI Control Center
    st.markdown("### 🎮 Unified AI Control Center")
    
    ai_mode = st.selectbox(
        "AI Operation Mode:",
        [
            "Fully Autonomous (AI decides everything)",
            "Human-Guided (AI suggests, human approves)",
            "Safety-First (Maximum safety, reduced throughput)",
            "Efficiency-Max (Maximum throughput and efficiency)",
            "Green-Mode (Maximum energy savings)"
        ]
    )
    
    col_control_a, col_control_b, col_control_c = st.columns(3)
    
    with col_control_a:
        if st.button("🤖 Enable Full AI Control", type="primary", use_container_width=True):
            st.success("Full AI control enabled. System now autonomous.")
    
    with col_control_b:
        if st.button("🔄 Optimize All Systems", use_container_width=True):
            st.info("Optimizing all systems for balanced performance...")
    
    with col_control_c:
        if st.button("📊 Generate System Report", use_container_width=True):
            st.success("System report generated and saved to data/system_report.json")

# ========== FOOTER ==========
st.markdown("---")
footer = """
<div style="text-align: center; padding: 30px; color: #94a3b8; font-size: 12px;">
    <p>🚆 Enhanced AI Railway Control System v5.0 | Multi-Agent RL • Weather AI • Predictive Maintenance • Green Railways • Passenger AI</p>
    <p>Active Agents: {agents} | Throughput: {throughput:.1f} trains/hour | Energy Eff: {energy:.1f}% | Prediction Acc: {prediction:.1f}%</p>
    <p style="margin-top: 10px; font-size: 10px;">
        Real-time multi-agent coordination | Weather-adaptive control | Predictive maintenance | Energy optimization | Passenger information
        Last update: {last_update}
    </p>
</div>
""".format(
    agents=simulator.num_trains,
    throughput=analysis['throughput_analysis']['current_throughput'],
    energy=analysis['energy_analysis']['efficiency_score'],
    prediction=analysis['passenger_analysis']['prediction_accuracy'],
    last_update=simulator.last_update.strftime("%H:%M:%S")
)

st.markdown(footer, unsafe_allow_html=True)

# ========== AUTO REFRESH ==========
if st.session_state.get('auto_refresh', True):
    current_time = datetime.now()
    if (current_time - st.session_state.last_update).seconds >= 10:
        st.session_state.last_update = current_time
        st.rerun()

# ========== JAVASCRIPT ==========
st.markdown("""
<script>
    // Auto-refresh for real-time updates
    setTimeout(function() {
        window.location.reload();
    }, 10000); // 10 seconds
</script>
""", unsafe_allow_html=True)
