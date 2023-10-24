
import pandas as pd


class Entropy:

    def load(cls, *args, **kwargs):
        cls.res = kwargs.pop('res')
        for var, val in kwargs.items():
            yield pd.DataFrame({var: val})

    def combine(self, dfs):
        join = dfs[0]
        for d in dfs[1:]:
            join = join.merge(d, how='cross')
        return join

    def transform(self, combined):
        d = {c: [] for c in combined.columns}
        for vals in combined.values:
            d[self.res] = d.get(self.res, []) + [sum(vals.tolist())]
            for idx, val in enumerate(vals.tolist()):
                d[combined.columns[idx]] = d.get(combined.columns[idx], []) + [val]
        self.data = pd.DataFrame.from_dict(d)
        return self.data


if __name__ == '__main__':
    e = Entropy()
    dfs = e.load(res='x', y=[0, 1], z=[1, 1, 2, 3])
    print(e.transform(e.combine(list(dfs))))
