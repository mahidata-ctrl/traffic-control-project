import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from datetime import datetime, timedelta
import json
import math
from typing import Dict, List, Tuple, Optional

class EnhancedRailwayEnv(gym.Env):
    """Enhanced railway environment for Indian trains"""
    
    metadata = {'render.modes': ['human', 'rgb_array']}
    
    def __init__(self, route_length=2000, num_stations=8, num_trains=3):
        super(EnhancedRailwayEnv, self).__init__()
        
        # Action space: 0=Emergency Stop, 1=Decelerate, 2=Maintain, 3=Accelerate, 4=Full Speed
        self.action_space = spaces.Discrete(5)
        
        # Enhanced observation space
        # [position, speed, distance_to_next, time_pressure, weather, track_condition,
        #  energy_level, station_proximity, train_density, signal_status]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([route_length, 40, 500, 1, 1, 1, 100, 1, 10, 3], dtype=np.float32),
            dtype=np.float32
        )
        
        # Environment parameters
        self.route_length = route_length
        self.num_stations = num_stations
        self.num_trains = num_trains
        
        # Indian railway stations with coordinates
        self.stations = self._load_indian_stations()
        self.station_positions = np.linspace(0, route_length, num_stations + 1)[1:]
        
        # Multiple trains
        self.trains = []
        self.current_train_idx = 0
        
        # Weather conditions
        self.weather_conditions = {
            0: {'name': 'Clear', 'effect': 1.0, 'color': '☀️'},
            1: {'name': 'Rain', 'effect': 0.7, 'color': '🌧️'},
            2: {'name': 'Fog', 'effect': 0.5, 'color': '🌫️'},
            3: {'name': 'Storm', 'effect': 0.3, 'color': '⛈️'}
        }
        
        # Track conditions
        self.track_conditions = {
            0: {'name': 'Excellent', 'effect': 1.0, 'color': '🟢'},
            1: {'name': 'Good', 'effect': 0.9, 'color': '🟡'},
            2: {'name': 'Fair', 'effect': 0.7, 'color': '🟠'},
            3: {'name': 'Poor', 'effect': 0.5, 'color': '🔴'}
        }
        
        # Signals and blocks
        self.blocks = self._create_blocks()
        self.signals = {block: 'GREEN' for block in self.blocks}
        
        # Energy parameters
        self.energy_consumption_rate = 0.1
        self.regeneration_rate = 0.05
        
        # Passenger parameters
        self.passenger_count = random.randint(100, 500)
        
        # Initialize
        self.reset()
    
    def _load_indian_stations(self):
        """Load Indian railway stations"""
        return {
            'MAS': {'name': 'Chennai Central', 'lat': 13.0827, 'lon': 80.2707, 'importance': 10},
            'KPD': {'name': 'Katpadi Junction', 'lat': 12.9702, 'lon': 79.1590, 'importance': 8},
            'JTJ': {'name': 'Jolarpettai Junction', 'lat': 12.5667, 'lon': 78.5667, 'importance': 7},
            'SA': {'name': 'Salem Junction', 'lat': 11.6643, 'lon': 78.1460, 'importance': 8},
            'CBE': {'name': 'Coimbatore Junction', 'lat': 11.0168, 'lon': 76.9558, 'importance': 9},
            'TUP': {'name': 'Tiruppur', 'lat': 11.1075, 'lon': 77.3398, 'importance': 6},
            'ED': {'name': 'Erode Junction', 'lat': 11.3420, 'lon': 77.7172, 'importance': 7},
            'PGT': {'name': 'Palakkad Junction', 'lat': 10.7654, 'lon': 76.6600, 'importance': 8}
        }
    
    def _create_blocks(self):
        """Create railway blocks for signaling"""
        block_length = self.route_length / 20  # 20 blocks
        return [(i * block_length, (i + 1) * block_length) for i in range(20)]
    
    def _get_current_block(self, position):
        """Get current railway block"""
        for idx, (start, end) in enumerate(self.blocks):
            if start <= position < end:
                return idx
        return len(self.blocks) - 1
    
    def _update_signals(self):
        """Update signal status based on train positions"""
        # Reset all signals to green
        self.signals = {block: 'GREEN' for block in range(len(self.blocks))}
        
        # Set signals to red for blocks occupied by trains
        for train in self.trains:
            block_idx = self._get_current_block(train['position'])
            
            # Set current block and next block to yellow
            self.signals[block_idx] = 'RED'
            if block_idx + 1 < len(self.blocks):
                self.signals[block_idx + 1] = 'YELLOW'
            if block_idx + 2 < len(self.blocks):
                self.signals[block_idx + 2] = 'YELLOW'
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Initialize multiple trains
        self.trains = []
        for i in range(self.num_trains):
            train = {
                'id': i + 1,
                'position': random.uniform(0, 200),
                'speed': random.uniform(10, 25),
                'acceleration': 0,
                'distance_to_next': random.uniform(100, 300),
                'time_pressure': random.uniform(0, 0.3),
                'weather': random.choice([0, 1, 2, 3]),
                'track_condition': random.choice([0, 1, 2, 3]),
                'energy': 100.0,
                'station_idx': 0,
                'arrival_times': [],
                'delay': 0,
                'passengers': random.randint(50, 300),
                'status': 'RUNNING',
                'route': list(self.stations.keys())[:self.num_stations]
            }
            self.trains.append(train)
        
        # Set current train
        self.current_train_idx = 0
        
        # Update signals
        self._update_signals()
        
        # Calculate train density
        train_density = self._calculate_train_density()
        
        # Get current state for the first train
        return self._get_state(0), {}
    
    def _get_state(self, train_idx):
        """Get observation state for a specific train"""
        train = self.trains[train_idx]
        
        # Calculate station proximity
        if train['station_idx'] < len(train['route']):
            station_code = train['route'][train['station_idx']]
            station_pos = self.station_positions[train['station_idx']]
            station_proximity = 1 - min(1, abs(train['position'] - station_pos) / 200)
        else:
            station_proximity = 0
        
        # Calculate signal status (0=GREEN, 1=YELLOW, 2=RED)
        current_block = self._get_current_block(train['position'])
        signal_map = {'GREEN': 0, 'YELLOW': 1, 'RED': 2}
        signal_status = signal_map.get(self.signals.get(current_block, 'GREEN'), 0)
        
        # Calculate train density in the area
        train_density = self._calculate_train_density()
        
        return np.array([
            train['position'] / self.route_length,  # Normalized position
            train['speed'] / 40.0,  # Normalized speed
            train['distance_to_next'] / 500.0,  # Normalized distance
            train['time_pressure'],
            train['weather'] / 3.0,  # Normalized weather
            train['track_condition'] / 3.0,  # Normalized track condition
            train['energy'] / 100.0,  # Normalized energy
            station_proximity,
            train_density / 10.0,  # Normalized density
            signal_status / 2.0  # Normalized signal status
        ], dtype=np.float32)
    
    def _calculate_train_density(self):
        """Calculate train density in the current area"""
        if len(self.trains) <= 1:
            return 0
        
        positions = [t['position'] for t in self.trains]
        avg_distance = np.mean([abs(p1 - p2) for i, p1 in enumerate(positions) for p2 in positions[i+1:]])
        
        # Higher density if trains are close together
        if avg_distance < 100:
            return 5
        elif avg_distance < 200:
            return 3
        elif avg_distance < 300:
            return 1
        return 0
    
    def _get_weather_effect(self, weather):
        """Get speed multiplier based on weather"""
        return self.weather_conditions[weather]['effect']
    
    def _get_track_effect(self, track):
        """Get speed multiplier based on track condition"""
        return self.track_conditions[track]['effect']
    
    def step(self, action):
        train = self.trains[self.current_train_idx]
        
        # Apply action
        if action == 0:  # Emergency stop
            train['acceleration'] = -5.0
        elif action == 1:  # Decelerate
            train['acceleration'] = -1.5
        elif action == 2:  # Maintain
            train['acceleration'] = 0.0
        elif action == 3:  # Accelerate
            train['acceleration'] = 1.5
        elif action == 4:  # Full speed
            train['acceleration'] = 3.0
        
        # Apply physics
        old_speed = train['speed']
        train['speed'] += train['acceleration']
        
        # Apply weather and track effects
        weather_mult = self._get_weather_effect(train['weather'])
        track_mult = self._get_track_effect(train['track_condition'])
        max_speed = 40 * weather_mult * track_mult
        
        # Apply speed limits
        train['speed'] = np.clip(train['speed'], 0, max_speed)
        
        # Update position
        train['position'] += train['speed']
        
        # Update distance to next train
        if self.current_train_idx < len(self.trains) - 1:
            next_train = self.trains[self.current_train_idx + 1]
            train['distance_to_next'] = max(0, next_train['position'] - train['position'])
        else:
            train['distance_to_next'] = random.uniform(100, 300)
        
        # Update energy
        energy_used = abs(train['acceleration']) * self.energy_consumption_rate
        if train['acceleration'] < 0:  # Regenerative braking
            energy_regen = abs(train['acceleration']) * self.regeneration_rate
            train['energy'] = min(100, train['energy'] - energy_used + energy_regen)
        else:
            train['energy'] = max(0, train['energy'] - energy_used)
        
        # Update time pressure
        train['time_pressure'] = min(1.0, train['time_pressure'] + 0.01)
        
        # Check station arrival
        reward = self._check_station_arrival(train)
        
        # Check for completion
        done = train['position'] >= self.route_length or train['station_idx'] >= len(train['route'])
        
        # Safety penalty for close distance
        if train['distance_to_next'] < 50:
            reward -= 20 * (50 - train['distance_to_next']) / 50
        
        # Penalize excessive speed changes
        if abs(train['acceleration']) > 2:
            reward -= 5
        
        # Energy efficiency bonus
        if train['energy'] > 70:
            reward += 5
        elif train['energy'] < 30:
            reward -= 10
        
        # Signal compliance
        current_block = self._get_current_block(train['position'])
        if self.signals[current_block] == 'RED' and train['speed'] > 5:
            reward -= 50  # Heavy penalty for running red signal
        
        # Passenger comfort (smooth acceleration)
        if abs(train['acceleration']) < 0.5:
            reward += 2
        
        # Update signals
        self._update_signals()
        
        # Rotate to next train
        self.current_train_idx = (self.current_train_idx + 1) % len(self.trains)
        
        # Get next state
        next_state = self._get_state(self.current_train_idx)
        
        # Additional info
        info = {
            'train_id': train['id'],
            'position': train['position'],
            'speed': train['speed'],
            'distance_to_next': train['distance_to_next'],
            'energy': train['energy'],
            'current_station': train['station_idx'],
            'weather': self.weather_conditions[train['weather']]['name'],
            'track_condition': self.track_conditions[train['track_condition']]['name'],
            'signal_status': self.signals[current_block],
            'delay': train['delay']
        }
        
        return next_state, reward, done, False, info
    
    def _check_station_arrival(self, train):
        """Check if train has arrived at a station and calculate reward"""
        reward = 0
        
        if train['station_idx'] < len(train['route']):
            station_code = train['route'][train['station_idx']]
            station_pos = self.station_positions[train['station_idx']]
            
            if train['position'] >= station_pos:
                # Station arrival bonus
                arrival_bonus = 100
                
                # Punctuality bonus/penalty
                schedule_time = (train['station_idx'] + 1) * 0.5  # 0.5 hours per station
                actual_time = train['time_pressure'] * 2  # Convert to hours
                time_diff = abs(actual_time - schedule_time)
                
                if time_diff < 0.1:  # Within 6 minutes
                    punctuality_bonus = 50
                    train['delay'] = 0
                elif time_diff < 0.25:  # Within 15 minutes
                    punctuality_bonus = 20
                    train['delay'] = time_diff * 60  # Convert to minutes
                else:
                    punctuality_bonus = -30
                    train['delay'] = time_diff * 60
                
                # Passenger satisfaction
                passenger_bonus = train['passengers'] * 0.1
                
                # Smooth stopping bonus
                if train['speed'] < 5:
                    stopping_bonus = 20
                else:
                    stopping_bonus = -20
                
                reward = arrival_bonus + punctuality_bonus + passenger_bonus + stopping_bonus
                
                # Update train state
                train['station_idx'] += 1
                train['arrival_times'].append(datetime.now())
                train['time_pressure'] = 0  # Reset time pressure
                
                # Random weather change after station
                if random.random() < 0.2:
                    train['weather'] = random.choice([0, 1, 2, 3])
                
                # Random track condition change
                if random.random() < 0.1:
                    train['track_condition'] = random.choice([0, 1, 2, 3])
        
        return reward
    
    def render(self, mode='human'):
        """Render the environment"""
        if mode == 'human':
            train = self.trains[self.current_train_idx]
            
            print(f"\n{'='*60}")
            print(f"🚆 TRAIN {train['id']} - ENVIRONMENT STATUS")
            print(f"{'='*60}")
            
            # Position and speed
            print(f"📍 Position: {train['position']:.1f}m / {self.route_length}m")
            print(f"🚀 Speed: {train['speed']:.1f} m/s ({train['speed']*3.6:.1f} km/h)")
            print(f"📏 Distance to next train: {train['distance_to_next']:.1f}m")
            
            # Conditions
            weather_info = self.weather_conditions[train['weather']]
            track_info = self.track_conditions[train['track_condition']]
            print(f"🌤️ Weather: {weather_info['color']} {weather_info['name']} "
                  f"(Speed factor: {weather_info['effect']:.1f})")
            print(f"🛤️ Track: {track_info['color']} {track_info['name']} "
                  f"(Speed factor: {track_info['effect']:.1f})")
            
            # Energy and signals
            current_block = self._get_current_block(train['position'])
            print(f"⚡ Energy: {train['energy']:.1f}%")
            print(f"🚦 Signal: {self.signals[current_block]} "
                  f"(Block {current_block + 1}/{len(self.blocks)})")
            
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
            print(f"{'='*60}")
    
    def get_train_info(self, train_idx):
        """Get detailed information about a train"""
        if train_idx < len(self.trains):
            train = self.trains[train_idx]
            
            # Calculate ETA to next station
            eta = None
            if train['station_idx'] < len(train['route']):
                station_pos = self.station_positions[train['station_idx']]
                distance = station_pos - train['position']
                if train['speed'] > 0:
                    eta = distance / train['speed'] / 60  # In minutes
            
            return {
                'id': train['id'],
                'position': train['position'],
                'speed': train['speed'],
                'speed_kmh': train['speed'] * 3.6,
                'distance_to_next': train['distance_to_next'],
                'energy': train['energy'],
                'current_station_idx': train['station_idx'],
                'current_station': train['route'][train['station_idx']] if train['station_idx'] < len(train['route']) else 'TERMINAL',
                'next_station': train['route'][train['station_idx'] + 1] if train['station_idx'] + 1 < len(train['route']) else 'TERMINAL',
                'weather': self.weather_conditions[train['weather']],
                'track_condition': self.track_conditions[train['track_condition']],
                'delay': train['delay'],
                'passengers': train['passengers'],
                'status': train['status'],
                'eta_minutes': eta,
                'arrival_times': train['arrival_times']
            }
        return None
    
    def get_all_trains_info(self):
        """Get information for all trains"""
        return [self.get_train_info(i) for i in range(len(self.trains))]
    
    def get_environment_stats(self):
        """Get environment statistics"""
        return {
            'total_trains': len(self.trains),
            'route_length': self.route_length,
            'stations': len(self.station_positions),
            'blocks': len(self.blocks),
            'average_speed': np.mean([t['speed'] for t in self.trains]),
            'average_energy': np.mean([t['energy'] for t in self.trains]),
            'total_passengers': sum([t['passengers'] for t in self.trains])
        }

# ========== SIMPLE ENVIRONMENT (Backward Compatible) ==========
class TrainTrafficEnv(gym.Env):
    """Simple environment for backward compatibility"""
    def __init__(self):
        super(TrainTrafficEnv, self).__init__()
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=1000, shape=(3,), dtype=np.float32)
        self.reset()
    
    def reset(self, seed=None, options=None):
        self.state = np.array([0, 15, 100], dtype=np.float32)
        return self.state, {}
    
    def step(self, action):
        pos, speed, dist = self.state
        
        if action == 0: speed -= 1
        elif action == 2: speed += 1
        speed = np.clip(speed, 5, 40)
        
        pos += speed
        dist -= 1
        
        reward = (speed * 0.5)
        if dist < 20: reward -= 50
        if dist > 20 and dist < 40: reward += 20
        
        done = pos >= 1000
        self.state = np.array([pos % 1000, speed, dist if dist > 0 else 100], dtype=np.float32)
        return self.state, reward, done, False, {}

# ========== TEST FUNCTION ==========
if __name__ == "__main__":
    print("🧪 Testing Enhanced Railway Environment...")
    
    env = EnhancedRailwayEnv()
    state, _ = env.reset()
    
    print(f"Initial State Shape: {state.shape}")
    print(f"Action Space: {env.action_space}")
    print(f"Observation Space: {env.observation_space}")
    
    # Test a few steps
    for step in range(5):
        action = env.action_space.sample()
        next_state, reward, done, _, info = env.step(action)
        
        print(f"\nStep {step + 1}:")
        print(f"  Action: {action}")
        print(f"  Reward: {reward:.2f}")
        print(f"  Done: {done}")
        print(f"  Info: {info}")
        
        if done:
            break
    
    print("\n✅ Environment test complete!")
