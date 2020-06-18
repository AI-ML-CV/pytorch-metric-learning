import unittest
import torch
from pytorch_metric_learning.reducers import DoNothingReducer

class TestDoNothingReducer(unittest.TestCase):
    def test_do_nothing_reducer(self):
        reducer = DoNothingReducer()
        loss_dict = {"loss": {"losses": torch.randn(100), "indices": torch.arange(100), "reduction_type": "element"}}
        output = reducer(loss_dict, None, None)
        self.assertTrue(output == loss_dict)