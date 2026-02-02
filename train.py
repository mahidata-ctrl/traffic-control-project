import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

# 1. DQN NETWORK ARCHITECTURE
class DQNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# 

# 2. RAILWAY ENVIRONMENT SIMULATOR (DQN AGENT)
class TrainAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # Discount rate
        self.epsilon = 1.0   # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.model = DQNetwork(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

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

# 3. TRAINING LOOP
if __name__ == "__main__":
    # States: [Train Speed, Distance to Next Train, Weather Condition]
    # Actions: [Decrease Speed, Maintain, Increase Speed]
    state_size = 3 
    action_size = 3
    agent = TrainAgent(state_size, action_size)
    episodes = 100 

    print("🚀 AI Training Started: Optimizing Section Throughput...")
    
    for e in range(episodes):
        # Initial State: Random Speed (0-1), Random Gap (0.5-1), Weather (0 or 1)
        state = np.array([random.uniform(0.1, 0.8), random.uniform(0.5, 1.0), random.choice([0, 1])])
        state = np.reshape(state, [1, state_size])
        
        for time_step in range(50):
            action = agent.act(state)
            
            # Logic: If gap is large and speed is low, Reward for increasing speed
            # Reward Calculation: Throughput Optimization
            reward = 1 if action == 2 and state[0][1] > 0.7 else -1
            
            next_state = np.array([random.uniform(0.1, 0.8), random.uniform(0.5, 1.0), random.choice([0, 1])])
            next_state = np.reshape(next_state, [1, state_size])
            done = True if time_step == 49 else False
            
            agent.memory.append((state, action, reward, next_state, done))
            state = next_state
            
        agent.train_step(32)
        if e % 10 == 0:
            print(f"Episode: {e}/{episodes}, Exploration Rate: {agent.epsilon:.2f}")

    # SAVE THE TRAINED MODEL
    torch.save(agent.model.state_size(), "train_model.pth")
    print("✅ Training Complete. Model saved as 'train_model.pth'")
