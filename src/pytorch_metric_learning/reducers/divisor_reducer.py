from .base_reducer import BaseReducer
import torch

class DivisorReducer(BaseReducer):
    def unpack_loss_info(self, loss_info):
        losses, loss_indices, reduction_type, divisor_components = loss_info
        self.total_divisor = 0
        for name, value in divisor_components.items():
            self.total_divisor += value
            self.add_to_recordable_attributes(name=name, is_stat=True, optional=True)
            self.set_recordable_attribute(name, value)
        return losses, loss_indices, reduction_type

    def sum_and_divide(self, losses):
        if self.total_divisor != 0:
            return torch.sum(losses) / self.total_divisor
        return torch.sum(losses*0)

    def element_reduction(self, losses, *_):
        return self.sum_and_divide(losses)
    
    def pos_pair_reduction(self, losses, *args):
        return self.sum_and_divide(losses) 

    def neg_pair_reduction(self, losses, *args):
        return self.sum_and_divide(losses) 

    def triplet_reduction(self, losses, *args):
        return self.sum_and_divide(losses)