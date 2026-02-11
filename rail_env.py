import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from datetime import datetime, timedelta

class TrainTrafficEnv(gym.Env):
    def __init__(self, route_length=1000, num_stations=5):
        super(TrainTrafficEnv, self).__init__()
        
        # Actions: 0=Decelerate, 1=Maintain, 2=Accelerate
        self.action_space = spaces.Discrete(3)
        
        # Enhanced state: [Position, Speed, Distance to next train, 
        #                  Time pressure, Weather condition, Track condition]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([route_length, 40, 200, 1, 1, 1], dtype=np.float32),
            dtype=np.float32
        )
        
        self.route_length = route_length
        self.num_stations = num_stations
        self.station_positions = np.linspace(0, route_length, num_stations + 1)[1:]
        
        # Weather and track conditions
        self.weather_conditions = ['clear', 'rain', 'fog', 'storm']
        self.track_conditions = ['normal', 'maintenance', 'slippery']
        
        self.reset()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Initialize train with realistic values
        self.position = 0.0
        self.speed = random.uniform(10, 25)  # m/s
        self.distance_to_next = random.uniform(100, 200)  # meters
        self.time_pressure = random.uniform(0, 1)
        
        # Initialize weather and track
        self.weather = random.choice([0, 0.33, 0.66, 1])  # Normalized
        self.track_condition = random.choice([0, 0.5, 1])  # Normalized
        
        # Station tracking
        self.current_station_idx = 0
        self.schedule_time = datetime.now()
        self.arrival_times = []
        
        return self._get_state(), {}
    
    def _get_state(self):
        return np.array([
            self.position,
            self.speed,
            self.distance_to_next,
            self.time_pressure,
            self.weather,
            self.track_condition
        ], dtype=np.float32)
    
    def _get_weather_effect(self):
        """Calculate speed multiplier based on weather"""
        if self.weather < 0.33:  # Clear
            return 1.0
        elif self.weather < 0.66:  # Rain
            return 0.8
        elif self.weather < 0.99:  # Fog
            return 0.6
        else:  # Storm
            return 0.4
    
    def _get_track_effect(self):
        """Calculate speed multiplier based on track condition"""
        if self.track_condition < 0.33:  # Normal
            return 1.0
        elif self.track_condition < 0.66:  # Maintenance
            return 0.7
        else:  # Slippery
            return 0.5
    
    def step(self, action):
        pos, speed, dist_next, time_pressure, weather, track = self._get_state()
        
        # Apply weather and track effects
        weather_multiplier = self._get_weather_effect()
        track_multiplier = self._get_track_effect()
        max_speed = 40 * weather_multiplier * track_multiplier
        
        # AI Logic for Speed adjustment
        if action == 0:  # Decelerate
            speed -= random.uniform(0.5, 2.0)
        elif action == 2:  # Accelerate
            speed += random.uniform(0.5, 2.0)
        
        # Apply speed limits
        speed = np.clip(speed, 5, max_speed)
        
        # Update position
        pos += speed
        
        # Update distance to next train (simulated)
        dist_next -= speed * random.uniform(0.8, 1.2)
        if dist_next < 0:
            dist_next = random.uniform(150, 250)
        
        # Check if arriving at station
        if self.current_station_idx < len(self.station_positions):
            next_station = self.station_positions[self.current_station_idx]
            if pos >= next_station:
                self.current_station_idx += 1
                self.arrival_times.append(datetime.now())
        
        # Update time pressure (more pressure as time progresses)
        elapsed_time = (datetime.now() - self.schedule_time).total_seconds() / 3600
        time_pressure = min(1.0, elapsed_time / 2.0)  # 2 hour schedule
        
        # Random weather changes
        if random.random() < 0.1:  # 10% chance of weather change
            self.weather = random.choice([0, 0.33, 0.66, 1])
        
        # Enhanced Reward Logic
        reward = 0
        
        # Speed reward (encourage optimal speed)
        optimal_speed = 25 * weather_multiplier * track_multiplier
        speed_deviation = abs(speed - optimal_speed)
        reward += 10 * (1 - speed_deviation / optimal_speed)
        
        # Safety reward (maintain safe distance)
        safe_distance = 50 + speed * 2  # 2 seconds following distance
        if dist_next < safe_distance:
            penalty = max(0, (safe_distance - dist_next) / safe_distance)
            reward -= 50 * penalty
        else:
            reward += 20 * min(1, dist_next / 200)
        
        # Station arrival bonus
        if self.current_station_idx > 0 and len(self.arrival_times) == self.current_station_idx:
            reward += 100
            # Schedule adherence bonus
            schedule_deviation = abs(elapsed_time - (self.current_station_idx * 0.4))  # 0.4 hours per station
            reward += 50 * (1 - schedule_deviation)
        
        # Energy efficiency reward
        energy_efficiency = speed / (speed ** 2 * 0.01 + 10)  # Simplified model
        reward += 5 * energy_efficiency
        
        # Penalize excessive acceleration changes
        if action != 1:  # If not maintaining speed
            reward -= 2
        
        # Check completion
        done = pos >= self.route_length or self.current_station_idx >= self.num_stations
        
        # Update state
        self.position = pos % self.route_length if not done else self.route_length
        self.speed = speed
        self.distance_to_next = max(10, dist_next) if not done else 200
        self.time_pressure = time_pressure
        
        next_state = self._get_state()
        
        return next_state, reward, done, False, {
            'position': self.position,
            'speed': self.speed,
            'distance_to_next': self.distance_to_next,
            'current_station': self.current_station_idx,
            'weather': self.weather,
            'track_condition': self.track_condition,
            'arrival_times': self.arrival_times.copy()
        }
    
    def render(self, mode='human'):
        print(f"Position: {self.position:.1f}m | "
              f"Speed: {self.speed:.1f}m/s | "
              f"Next Train: {self.distance_to_next:.1f}m | "
              f"Station: {self.current_station_idx}/{self.num_stations}")
    
    def get_station_info(self, station_idx):
        if station_idx < len(self.station_positions):
            return {
                'position': self.station_positions[station_idx],
                'name': f"Station {station_idx + 1}",
                'arrived': station_idx < self.current_station_idx
            }
        return None
