import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import pandas as pd
import pickle
import time
import json
import os
from datetime import datetime

# ========== ENHANCED DQN NETWORK ==========
class DQNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, 64)
        self.fc5 = nn.Linear(64, action_size)
        
        self.dropout1 = nn.Dropout(0.3)
        self.dropout2 = nn.Dropout(0.3)
        
        # Batch normalization
        self.bn1 = nn.BatchNorm1d(256)
        self.bn2 = nn.BatchNorm1d(256)
        self.bn3 = nn.BatchNorm1d(128)
        
    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        x = torch.relu(self.bn3(self.fc3(x)))
        x = torch.relu(self.fc4(x))
        return self.fc5(x)

# ========== PRIORITIZED EXPERIENCE REPLAY ==========
class PrioritizedReplayBuffer:
    def __init__(self, capacity, alpha=0.6, beta=0.4):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        self.alpha = alpha
        self.beta = beta
        self.pos = 0
        self.max_priority = 1.0
        
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
        self.priorities.append(self.max_priority)
        
    def sample(self, batch_size):
        if len(self.buffer) < batch_size:
            return random.sample(self.buffer, len(self.buffer)), np.ones(len(self.buffer)), np.arange(len(self.buffer))
        
        priorities = np.array(self.priorities) ** self.alpha
        probs = priorities / priorities.sum()
        
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        samples = [self.buffer[i] for i in indices]
        
        # Calculate importance sampling weights
        total = len(self.buffer)
        weights = (total * probs[indices]) ** (-self.beta)
        weights = weights / weights.max()
        
        return samples, weights, indices
    
    def update_priorities(self, indices, priorities):
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority + 1e-5
            self.max_priority = max(self.max_priority, priority)
    
    def __len__(self):
        return len(self.buffer)

# ========== ENHANCED TRAIN AGENT ==========
class EnhancedTrainAgent:
    def __init__(self, state_size, action_size, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.state_size = state_size
        self.action_size = action_size
        self.device = device
        
        # Double DQN with target network
        self.policy_net = DQNetwork(state_size, action_size).to(device)
        self.target_net = DQNetwork(state_size, action_size).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Prioritized experience replay
        self.memory = PrioritizedReplayBuffer(capacity=100000)
        
        # Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.0005
        self.batch_size = 128
        self.target_update = 10
        self.tau = 0.01  # For soft updates
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.criterion = nn.SmoothL1Loss()  # Huber loss
        
        # Training history
        self.training_history = {
            'episode': [], 'total_reward': [], 'avg_loss': [],
            'epsilon': [], 'avg_q_value': [], 'steps': []
        }
        
        self.episode = 0
        
    def act(self, state, training=True):
        if training and random.random() < self.epsilon:
            return random.randrange(self.action_size)
        
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.policy_net(state)
        return torch.argmax(q_values).item()
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.push(state, action, reward, next_state, done)
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return 0, np.zeros(self.batch_size)
        
        # Sample from prioritized replay buffer
        samples, weights, indices = self.memory.sample(self.batch_size)
        
        states, actions, rewards, next_states, dones = zip(*samples)
        
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        weights = torch.FloatTensor(weights).unsqueeze(1).to(self.device)
        
        # Current Q values
        current_q = self.policy_net(states).gather(1, actions)
        
        # Double DQN: Use policy net to select action, target net to evaluate
        with torch.no_grad():
            next_actions = self.policy_net(next_states).argmax(1).unsqueeze(1)
            next_q = self.target_net(next_states).gather(1, next_actions)
            target_q = rewards + (1 - dones) * self.gamma * next_q
        
        # Compute TD errors for prioritization
        td_errors = (target_q - current_q).abs().detach().cpu().numpy()
        
        # Update priorities
        self.memory.update_priorities(indices, td_errors.squeeze())
        
        # Compute loss with importance sampling weights
        loss = (weights * self.criterion(current_q, target_q)).mean()
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        
        self.optimizer.step()
        
        # Soft update target network
        self.soft_update()
        
        return loss.item(), td_errors
    
    def soft_update(self):
        """Soft update of the target network parameters"""
        for target_param, policy_param in zip(self.target_net.parameters(), self.policy_net.parameters()):
            target_param.data.copy_(self.tau * policy_param.data + (1.0 - self.tau) * target_param.data)
    
    def train(self, env, episodes=1000, save_every=50, render_every=100):
        print("🚀 Enhanced AI Training Started: Optimizing Indian Railways Throughput...")
        print(f"📊 State Size: {self.state_size}, Action Size: {self.action_size}")
        print(f"⚙️ Device: {self.device}")
        
        start_time = time.time()
        best_reward = -float('inf')
        
        for episode in range(episodes):
            state = env.reset()
            state = np.reshape(state, [1, self.state_size])
            total_reward = 0
            total_loss = 0
            total_q = 0
            steps = 0
            
            done = False
            while not done and steps < 1000:  # Max steps per episode
                action = self.act(state)
                next_state, reward, done, _ = env.step(action)
                next_state = np.reshape(next_state, [1, self.state_size])
                
                self.remember(state, action, reward, next_state, done)
                
                loss, td_errors = self.replay()
                total_loss += loss if loss else 0
                
                # Calculate average Q-value
                with torch.no_grad():
                    state_tensor = torch.FloatTensor(state).to(self.device)
                    q_values = self.policy_net(state_tensor)
                    total_q += q_values[0][action].item()
                
                total_reward += reward
                state = next_state
                steps += 1
            
            # Decay epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            
            # Record training history
            self.training_history['episode'].append(episode)
            self.training_history['total_reward'].append(total_reward)
            self.training_history['avg_loss'].append(total_loss / steps if steps > 0 else 0)
            self.training_history['epsilon'].append(self.epsilon)
            self.training_history['avg_q_value'].append(total_q / steps if steps > 0 else 0)
            self.training_history['steps'].append(steps)
            
            # Print progress
            if episode % render_every == 0:
                avg_reward = np.mean(self.training_history['total_reward'][-render_every:])
                avg_loss = np.mean(self.training_history['avg_loss'][-render_every:])
                print(f"Episode: {episode:4d}/{episodes} | "
                      f"Reward: {total_reward:7.2f} | "
                      f"Avg Reward: {avg_reward:7.2f} | "
                      f"Loss: {total_loss/steps if steps>0 else 0:7.4f} | "
                      f"Epsilon: {self.epsilon:.3f} | "
                      f"Steps: {steps:4d}")
            
            # Save best model
            if total_reward > best_reward:
                best_reward = total_reward
                self.save_model(f"best_model_{total_reward:.0f}.pth")
            
            # Periodic save
            if episode % save_every == 0:
                self.save_model(f"checkpoint_ep{episode}.pth")
                self.save_training_history()
        
        # Final save
        self.save_model("final_model.pth")
        self.save_training_history()
        
        training_time = time.time() - start_time
        print(f"\n✅ Training Complete! Time: {training_time/60:.2f} minutes")
        print(f"🏆 Best Reward: {best_reward:.2f}")
        print(f"📈 Average Reward: {np.mean(self.training_history['total_reward']):.2f}")
        
        return self.training_history
    
    def save_model(self, filename="train_model.pth"):
        """Save model checkpoint"""
        checkpoint = {
            'policy_state_dict': self.policy_net.state_dict(),
            'target_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_history': self.training_history,
            'state_size': self.state_size,
            'action_size': self.action_size
        }
        torch.save(checkpoint, filename)
        print(f"💾 Model saved as {filename}")
    
    def load_model(self, filename="train_model.pth"):
        """Load model checkpoint"""
        if not os.path.exists(filename):
            print(f"⚠️ Model file {filename} not found!")
            return
        
        checkpoint = torch.load(filename, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint['policy_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.training_history = checkpoint['training_history']
        self.state_size = checkpoint['state_size']
        self.action_size = checkpoint['action_size']
        print(f"📂 Model loaded from {filename}")
    
    def save_training_history(self):
        """Save training history to CSV"""
        df = pd.DataFrame(self.training_history)
        df.to_csv('training_history.csv', index=False)
        print("📊 Training history saved to training_history.csv")
    
    def predict(self, state):
        """Predict action for given state (without exploration)"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.policy_net(state)
        action = torch.argmax(q_values).item()
        q_value = q_values[0][action].item()
        return action, q_value
    
    def get_q_values(self, state):
        """Get Q-values for all actions"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.policy_net(state).cpu().numpy().flatten()
        return q_values

# ========== TRAINING LOOP ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🚆 ENHANCED INDIAN RAILWAYS AI TRAINING SYSTEM")
    print("=" * 60)
    
    try:
        # Import environment
        from rail_env import EnhancedRailwayEnv
        
        # Initialize environment
        print("\n📦 Initializing Railway Environment...")
        env = EnhancedRailwayEnv()
        state_size = env.observation_space.shape[0]
        action_size = env.action_space.n
        
        print(f"📊 State Size: {state_size}, Action Size: {action_size}")
        
        # Initialize agent
        print("🤖 Initializing Enhanced DQN Agent...")
        agent = EnhancedTrainAgent(state_size, action_size)
        
        # Train agent
        print("\n🎯 Starting Training...")
        episodes = 1000
        training_history = agent.train(env, episodes=episodes, save_every=100, render_every=50)
        
        # Test the trained agent
        print("\n🧪 Testing Trained Agent...")
        test_episodes = 10
        test_rewards = []
        
        for test_ep in range(test_episodes):
            state = env.reset()
            state = np.reshape(state, [1, state_size])
            total_reward = 0
            done = False
            
            while not done:
                action, _ = agent.predict(state)
                next_state, reward, done, _ = env.step(action)
                next_state = np.reshape(next_state, [1, state_size])
                total_reward += reward
                state = next_state
            
            test_rewards.append(total_reward)
            print(f"Test Episode {test_ep+1}: Reward = {total_reward:.2f}")
        
        print(f"\n📊 Test Results:")
        print(f"  Average Reward: {np.mean(test_rewards):.2f}")
        print(f"  Max Reward: {np.max(test_rewards):.2f}")
        print(f"  Min Reward: {np.min(test_rewards):.2f}")
        print(f"  Std Dev: {np.std(test_rewards):.2f}")
        
        # Save final model
        agent.save_model("indian_railways_ai_model.pth")
        
        print("\n🎉 Training Complete! Model ready for deployment.")
        
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()

# ========== HELPER FUNCTIONS ==========
def create_training_report():
    """Generate training report"""
    if os.path.exists('training_history.csv'):
        df = pd.read_csv('training_history.csv')
        
        print("\n📈 TRAINING REPORT")
        print("=" * 40)
        print(f"Total Episodes: {len(df)}")
        print(f"Average Reward: {df['total_reward'].mean():.2f}")
        print(f"Best Reward: {df['total_reward'].max():.2f}")
        print(f"Average Loss: {df['avg_loss'].mean():.4f}")
        print(f"Final Epsilon: {df['epsilon'].iloc[-1]:.4f}")
        print(f"Average Steps: {df['steps'].mean():.0f}")
        
        # Create plot (optional)
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            
            # Reward plot
            axes[0, 0].plot(df['episode'], df['total_reward'])
            axes[0, 0].set_title('Reward per Episode')
            axes[0, 0].set_xlabel('Episode')
            axes[0, 0].set_ylabel('Reward')
            
            # Loss plot
            axes[0, 1].plot(df['episode'], df['avg_loss'])
            axes[0, 1].set_title('Average Loss per Episode')
            axes[0, 1].set_xlabel('Episode')
            axes[0, 1].set_ylabel('Loss')
            
            # Epsilon decay
            axes[1, 0].plot(df['episode'], df['epsilon'])
            axes[1, 0].set_title('Epsilon Decay')
            axes[1, 0].set_xlabel('Episode')
            axes[1, 0].set_ylabel('Epsilon')
            
            # Q-values
            axes[1, 1].plot(df['episode'], df['avg_q_value'])
            axes[1, 1].set_title('Average Q-Value')
            axes[1, 1].set_xlabel('Episode')
            axes[1, 1].set_ylabel('Q-Value')
            
            plt.tight_layout()
            plt.savefig('training_report.png')
            print("📊 Training report plot saved as 'training_report.png'")
            
        except:
            pass

# Run if this file is executed directly
if __name__ == "__main__":
    create_training_report()
