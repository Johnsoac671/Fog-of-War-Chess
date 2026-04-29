import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import glob
import re
import os


class DarkChessDataset(Dataset):
    def __init__(self, file_paths):
        self.data = []
            
        corrupted_lines = 0
        for path in file_paths:
            
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    try:
                        self.data.append(json.loads(line))
                    except json.JSONDecodeError:
                        corrupted_lines += 1
                        
        if corrupted_lines > 0:
            print(f"Warning: Skipped {corrupted_lines} corrupted states during loading.")
            

    def __len__(self):
        return len(self.data)


    def __getitem__(self, idx):
        item = self.data[idx]
        board_tensor = torch.tensor(item["state"], dtype=torch.float32)
        policy_tensor = torch.tensor(item["policy"], dtype=torch.float32)
        target_val = torch.tensor([(item["value"] + 1.0) / 2.0], dtype=torch.float32)
        return board_tensor, policy_tensor, target_val


class DarkChessNetwork(nn.Module):
    def __init__(self):
        super(DarkChessNetwork, self).__init__()
        self.conv_block = nn.Sequential(
            nn.Conv2d(14, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        self.policy_conv = nn.Conv2d(128, 2, kernel_size=1)
        self.policy_fc = nn.Linear(2 * 5 * 5, 625)
        
        self.value_conv = nn.Conv2d(128, 1, kernel_size=1)
        self.value_fc1 = nn.Linear(1 * 5 * 5, 64)
        self.value_fc2 = nn.Linear(64, 1)

    def forward(self, x):
        shared = self.conv_block(x)
        p = torch.relu(self.policy_conv(shared)).view(shared.size(0), -1)
        policy = self.policy_fc(p)
        
        v = torch.relu(self.value_conv(shared)).view(shared.size(0), -1)
        v = torch.relu(self.value_fc1(v))
        value = torch.sigmoid(self.value_fc2(v))
        
        return policy, value

def train_network(model, dataset_paths, save_path, epochs=3, batch_size=64, learning_rate=0.001):
    dataset = DarkChessDataset(dataset_paths)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.train()

    for epoch in range(epochs):
        total_loss = 0.0
        
        for boards, target_policies, target_values in dataloader:
            boards, target_policies, target_values = boards.to(device), target_policies.to(device), target_values.to(device)
            optimizer.zero_grad()
            
            pred_policy, pred_value = model(boards)
            loss_value = F.mse_loss(pred_value, target_values)
            loss_policy = -torch.mean(torch.sum(target_policies * F.log_softmax(pred_policy, dim=1), dim=1))
            loss = loss_value + loss_policy
            
            loss.backward()
            
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(dataloader):.4f}")
    
    torch.save(model.state_dict(), save_path)


def get_recent_dataset_files(window_size):
    files = glob.glob(f"{os.path.join(".", "training_data_v")}*{".jsonl"}")
    
    # gross regular expression to rip the version number back out lol
    def extract_version(f):
        match = re.search(r'_v(\d+)\.jsonl', f)
        return int(match.group(1)) if match else -1

    files.sort(key=extract_version)
    return files[-window_size:]


if __name__ == "__main__":
    target_version = 1
    
    net = DarkChessNetwork()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    prev_model_path = f"dark_chess_v{target_version - 1}.pth"
    if os.path.exists(prev_model_path):
        print(f"Loading previous weights from {prev_model_path}")
        net.load_state_dict(torch.load(prev_model_path, map_location=device))
        
    data_files = get_recent_dataset_files(5)
    print(f"Training on datasets: {data_files}")
    
    save_name = f"dark_chess_v{target_version}.pth"
    train_network(net, data_files, save_name, 10)