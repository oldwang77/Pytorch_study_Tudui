import torchvision
import torch
from p27.model import *

# 准备数据集
from torch.utils.data import DataLoader

train_data = torchvision.datasets.CIFAR10(root="../dataset", train=True, transform=torchvision.transforms.ToTensor(),
                                          download=True)

test_data = torchvision.datasets.CIFAR10(root="../dataset", train=False, transform=torchvision.transforms.ToTensor(),
                                         download=True)

train_data_size = len(train_data)
test_data_size = len(test_data)
print(f"训练集的长度是{train_data_size}")
print(f"测试集的长度是{test_data_size}")

# 利用DataLoader来加载数据集
train_dataloader = DataLoader(train_data, batch_size=64)
test_dataloader = DataLoader(test_data, batch_size=64)

# 创建网络模型
tudui = Tudui()

# 损失函数,分类问题，可以用交叉熵
loss_fn = nn.CrossEntropyLoss()

# 优化器
learning_rate = 0.01
optimizer = torch.optim.SGD(tudui.parameters(), lr=learning_rate)

# 设置训练网络的一些参数
# 记录训练的次数
total_train_step = 0
# 记录测试的次数
total_test_step = 0
# 训练的轮数
epoch = 10

writer = SummaryWriter("../logs_train")

for i in range(epoch):
    print(f"---第{i}轮训练开始---")

    # 训练开始，通常情况下都要写这个train
    tudui.train()

    for data in train_dataloader:
        imgs, target = data
        output = tudui(imgs)
        loss = loss_fn(output, target)
        # 优化器优化模型
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_train_step = total_train_step + 1
        if total_train_step % 100 == 0:
            print(f"训练次数:{total_train_step},loss:{loss.item()}")
            writer.add_scalar("train_loss", loss.item(), total_train_step)

    # 测试步骤
    tudui.eval()
    # 保证不再对模型调优
    total_test_loss = 0
    total_accuracy = 0

    with torch.no_grad():
        for data in test_dataloader:
            imgs, target = data
            outputs = tudui(imgs)
            loss = loss_fn(outputs, target)
            total_test_loss = total_test_loss + loss.item()
            # 方向是横向的是1
            accuracy = (outputs.argmax(1) == target).sum()
            total_accuracy = total_accuracy + accuracy

    print(f"整体测试集上的loss:{total_test_loss}")
    print(f"整体上测试集的正确率:{total_accuracy/test_data_size}")
    writer.add_scalar("test_loss", total_test_loss, total_test_step)
    writer.add_scalar("test_accuracy", total_accuracy/test_data_size, total_test_step)
    total_test_step = total_test_step + 1

    torch.save(tudui, "tudui.{}.pth".format(i))
    print("模型已经保存")

writer.close()
