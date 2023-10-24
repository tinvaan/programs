
import math

import pandas as pd
import sqlalchemy as sql


class Entropy:

    @classmethod
    def p(cls, **kwargs):
        keys = list(kwargs.keys())
        x, y = keys[0], keys[1] if len(keys) > 1 else None
        with cls.engine.connect() as conn:
            d, = conn.execute(sql.text("SELECT COUNT(*) FROM combinations")).fetchone()
            n, = conn.execute(sql.text(
                    "SELECT COUNT(*) FROM combinations " +
                    f"WHERE '{x}'={kwargs.get(x)} and '{y}'={kwargs.get(y)}" if x and y else
                    f"WHERE '{x}'={kwargs.get(x)}"
                )).fetchone()
            return float(n / d)

    @classmethod
    def load(cls, *args, **kwargs):
        cls.res = kwargs.pop('res')
        cls.engine = sql.create_engine('sqlite://', echo=False)
        for var, val in kwargs.items():
            yield pd.DataFrame({var: val})

    def cache(self, data):
        self.dframe = data
        self.dframe.to_sql('combinations', self.engine, if_exists='replace')
        return self.dframe

    def calculate(self, src, dst=None, at=None):
        """
        Entropy is defined as;
            H(X) = -Σi p(X=xi) lg p(X=xi)

        Likewise, conditional entropy of X given Y=yj is;
            H(X | Y=yj) = -Σi p(X=xi | Y=yj) lg p(X=xi | Y=yj)

        More generally, conditional entropy of X given Y is;
            H(X | Y) = -Σj p(Y=yj) Σi p(X=xi | Y=yj) lg p(X=xi | Y=yj)
        """
        p = 0
        if dst is None:
            for i in range(min(self.dframe[src]), max(self.dframe[src])):
                p += self.p(src=i) * math.log2(self.p(src=i))

        if dst and at:
            for i in range(min(self.dframe[src]), max(self.dframe[src])):
                p += self.p(**{src: i, dst: at}) * math.log2(self.p(**{src: i, dst: at}))

        if dst and at is None:
            for j in range(min(self.dframe[dst]), max(self.dframe[dst])):
                for i in range(min(self.dframe[src]), max(self.dframe[src])):
                    p += self.p(**{dst: j}) * (self.p(**{src: i, dst: j}) * math.log2(self.p(**{src: i, dst: j})))
        return abs(p)

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
        return self.cache(pd.DataFrame.from_dict(d))


if __name__ == '__main__':
    e = Entropy()
    dfs = e.load(res='x', y=[0, 1], z=[1, 1, 2, 3])
    print(e.transform(e.combine(list(dfs))))
    print(e.calculate('y', 'x'))
