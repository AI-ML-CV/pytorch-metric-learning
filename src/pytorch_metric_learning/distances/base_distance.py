import torch
from ..utils import common_functions as c_f
from ..utils.module_with_records import ModuleWithRecords


class BaseDistance(ModuleWithRecords):
    def __init__(self, normalize_embeddings=True, p=2, is_inverted=False, **kwargs):
        super().__init__(**kwargs)
        self.normalize_embeddings = normalize_embeddings
        self.p = p
        self.is_inverted = is_inverted
        self.add_to_recordable_attributes(list_of_names=["p"], is_stat=False)
        self.add_to_recordable_attributes(list_of_names=["avg_query_norm", "avg_ref_norm"], is_stat=True)

    def forward(self, query_emb, ref_emb=None):
        self.reset_stats()
        if ref_emb is None:
            ref_emb = query_emb
        query_emb = self.maybe_normalize(query_emb)
        ref_emb = self.maybe_normalize(ref_emb)
        self.set_stats(query_emb, ref_emb)
        mat = self.compute_mat(query_emb, ref_emb)
        assert mat.size() == torch.Size((query_emb.size(0), ref_emb.size(0)))
        return mat

    def compute_mat(self, query_emb, ref_emb):
        raise NotImplementedError

    def smallest_dist(self, *args, **kwargs):
        if self.is_inverted:
            return torch.max(*args, **kwargs)
        return torch.min(*args, **kwargs)

    def largest_dist(self, *args, **kwargs):
        if self.is_inverted:
            return torch.min(*args, **kwargs)
        return torch.max(*args, **kwargs)    

    def x_less_than_y(self, x, y, or_equal=False):
        condition = (x > y) if self.is_inverted else (x < y)
        if or_equal:
            condition |= x == y
        return condition

    def x_greater_than_y(self, x, y, or_equal=False):
        return ~self.x_less_than_y(x, y, not or_equal)

    # This measures the margin between x and y
    def margin(self, x, y):
        if self.is_inverted:
            return y - x
        return x - y

    def maybe_normalize(self, embeddings):
        if self.normalize_embeddings:
            return torch.nn.functional.normalize(embeddings, p=self.p, dim=1)
        return embeddings

    def get_norm(self, embeddings):
        return torch.norm(embeddings, p=self.p, dim=1)

    def set_stats(self, query_emb, ref_emb):
        if self.collect_stats:
            with torch.no_grad():
                self.avg_query_norm = torch.mean(torch.norm(query_emb, p=self.p, dim=1))
                self.avg_ref_norm = torch.mean(torch.norm(ref_emb, p=self.p, dim=1))

    