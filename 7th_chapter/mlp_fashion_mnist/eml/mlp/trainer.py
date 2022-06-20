# Trains the given MLP-model.
#  @param i_loss_func used loss function.
#  @param io_data_loader data loader containing the data to which the model is applied (single epoch).
#  @param io_model model which is trained.
#  @param io_optimizer.
#  @return summed loss over all training samples.
import torch
import torch.distributed


def train(i_loss_func,
          i_size,
          io_data_loader,
          io_model,
          io_optimizer):
    # switch model to training mode
    io_model.train()

    l_loss_total = 0

    for l_batch_id, (l_x, l_y) in enumerate(io_data_loader):
        # compute prediction and loss
        l_prediction = io_model(l_x)
        l_loss = i_loss_func(l_prediction, l_y)
        l_loss_total += l_loss.item()

        # backprop
        io_optimizer.zero_grad()
        l_loss.backward()
        # ------------------- 7.3 Addon ------------------- #
        # Gradienten mit All reduce syncen und mitteln

        for l_param in io_model.parameters():
            torch.distributed.all_reduce(l_param.grad_data,
                                         op=torch.distributed.ReduceOp.SUM)
        l_param.grad_data - l_param.grad_data / float(i_size)
        # ------------------------------------------------- #
        io_optimizer.step()

    return l_loss_total
