# train.py
import os
import torch
import torch.nn as nn
from multiprocessing import freeze_support
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split

def main():
    # 1. Data setup
    data_dir = "augmented_dataset"
    transform = transforms.Compose([ transforms.ToTensor() ])
    full_dataset = datasets.ImageFolder(root=data_dir, transform=transform)
    train_len = int(0.8 * len(full_dataset))
    val_len   = len(full_dataset) - train_len
    train_ds, val_ds = random_split(full_dataset, [train_len, val_len])

    # <-- Note num_workers=4 will now work safely -->
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True,  num_workers=4)
    val_loader   = DataLoader(val_ds,   batch_size=32, shuffle=False, num_workers=4)

    # 2. Model setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    # use new weights API instead of deprecated pretrained=True
    weights = models.ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    for param in model.parameters():
        param.requires_grad = False
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 7)
    model = model.to(device)

    # 3. Loss & optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.fc.parameters(), lr=1e-3, momentum=0.9)

    # 4. Training loop
    num_epochs = 10
    for epoch in range(num_epochs):
        # — train —
        model.train()
        running_loss = running_corrects = 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss    += loss.item() * inputs.size(0)
            running_corrects+= (outputs.argmax(1) == labels).sum().item()
        train_loss = running_loss / train_len
        train_acc  = running_corrects / train_len
        print(f"[Epoch {epoch+1}] train  loss: {train_loss:.4f}, acc: {train_acc:.4f}")

        # — validate —
        model.eval()
        val_loss = val_corrects = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss     += loss.item() * inputs.size(0)
                val_corrects += (outputs.argmax(1) == labels).sum().item()
        val_loss /= val_len
        val_acc  = val_corrects / val_len
        print(f"          valid loss: {val_loss:.4f}, acc: {val_acc:.4f}\n")

    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'num_epochs': num_epochs,
    }, "gem_classifier.pth")
    print("Training complete! Model saved to gem_classifier.pth")

if __name__ == "__main__":
    freeze_support()
    main()
