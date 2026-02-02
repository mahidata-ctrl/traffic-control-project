# train.py - Modified training loop
import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import json
import os

# 1. DQN NETWORK ARCHITECTURE
class DQNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, action_size)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# 2. RAILWAY ENVIRONMENT SIMULATOR (DQN AGENT)
class TrainAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=5000)
        self.gamma = 0.95    # Discount rate
        self.epsilon = 1.0   # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.998
        self.model = DQNetwork(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0005)
        self.criterion = nn.MSELoss()
        self.train_data = {}  # Store train-specific data

    def load_train_data(self, train_id):
        """Load specific train data based on train ID"""
        train_profiles = {
            "12673": {"max_speed": 40, "acceleration": 2.0, "braking": 2.5, "type": "Express"},
            "12674": {"max_speed": 45, "acceleration": 2.2, "braking": 2.3, "type": "Superfast"},
            "12675": {"max_speed": 35, "acceleration": 1.8, "braking": 2.8, "type": "Passenger"},
            "12676": {"max_speed": 50, "acceleration": 2.5, "braking": 2.0, "type": "Rajdhani"},
            "12677": {"max_speed": 38, "acceleration": 2.1, "braking": 2.4, "type": "Mail"}
        }
        
        if train_id in train_profiles:
            self.train_profile = train_profiles[train_id]
            print(f"✅ Loaded profile for Train {train_id}: {self.train_profile['type']}")
            return self.train_profile
        else:
            # Default profile
            self.train_profile = {"max_speed": 40, "acceleration": 2.0, "braking": 2.5, "type": "Express"}
            print(f"⚠️ Using default profile for Train {train_id}")
            return self.train_profile

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.FloatTensor(state)
        act_values = self.model(state)
        return torch.argmax(act_values).item()

    def train_step(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                next_state = torch.FloatTensor(next_state)
                target = (reward + self.gamma * torch.max(self.model(next_state)).item())
            
            state = torch.FloatTensor(state)
            target_f = self.model(state)
            target_f = target_f.clone()
            target_f[action] = target
            
            self.optimizer.zero_grad()
            output = self.model(state)
            loss = self.criterion(output, target_f)
            loss.backward()
            self.optimizer.step()
            
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# 3. ENHANCED TRAINING LOOP WITH TRAIN-SPECIFIC PROFILES
if __name__ == "__main__":
    # Get train ID from user or file
    import sys
    
    if len(sys.argv) > 1:
        train_id = sys.argv[1]
    else:
        train_id = input("Enter Train Number to train model for (e.g., 12673): ").strip()
    
    # States: [Train Speed, Distance to Next Train, Weather Condition, Train Type Factor]
    # Actions: [Decrease Speed (0), Maintain (1), Increase Speed (2)]
    state_size = 4  # Added train type factor
    action_size = 3
    agent = TrainAgent(state_size, action_size)
    
    # Load train-specific profile
    train_profile = agent.load_train_data(train_id)
    
    episodes = 200 
    print("=" * 70)
    print(f"🚀 AI TRAINING STARTED FOR TRAIN {train_id} ({train_profile['type']})")
    print(f"   Max Speed: {train_profile['max_speed']} m/s | Acceleration: {train_profile['acceleration']}")
    print("=" * 70)
    
    training_history = []
    
    for e in range(episodes):
        # Initial State with train-specific factors
        speed_factor = train_profile['max_speed'] / 50.0  # Normalize to 0-1
        accel_factor = train_profile['acceleration'] / 3.0
        state = np.array([
            random.uniform(0.1, 0.7),  # Speed (normalized)
            random.uniform(0.3, 1.0),  # Gap to next train
            random.choice([0, 0.5, 1]),  # Weather (0=Clear, 0.5=Rain, 1=Fog)
            speed_factor  # Train-specific speed capability
        ])
        state = np.reshape(state, [1, state_size])
        
        total_reward = 0
        for time_step in range(50):
            action = agent.act(state)
            
            # Enhanced reward calculation based on train type
            speed = state[0][0] * train_profile['max_speed']
            gap = state[0][1]
            weather = state[0][2]
            
            # Base rewards
            if action == 2 and gap > 0.7:  # Accelerate when gap is large
                reward = 1.5 * accel_factor
            elif action == 0 and gap < 0.3:  # Decelerate when gap is small
                reward = 1.2 * (train_profile['braking'] / 3.0)
            elif action == 1 and 0.4 <= gap <= 0.6:  # Maintain optimal gap
                reward = 1.0
            else:
                reward = -0.3
                
            # Penalty for speeding beyond train's capability
            if speed > train_profile['max_speed'] * 0.9:
                reward -= 2.0
                
            # Weather penalty
            if weather > 0.5:
                reward *= 0.7  # Reduce rewards in bad weather
                
            total_reward += reward
            
            # Next state with train-specific transitions
            next_state = np.array([
                random.uniform(0.1, 0.8) * speed_factor,
                random.uniform(0.3, 1.0),
                random.choice([0, 0.5, 1]),
                speed_factor  # Constant for this train
            ])
            next_state = np.reshape(next_state, [1, state_size])
            done = True if time_step == 49 else False
            
            agent.memory.append((state, action, reward, next_state, done))
            state = next_state
            
        agent.train_step(64)
        
        # Save episode data
        episode_data = {
            "episode": e,
            "epsilon": agent.epsilon,
            "avg_reward": total_reward/50,
            "train_id": train_id,
            "train_type": train_profile['type']
        }
        training_history.append(episode_data)
        
        if e % 20 == 0:
            print(f"📊 Episode: {e:3d}/{episodes} | ε: {agent.epsilon:.4f} | Reward: {total_reward/50:.3f} | Train: {train_id}")

    # SAVE THE TRAINED MODEL WITH TRAIN ID
    model_filename = f"train_model_{train_id}.pth"
    torch.save(agent.model.state_dict(), model_filename)
    
    # Save training history
    history_filename = f"training_history_{train_id}.json"
    with open(history_filename, 'w') as f:
        json.dump(training_history, f, indent=2)
    
    print("=" * 70)
    print(f"✅ TRAINING COMPLETE FOR TRAIN {train_id}!")
    print(f"   Model saved as: {model_filename}")
    print(f"   History saved as: {history_filename}")
    print(f"   Final Exploration Rate: {agent.epsilon:.4f}")
    print("=" * 70)
    
    # Summary
    print("\n🎯 TRAIN PROFILE SUMMARY:")
    print(f"   • Train Number: {train_id}")
    print(f"   • Type: {train_profile['type']}")
    print(f"   • Max Speed: {train_profile['max_speed']} m/s")
    print(f"   • Acceleration: {train_profile['acceleration']} m/s²")
    print(f"   • Braking: {train_profile['braking']} m/s²")
    print(f"   • Episodes Trained: {episodes}")
    print(f"   • Memory Size: {len(agent.memory)}")
    print("=" * 70)
