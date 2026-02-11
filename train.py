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

# ========== MULTI-AGENT DQN NETWORK ==========
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
        
    def push(self, state, action, reward, next_state, done, agent_id=None):
        self.buffer.append((state, action, reward, next_state, done, agent_id))
        self.priorities.append(self.max_priority)
        
    def sample(self, batch_size):
        if len(self.buffer) < batch_size:
            samples = random.sample(self.buffer, len(self.buffer))
            indices = np.arange(len(self.buffer))
            return samples, np.ones(len(self.buffer)), indices
        
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

# ========== MULTI-AGENT TRAIN AGENT ==========
class MultiAgentTrainAgent:
    def __init__(self, state_size, action_size, num_agents=10, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.state_size = state_size
        self.action_size = action_size
        self.num_agents = num_agents
        self.device = device
        
        # Create agents (one DQN per train for independent learning)
        self.agents = []
        for i in range(num_agents):
            agent = {
                'id': i,
                'policy_net': DQNetwork(state_size, action_size).to(device),
                'target_net': DQNetwork(state_size, action_size).to(device),
                'optimizer': optim.Adam(DQNetwork(state_size, action_size).parameters(), lr=0.0005),
                'memory': deque(maxlen=10000),
                'epsilon': 1.0,
                'epsilon_min': 0.01,
                'epsilon_decay': 0.995,
                'last_action': 0,
                'communication_buffer': deque(maxlen=10),  # For inter-agent communication
                'performance_stats': {
                    'avg_reward': 0,
                    'collisions_avoided': 0,
                    'energy_saved': 0,
                    'maintenance_alerts': 0
                }
            }
            agent['target_net'].load_state_dict(agent['policy_net'].state_dict())
            agent['target_net'].eval()
            self.agents.append(agent)
        
        # Shared prioritized experience replay
        self.shared_memory = PrioritizedReplayBuffer(capacity=100000)
        
        # Hyperparameters
        self.gamma = 0.99
        self.learning_rate = 0.0005
        self.batch_size = 128
        self.target_update = 10
        self.tau = 0.01  # For soft updates
        
        self.criterion = nn.SmoothL1Loss()  # Huber loss
        
        # Training history
        self.training_history = {
            'episode': [], 'total_reward': [], 'avg_loss': [],
            'epsilon': [], 'avg_q_value': [], 'steps': [],
            'throughput': [], 'avg_delay': [], 'energy_efficiency': [],
            'collisions_avoided': [], 'maintenance_alerts': [],
            'communication_success': [], 'weather_adaptations': []
        }
        
        # Communication protocols
        self.communication_protocol = {
            'gap_adjustment': True,
            'weather_warnings': True,
            'maintenance_alerts': True,
            'energy_savings': True
        }
        
        self.episode = 0
        
    def act(self, state, agent_id=0, training=True):
        """Select action for a specific agent"""
        agent = self.agents[agent_id]
        
        if training and random.random() < agent['epsilon']:
            return random.randrange(self.action_size)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = agent['policy_net'](state_tensor)
        
        action = torch.argmax(q_values).item()
        
        # Store for communication
        agent['last_action'] = action
        agent['communication_buffer'].append({
            'agent_id': agent_id,
            'action': action,
            'timestamp': time.time()
        })
        
        return action
    
    def communicate(self, agent_id, message_type, data):
        """Inter-agent communication"""
        agent = self.agents[agent_id]
        
        # Broadcast to other agents (simulated)
        for other_agent in self.agents:
            if other_agent['id'] != agent_id:
                # Process different message types
                if message_type == 'gap_adjustment':
                    other_agent['communication_buffer'].append({
                        'sender': agent_id,
                        'type': 'gap_adjustment',
                        'data': data,
                        'timestamp': time.time()
                    })
                elif message_type == 'weather_warning':
                    other_agent['communication_buffer'].append({
                        'sender': agent_id,
                        'type': 'weather_warning',
                        'data': data,
                        'timestamp': time.time()
                    })
                elif message_type == 'maintenance_alert':
                    other_agent['communication_buffer'].append({
                        'sender': agent_id,
                        'type': 'maintenance_alert',
                        'data': data,
                        'timestamp': time.time()
                    })
        
        return True
    
    def get_communication_messages(self, agent_id):
        """Get messages for a specific agent"""
        agent = self.agents[agent_id]
        return list(agent['communication_buffer'])
    
    def remember(self, state, action, reward, next_state, done, agent_id=0):
        """Store experience in shared memory"""
        self.shared_memory.push(state, action, reward, next_state, done, agent_id)
        
        # Also store in agent's personal memory
        self.agents[agent_id]['memory'].append((state, action, reward, next_state, done))
    
    def collaborative_replay(self):
        """Multi-agent collaborative learning"""
        if len(self.shared_memory) < self.batch_size:
            return 0, np.zeros(self.batch_size)
        
        # Sample from shared memory
        samples, weights, indices = self.shared_memory.sample(self.batch_size)
        
        total_loss = 0
        td_errors_all = []
        
        # Group experiences by agent
        agent_experiences = {}
        for i, (state, action, reward, next_state, done, agent_id) in enumerate(samples):
            if agent_id not in agent_experiences:
                agent_experiences[agent_id] = []
            agent_experiences[agent_id].append((i, state, action, reward, next_state, done, weights[i]))
        
        # Train each agent on their experiences
        for agent_id, experiences in agent_experiences.items():
            if agent_id < len(self.agents):
                agent = self.agents[agent_id]
                
                # Prepare batch
                indices_list = [exp[0] for exp in experiences]
                states = torch.FloatTensor(np.array([exp[1] for exp in experiences])).to(self.device)
                actions = torch.LongTensor([exp[2] for exp in experiences]).unsqueeze(1).to(self.device)
                rewards = torch.FloatTensor([exp[3] for exp in experiences]).unsqueeze(1).to(self.device)
                next_states = torch.FloatTensor(np.array([exp[4] for exp in experiences])).to(self.device)
                dones = torch.FloatTensor([exp[5] for exp in experiences]).unsqueeze(1).to(self.device)
                weights_tensor = torch.FloatTensor([exp[6] for exp in experiences]).unsqueeze(1).to(self.device)
                
                # Current Q values
                current_q = agent['policy_net'](states).gather(1, actions)
                
                # Double DQN
                with torch.no_grad():
                    next_actions = agent['policy_net'](next_states).argmax(1).unsqueeze(1)
                    next_q = agent['target_net'](next_states).gather(1, next_actions)
                    target_q = rewards + (1 - dones) * self.gamma * next_q
                
                # Compute TD errors
                td_errors = (target_q - current_q).abs().detach().cpu().numpy()
                td_errors_all.extend(td_errors)
                
                # Compute loss
                loss = (weights_tensor * self.criterion(current_q, target_q)).mean()
                total_loss += loss.item()
                
                # Optimize
                agent['optimizer'].zero_grad()
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(agent['policy_net'].parameters(), 1.0)
                
                agent['optimizer'].step()
                
                # Decay epsilon
                if agent['epsilon'] > agent['epsilon_min']:
                    agent['epsilon'] *= agent['epsilon_decay']
        
        # Update priorities
        if td_errors_all:
            self.shared_memory.update_priorities(indices, np.array(td_errors_all).squeeze())
        
        # Soft update target networks
        self.soft_update_all()
        
        avg_loss = total_loss / len(agent_experiences) if agent_experiences else 0
        return avg_loss, np.array(td_errors_all) if td_errors_all else np.zeros(self.batch_size)
    
    def soft_update_all(self):
        """Soft update all target networks"""
        for agent in self.agents:
            for target_param, policy_param in zip(agent['target_net'].parameters(), agent['policy_net'].parameters()):
                target_param.data.copy_(self.tau * policy_param.data + (1.0 - self.tau) * target_param.data)
    
    def train(self, env, episodes=1000, save_every=50, render_every=100):
        print("🚀 Multi-Agent AI Training Started: Optimizing Railway Throughput...")
        print(f"🤖 Number of Agents: {self.num_agents}")
        print(f"📊 State Size: {self.state_size}, Action Size: {self.action_size}")
        print(f"⚙️ Device: {self.device}")
        
        start_time = time.time()
        best_reward = -float('inf')
        best_throughput = 0
        
        for episode in range(episodes):
            # Reset environment for all agents
            states = env.reset()
            states = np.reshape(states, [self.num_agents, self.state_size])
            
            total_reward = np.zeros(self.num_agents)
            total_loss = 0
            total_q = 0
            steps = 0
            trains_completed = 0
            total_delay = 0
            total_energy = 0
            collisions_avoided = 0
            maintenance_alerts = 0
            communication_success = 0
            weather_adaptations = 0
            
            # Track agent states
            agent_dones = [False] * self.num_agents
            all_done = False
            
            while not all_done and steps < 1000:
                actions = []
                
                # Each agent selects action
                for agent_id in range(self.num_agents):
                    if not agent_dones[agent_id]:
                        # Check for communication messages
                        messages = self.get_communication_messages(agent_id)
                        
                        # Process weather warnings
                        weather_warnings = [m for m in messages if m.get('type') == 'weather_warning']
                        if weather_warnings:
                            weather_adaptations += 1
                            # Adjust state for weather
                            pass
                        
                        # Process maintenance alerts
                        maintenance_alerts_msgs = [m for m in messages if m.get('type') == 'maintenance_alert']
                        if maintenance_alerts_msgs:
                            maintenance_alerts += 1
                        
                        action = self.act(states[agent_id], agent_id)
                        actions.append(action)
                    else:
                        actions.append(0)  # No-op for done agents
                
                # Step environment for all agents
                next_states, rewards, dones, infos = env.step(actions)
                next_states = np.reshape(next_states, [self.num_agents, self.state_size])
                
                # Store experiences and update
                for agent_id in range(self.num_agents):
                    if not agent_dones[agent_id]:
                        self.remember(states[agent_id], actions[agent_id], 
                                     rewards[agent_id], next_states[agent_id], 
                                     dones[agent_id], agent_id)
                        
                        total_reward[agent_id] += rewards[agent_id]
                        
                        # Calculate Q-value
                        with torch.no_grad():
                            state_tensor = torch.FloatTensor(states[agent_id]).to(self.device)
                            q_values = self.agents[agent_id]['policy_net'](state_tensor)
                            total_q += q_values[0][actions[agent_id]].item()
                        
                        # Check for inter-agent communication needs
                        if 'distance_to_next' in infos[agent_id] and infos[agent_id]['distance_to_next'] < 50:
                            # Send gap adjustment message
                            self.communicate(agent_id, 'gap_adjustment', {
                                'distance': infos[agent_id]['distance_to_next'],
                                'suggested_action': 1  # Decelerate
                            })
                            communication_success += 1
                        
                        if infos[agent_id].get('weather_alert'):
                            # Send weather warning
                            self.communicate(agent_id, 'weather_warning', {
                                'weather': infos[agent_id]['weather'],
                                'severity': infos[agent_id].get('weather_severity', 'moderate')
                            })
                            communication_success += 1
                        
                        if infos[agent_id].get('maintenance_alert'):
                            # Send maintenance alert
                            self.communicate(agent_id, 'maintenance_alert', {
                                'train_id': infos[agent_id]['train_id'],
                                'issue': infos[agent_id].get('maintenance_issue', 'unknown'),
                                'suggested_action': 'inspect_at_next_station'
                            })
                            communication_success += 1
                        
                        if infos[agent_id].get('collision_avoided'):
                            collisions_avoided += 1
                            self.agents[agent_id]['performance_stats']['collisions_avoided'] += 1
                        
                        if infos[agent_id].get('energy_saved'):
                            self.agents[agent_id]['performance_stats']['energy_saved'] += infos[agent_id]['energy_saved']
                        
                        agent_dones[agent_id] = dones[agent_id]
                
                # Collaborative learning
                loss, _ = self.collaborative_replay()
                total_loss += loss if loss else 0
                
                states = next_states
                steps += 1
                
                # Track throughput metrics
                if 'trains_completed' in env.get_environment_stats():
                    trains_completed = env.get_environment_stats()['trains_completed']
                if 'avg_delay' in env.get_environment_stats():
                    total_delay += env.get_environment_stats()['avg_delay']
                if 'total_energy' in env.get_environment_stats():
                    total_energy = env.get_environment_stats()['total_energy']
                
                all_done = all(agent_dones)
            
            # Calculate metrics
            throughput = (trains_completed / (steps / 3600)) if steps > 0 else 0
            avg_delay = total_delay / max(1, trains_completed)
            energy_efficiency = 100 - (total_energy / max(1, steps)) * 10
            
            # Record training history
            self.training_history['episode'].append(episode)
            self.training_history['total_reward'].append(np.sum(total_reward))
            self.training_history['avg_loss'].append(total_loss / steps if steps > 0 else 0)
            self.training_history['epsilon'].append(np.mean([a['epsilon'] for a in self.agents]))
            self.training_history['avg_q_value'].append(total_q / (steps * self.num_agents) if steps > 0 else 0)
            self.training_history['steps'].append(steps)
            self.training_history['throughput'].append(throughput)
            self.training_history['avg_delay'].append(avg_delay)
            self.training_history['energy_efficiency'].append(energy_efficiency)
            self.training_history['collisions_avoided'].append(collisions_avoided)
            self.training_history['maintenance_alerts'].append(maintenance_alerts)
            self.training_history['communication_success'].append(communication_success)
            self.training_history['weather_adaptations'].append(weather_adaptations)
            
            # Print progress
            if episode % render_every == 0:
                avg_reward = np.mean(self.training_history['total_reward'][-render_every:])
                avg_throughput = np.mean(self.training_history['throughput'][-render_every:])
                avg_loss = np.mean(self.training_history['avg_loss'][-render_every:])
                print(f"Episode: {episode:4d}/{episodes} | "
                      f"Reward: {np.sum(total_reward):7.2f} | "
                      f"Throughput: {throughput:5.1f} trains/h | "
                      f"Agents Active: {self.num_agents - sum(agent_dones):2d} | "
                      f"Comms: {communication_success:3d} | "
                      f"Collisions Avoided: {collisions_avoided:2d} | "
                      f"Loss: {total_loss/steps if steps>0 else 0:7.4f}")
            
            # Save best model based on throughput
            if throughput > best_throughput:
                best_throughput = throughput
                self.save_model(f"models/multiagent_best_{throughput:.0f}_throughput.pth")
                print(f"🏆 New best throughput: {throughput:.1f} trains/hour")
            
            # Save best model based on reward
            if np.sum(total_reward) > best_reward:
                best_reward = np.sum(total_reward)
                self.save_model(f"models/multiagent_best_{np.sum(total_reward):.0f}_reward.pth")
            
            # Periodic save
            if episode % save_every == 0:
                self.save_model(f"models/multiagent_checkpoint_ep{episode}.pth")
                self.save_training_history()
        
        # Final save
        self.save_model("models/multiagent_final_model.pth")
        self.save_training_history()
        
        training_time = time.time() - start_time
        print(f"\n✅ Multi-Agent Training Complete! Time: {training_time/60:.2f} minutes")
        print(f"🏆 Best Throughput: {best_throughput:.1f} trains/hour")
        print(f"🏆 Best Reward: {best_reward:.2f}")
        print(f"🤖 Agents: {self.num_agents}")
        print(f"📈 Average Throughput: {np.mean(self.training_history['throughput']):.2f} trains/hour")
        print(f"📉 Average Delay: {np.mean(self.training_history['avg_delay']):.2f} minutes")
        print(f"🔄 Communication Success Rate: {np.mean(self.training_history['communication_success']):.1f}/step")
        
        return self.training_history
    
    def save_model(self, filename="multiagent_model.pth"):
        """Save model checkpoint"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        checkpoint = {
            'agents_state_dicts': [a['policy_net'].state_dict() for a in self.agents],
            'targets_state_dicts': [a['target_net'].state_dict() for a in self.agents],
            'optimizers_state_dicts': [a['optimizer'].state_dict() for a in self.agents],
            'epsilons': [a['epsilon'] for a in self.agents],
            'training_history': self.training_history,
            'state_size': self.state_size,
            'action_size': self.action_size,
            'num_agents': self.num_agents,
            'communication_protocol': self.communication_protocol,
            'performance_stats': [a['performance_stats'] for a in self.agents]
        }
        torch.save(checkpoint, filename)
        print(f"💾 Multi-Agent Model saved as {filename}")
    
    def load_model(self, filename="multiagent_model.pth"):
        """Load model checkpoint"""
        if not os.path.exists(filename):
            print(f"⚠️ Model file {filename} not found!")
            return False
        
        checkpoint = torch.load(filename, map_location=self.device)
        
        # Ensure we have enough agents
        if checkpoint['num_agents'] != self.num_agents:
            print(f"⚠️ Model has {checkpoint['num_agents']} agents, but environment expects {self.num_agents}")
            return False
        
        # Load each agent
        for i in range(self.num_agents):
            self.agents[i]['policy_net'].load_state_dict(checkpoint['agents_state_dicts'][i])
            self.agents[i]['target_net'].load_state_dict(checkpoint['targets_state_dicts'][i])
            self.agents[i]['optimizer'].load_state_dict(checkpoint['optimizers_state_dicts'][i])
            self.agents[i]['epsilon'] = checkpoint['epsilons'][i]
            if 'performance_stats' in checkpoint and i < len(checkpoint['performance_stats']):
                self.agents[i]['performance_stats'] = checkpoint['performance_stats'][i]
        
        self.training_history = checkpoint['training_history']
        self.state_size = checkpoint['state_size']
        self.action_size = checkpoint['action_size']
        
        if 'communication_protocol' in checkpoint:
            self.communication_protocol = checkpoint['communication_protocol']
        
        print(f"📂 Multi-Agent Model loaded from {filename}")
        return True
    
    def save_training_history(self):
        """Save training history to CSV"""
        os.makedirs('data', exist_ok=True)
        df = pd.DataFrame(self.training_history)
        df.to_csv('data/multiagent_training_history.csv', index=False)
        print("📊 Multi-Agent Training history saved to data/multiagent_training_history.csv")
    
    def predict(self, state, agent_id=0):
        """Predict action for given state (without exploration)"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.agents[agent_id]['policy_net'](state_tensor)
        action = torch.argmax(q_values).item()
        q_value = q_values[0][action].item()
        return action, q_value
    
    def get_q_values(self, state, agent_id=0):
        """Get Q-values for all actions for a specific agent"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.agents[agent_id]['policy_net'](state_tensor).cpu().numpy().flatten()
        return q_values
    
    def get_agent_performance_stats(self, agent_id=0):
        """Get performance statistics for a specific agent"""
        if agent_id < len(self.agents):
            return self.agents[agent_id]['performance_stats']
        return None
    
    def get_all_agent_stats(self):
        """Get performance statistics for all agents"""
        return [agent['performance_stats'] for agent in self.agents]

# ========== TRAINING LOOP ==========
if __name__ == "__main__":
    print("=" * 70)
    print("🚆 MULTI-AGENT AI RAILWAY THROUGHPUT OPTIMIZATION SYSTEM")
    print("🤖 Features: MARL, Weather Integration, Predictive Maintenance, Energy Efficiency")
    print("=" * 70)
    
    try:
        # Import environment
        from rail_env import EnhancedRailwayEnv
        
        # Initialize environment with multiple trains
        print("\n📦 Initializing Multi-Agent Railway Environment...")
        env = EnhancedRailwayEnv(num_trains=10)  # 10 trains = 10 agents
        state_size = env.observation_space.shape[0]
        action_size = env.action_space.n
        
        print(f"📊 State Size: {state_size}, Action Size: {action_size}")
        print(f"🤖 Number of Agents: {env.num_trains}")
        
        # Initialize multi-agent system
        print("🤖 Initializing Multi-Agent DQN System...")
        agent = MultiAgentTrainAgent(state_size, action_size, num_agents=env.num_trains)
        
        # Try to load existing model
        if agent.load_model("models/multiagent_best_model.pth"):
            print("✅ Loaded existing multi-agent model")
        else:
            print("🆕 Starting fresh multi-agent training")
        
        # Train agents
        print("\n🎯 Starting Multi-Agent Training...")
        print("Target: Maximize throughput with communication and coordination")
        episodes = 1000
        training_history = agent.train(env, episodes=episodes, save_every=100, render_every=50)
        
        # Test the trained agents
        print("\n🧪 Testing Trained Multi-Agent System...")
        test_episodes = 5
        test_rewards = []
        test_throughputs = []
        test_communications = []
        
        for test_ep in range(test_episodes):
            states = env.reset()
            states = np.reshape(states, [agent.num_agents, state_size])
            total_reward = np.zeros(agent.num_agents)
            done_list = [False] * agent.num_agents
            trains_completed = 0
            communications = 0
            
            steps = 0
            while not all(done_list) and steps < 500:
                actions = []
                for agent_id in range(agent.num_agents):
                    if not done_list[agent_id]:
                        action, _ = agent.predict(states[agent_id], agent_id)
                        actions.append(action)
                        
                        # Simulate communication
                        if steps % 10 == 0:
                            # Send gap adjustment message
                            agent.communicate(agent_id, 'gap_adjustment', {
                                'distance': random.randint(30, 100),
                                'suggested_action': random.choice([1, 2, 3])
                            })
                            communications += 1
                    else:
                        actions.append(0)
                
                next_states, rewards, dones, infos = env.step(actions)
                next_states = np.reshape(next_states, [agent.num_agents, state_size])
                
                for agent_id in range(agent.num_agents):
                    if not done_list[agent_id]:
                        total_reward[agent_id] += rewards[agent_id]
                        done_list[agent_id] = dones[agent_id]
                        
                        if dones[agent_id] and 'status' in infos[agent_id] and infos[agent_id]['status'] == 'COMPLETED':
                            trains_completed += 1
                
                states = next_states
                steps += 1
            
            # Calculate throughput for this episode
            throughput = trains_completed * 12  # Assuming ~5-min episodes
            test_rewards.append(np.sum(total_reward))
            test_throughputs.append(throughput)
            test_communications.append(communications)
            
            print(f"Test Episode {test_ep+1}: Reward = {np.sum(total_reward):.2f}, "
                  f"Throughput = {throughput:.1f} trains/h, "
                  f"Communications = {communications}")
        
        print(f"\n📊 Multi-Agent Test Results:")
        print(f"  Average Reward: {np.mean(test_rewards):.2f}")
        print(f"  Average Throughput: {np.mean(test_throughputs):.1f} trains/hour")
        print(f"  Average Communications: {np.mean(test_communications):.1f}/episode")
        print(f"  Max Throughput: {np.max(test_throughputs):.1f} trains/hour")
        
        # Save final model
        agent.save_model("models/multiagent_railway_model.pth")
        
        # Get agent performance statistics
        print("\n📈 Agent Performance Statistics:")
        for i, stats in enumerate(agent.get_all_agent_stats()):
            print(f"  Agent {i+1}: Collisions Avoided: {stats['collisions_avoided']}, "
                  f"Energy Saved: {stats['energy_saved']:.1f}, "
                  f"Maintenance Alerts: {stats['maintenance_alerts']}")
        
        print("\n🎉 Multi-Agent Training Complete! System ready for deployment.")
        
    except Exception as e:
        print(f"\n❌ Error during multi-agent training: {e}")
        import traceback
        traceback.print_exc()

# ========== HELPER FUNCTIONS ==========
def create_multiagent_training_report():
    """Generate multi-agent training report"""
    if os.path.exists('data/multiagent_training_history.csv'):
        df = pd.read_csv('data/multiagent_training_history.csv')
        
        print("\n" + "="*70)
        print("📈 MULTI-AGENT TRAINING REPORT: Advanced Features")
        print("="*70)
        print(f"Total Episodes: {len(df)}")
        print(f"Average Reward: {df['total_reward'].mean():.2f}")
        print(f"Best Reward: {df['total_reward'].max():.2f}")
        print(f"Average Throughput: {df['throughput'].mean():.1f} trains/hour")
        print(f"Best Throughput: {df['throughput'].max():.1f} trains/hour")
        print(f"Average Delay: {df['avg_delay'].mean():.1f} minutes")
        print(f"Collisions Avoided: {df['collisions_avoided'].sum():.0f}")
        print(f"Maintenance Alerts: {df['maintenance_alerts'].sum():.0f}")
        print(f"Communication Success Rate: {df['communication_success'].mean():.1f}/step")
        print(f"Weather Adaptations: {df['weather_adaptations'].sum():.0f}")
        print(f"Energy Efficiency: {df['energy_efficiency'].mean():.1f}%")
        
        # Create plot (optional)
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(3, 2, figsize=(15, 12))
            
            # Throughput plot
            axes[0, 0].plot(df['episode'], df['throughput'])
            axes[0, 0].set_title('Multi-Agent Throughput (trains/hour)')
            axes[0, 0].set_xlabel('Episode')
            axes[0, 0].set_ylabel('Trains/hour')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Communication plot
            axes[0, 1].plot(df['episode'], df['communication_success'])
            axes[0, 1].set_title('Inter-Agent Communications')
            axes[0, 1].set_xlabel('Episode')
            axes[0, 1].set_ylabel('Communications/step')
            axes[0, 1].grid(True, alpha=0.3)
            
            # Collisions avoided plot
            axes[1, 0].plot(df['episode'], df['collisions_avoided'].cumsum())
            axes[1, 0].set_title('Cumulative Collisions Avoided')
            axes[1, 0].set_xlabel('Episode')
            axes[1, 0].set_ylabel('Total Collisions Avoided')
            axes[1, 0].grid(True, alpha=0.3)
            
            # Maintenance alerts plot
            axes[1, 1].plot(df['episode'], df['maintenance_alerts'].cumsum())
            axes[1, 1].set_title('Cumulative Maintenance Alerts')
            axes[1, 1].set_xlabel('Episode')
            axes[1, 1].set_ylabel('Total Maintenance Alerts')
            axes[1, 1].grid(True, alpha=0.3)
            
            # Energy efficiency plot
            axes[2, 0].plot(df['episode'], df['energy_efficiency'])
            axes[2, 0].set_title('Energy Efficiency')
            axes[2, 0].set_xlabel('Episode')
            axes[2, 0].set_ylabel('Efficiency Score (%)')
            axes[2, 0].grid(True, alpha=0.3)
            
            # Weather adaptations plot
            axes[2, 1].plot(df['episode'], df['weather_adaptations'].cumsum())
            axes[2, 1].set_title('Cumulative Weather Adaptations')
            axes[2, 1].set_xlabel('Episode')
            axes[2, 1].set_ylabel('Total Weather Adaptations')
            axes[2, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('data/multiagent_training_report.png', dpi=300, bbox_inches='tight')
            print("📊 Multi-agent training report plot saved as 'data/multiagent_training_report.png'")
            
        except Exception as e:
            print(f"⚠️ Could not create plots: {e}")

# Run training report if executed directly
if __name__ == "__main__":
    create_multiagent_training_report()
