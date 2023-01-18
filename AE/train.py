from .model import LSTM_AE_GMM
import numpy as np
import torch
import torch.nn as nn
import sys
import os

batch_size = 128
Max_epochs = 1000 # modeified

def main(white_type, black_type, data_type, mode, device):
    data_dir = os.path.join('../data', 'white_' + white_type + '_black_' + black_type, 'source/data')
    model_dir = os.path.join('../data', 'white_' + white_type + '_black_' + black_type, 'source/model')

    train_data = np.load(os.path.join(data_dir, data_type + '.npy'))[:, :50]
    total_size, input_size = train_data.shape
    max_epochs = Max_epochs * 200 // total_size
    device_id = int(device)
    print(device_id)
    torch.cuda.set_device(device_id)
    if mode == 'continue':
        dagmm = torch.load(os.path.join(model_dir, 'ae_' + data_type + '.pkl'))
        dagmm.to_cuda(device_id)
        dagmm = dagmm.cuda()

    else:
        dagmm = LSTM_AE_GMM(
            input_size=input_size,
            max_len=2000,
            emb_dim=32,
            hidden_size=8,
            dropout=0.2,
            est_hidden_size=64,
            est_output_size=8,
            device=device_id,
        ).cuda()

    dagmm.train_mode()
    optimizer = torch.optim.Adam(dagmm.parameters(), lr=1e-2)
    for epoch in range(max_epochs):
        for batch in range(total_size // batch_size + 1):
            if batch * batch_size >= total_size:
                break
            optimizer.zero_grad()
            input = train_data[batch_size * batch : batch_size * (batch + 1)]
            loss = dagmm.loss(torch.Tensor(input).long().cuda())
            loss.backward()
            optimizer.step()
        print('epoch:', epoch, 'loss:', loss)
        if (epoch + 1) % 50 == 0: # modified
            dagmm.to_cpu()
            dagmm = dagmm.cpu()
            torch.save(dagmm, os.path.join(model_dir, 'ae_' + data_type + '.pkl'))
            dagmm.to_cuda(device_id)
            dagmm = dagmm.cuda()

if __name__ == '__main__':
    
    _, white_type, black_type, data_type, mode, device = sys.argv
    main(white_type, black_type, data_type, mode, device)