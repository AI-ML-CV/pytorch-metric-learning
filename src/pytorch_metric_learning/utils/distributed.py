import torch

# modified from https://github.com/allenai/allennlp
def is_distributed():
    return torch.distributed.is_available() and torch.distributed.is_initialized()

# modified from https://github.com/JohnGiorgi/DeCLUTR
def all_gather_embeddings_labels(embeddings, labels):
    # If we are not using distributed training, this is a no-op.
    if not is_distributed():
        return embeddings, labels
    # Gather the encoded anchors and positives on all replicas
    embeddings_list = [torch.ones_like(embeddings) for _ in range(torch.distributed.get_world_size())]
    labels_list = [torch.ones_like(labels) for _ in range(torch.distributed.get_world_size())]
    torch.distributed.all_gather(embeddings_list, embeddings.contiguous())
    torch.distributed.all_gather(labels_list, labels.contiguous())
    # The gathered copy of the current replicas positive pairs have no gradients, so we overwrite
    # them with the positive pairs generated on this replica, which DO have gradients.
    embeddings_list[torch.distributed.get_rank()] = embeddings
    labels_list[torch.distributed.get_rank()] = labels
    # Finally, we concatenate the positive pairs so they can be fed to the contrastive loss.
    embeddings = torch.cat(embeddings_list)
    labels = torch.cat(labels_list)
    return embeddings, labels


class DistributedLossWrapper(torch.nn.Module):
    def __init__(self, loss):
        super().__init__()
        self.loss = loss

    def forward(self, embeddings, labels, indices_tuple=None):
        embeddings, labels = all_gather_embeddings_labels(embeddings, labels)
        return self.loss(embeddings, labels, indices_tuple)



class DistributedMinerWrapper(torch.nn.Module):
    def __init__(self, miner):
        super().__init__()
        self.miner = miner

    def forward(self, embeddings, labels, ref_emb=None, ref_labels=None):
        embeddings, labels = all_gather_embeddings_labels(embeddings, labels)
        if ref_emb is not None:
            ref_emb, ref_labels = all_gather_embeddings_labels(ref_emb, ref_labels)
        return self.miner(embeddings, labels, ref_emb, ref_labels)