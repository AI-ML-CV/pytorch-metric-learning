import unittest
import torch
import numpy as np
from pytorch_metric_learning.losses import ArcFaceLoss
from pytorch_metric_learning.utils import common_functions as c_f

class TestArcFaceLoss(unittest.TestCase):
    def test_arcface_loss(self):
        margin = 30
        scale = 64
        loss_func = ArcFaceLoss(margin=margin, scale=scale, num_classes=10, embedding_size=2)

        embedding_angles = [0, 20, 40, 60, 80]
        embeddings = torch.FloatTensor([c_f.angle_to_coord(a) for a in embedding_angles]) #2D embeddings
        labels = torch.LongTensor([0, 0, 1, 1, 2])

        loss = loss_func(embeddings, labels)

        weights = torch.nn.functional.normalize(loss_func.W, p=2, dim=0)
        logits = torch.matmul(embeddings, weights)
        for i, c in enumerate(labels):
            logits[i, c] = torch.cos(torch.acos(logits[i, c]) + torch.tensor(np.radians(margin)))
        
        correct_loss = torch.nn.functional.cross_entropy(logits*scale, labels)
        self.assertTrue(torch.isclose(loss, correct_loss))