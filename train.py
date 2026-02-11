import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import pandas as pd
import pickle
import time

# 1. ENHANCED DQN NETWORK ARCHITECTURE
class DQNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, action_size)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.relu(self.fc3(x))
        return self.fc4(x)

# 2. ENHANCED TRAIN AGENT WITH EXPERIENCE REPLAY
class TrainAgent:
    def __init__(self, state_size, action_size, use_pretrained=False):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)  # Larger memory
        self.gamma = 0.99    # Increased discount rate
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.998
        self.learning_rate = 0.001
        self.batch_size = 64
        
        self.model = DQNetwork(state_size, action_size)
        self.target_model = DQNetwork(state_size, action_size)
        self.update_target_model()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        
        # Training history
        self.training_history = {
            'episodes': [],
            'rewards': [],
            'epsilons': [],
            'losses': []
        }
        
        if use_pretrained:
            self.load_model("train_model.pth")

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def act(self, state, training=True):
        if training and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state = torch.FloatTensor(state)
        with torch.no_grad():
            act_values = self.model(state)
        return torch.argmax(act_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return 0
        
        minibatch = random.sample(self.memory, self.batch_size)
        total_loss = 0
        
        states = []
        targets = []
        
        for state, action, reward, next_state, done in minibatch:
            state_tensor = torch.FloatTensor(state)
            next_state_tensor = torch.FloatTensor(next_state)
            
            # Current Q values
            current_q = self.model(state_tensor)[action]
            
            # Calculate target Q value
            with torch.no_grad():
                if done:
                    target = reward
                else:
                    next_q = torch.max(self.target_model(next_state_tensor))
                    target = reward + self.gamma * next_q.item()
            
            # Calculate loss
            target_f = self.model(state_tensor).clone()
            target_f[action] = target
            
            states.append(state_tensor)
            targets.append(target_f)
        
        # Batch optimization
        states = torch.stack(states)
        targets = torch.stack(targets)
        
        self.optimizer.zero_grad()
        outputs = self.model(states)
        loss = self.criterion(outputs, targets)
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss.item()

    def train(self, env, episodes=500, render_every=50):
        print("🚀 AI Training Started: Optimizing Section Throughput...")
        
        for e in range(episodes):
            state = env.reset()
            state = np.reshape(state, [1, self.state_size])
            total_reward = 0
            episode_loss = 0
            steps = 0
            
            for time_step in range(200):  # Increased episode length
                action = self.act(state)
                next_state, reward, done, _ = env.step(action)
                next_state = np.reshape(next_state, [1, self.state_size])
                
                self.remember(state, action, reward, next_state, done)
                loss = self.replay()
                episode_loss += loss if loss else 0
                
                total_reward += reward
                state = next_state
                steps += 1
                
                if done:
                    break
            
            # Update target network every 10 episodes
            if e % 10 == 0:
                self.update_target_model()
            
            # Record training history
            self.training_history['episodes'].append(e)
            self.training_history['rewards'].append(total_reward)
            self.training_history['epsilons'].append(self.epsilon)
            self.training_history['losses'].append(episode_loss / steps if steps > 0 else 0)
            
            if e % render_every == 0:
                print(f"Episode: {e}/{episodes}, "
                      f"Reward: {total_reward:.2f}, "
                      f"Epsilon: {self.epsilon:.3f}, "
                      f"Avg Loss: {episode_loss/steps if steps>0 else 0:.4f}")
        
        self.save_training_history()
        return self.training_history

    def save_model(self, filename):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_history': self.training_history
        }, filename)
        print(f"✅ Model saved as {filename}")

    def load_model(self, filename):
        checkpoint = torch.load(filename)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.training_history = checkpoint['training_history']
        print(f"✅ Model loaded from {filename}")

    def save_training_history(self):
        df = pd.DataFrame(self.training_history)
        df.to_csv('training_history.csv', index=False)
        print("✅ Training history saved to training_history.csv")

    def get_q_values(self, state):
        state = torch.FloatTensor(state)
        with torch.no_grad():
            q_values = self.model(state)
        return q_values.numpy()

# 3. ENHANCED TRAINING LOOP WITH ENVIRONMENT INTEGRATION
if __name__ == "__main__":
    from rail_env import TrainTrafficEnv
    
    # Initialize environment
    env = TrainTrafficEnv()
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    
    # Initialize agent
    agent = TrainAgent(state_size, action_size)
    
    # Train agent
    episodes = 500
    training_history = agent.train(env, episodes=episodes, render_every=50)
    
    # Save the trained model
    agent.save_model("train_model_enhanced.pth")
    
    # Test the trained agent
    print("\n🧪 Testing trained agent...")
    state = env.reset()
    total_test_reward = 0
    
    for _ in range(100):
        state_tensor = np.reshape(state, [1, state_size])
        action = agent.act(state_tensor, training=False)
        next_state, reward, done, _ = env.step(action)
        total_test_reward += reward
        state = next_state
        
        if done:
            break
    
    print(f"✅ Test complete. Total reward: {total_test_reward}")
    print("🚆 AI Training Complete!")
