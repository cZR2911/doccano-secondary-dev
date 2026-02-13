import abc
import dataclasses
import enum
import random
from typing import List

import numpy as np


@dataclasses.dataclass
class Assignment:
    user: int
    example: int


class StrategyName(enum.Enum):
    # 对应前端：项目设置 -> 成员管理 -> 自动分配 -> 策略选择
    # 场景：当你有一批数据需要分给不同成员标注时使用
    weighted_sequential = enum.auto()  # 加权顺序分配
    weighted_random = enum.auto()      # 加权随机分配
    sampling_without_replacement = enum.auto() # 不放回采样


def create_assignment_strategy(strategy_name: StrategyName, dataset_size: int, weights: List[int]) -> "BaseStrategy":
    if strategy_name == StrategyName.weighted_sequential:
        return WeightedSequentialStrategy(dataset_size, weights)
    elif strategy_name == StrategyName.weighted_random:
        return WeightedRandomStrategy(dataset_size, weights)
    elif strategy_name == StrategyName.sampling_without_replacement:
        return SamplingWithoutReplacementStrategy(dataset_size, weights)
    else:
        raise ValueError(f"Unknown strategy name: {strategy_name}")


class BaseStrategy(abc.ABC):
    @abc.abstractmethod
    def assign(self) -> List[Assignment]: ...


class WeightedSequentialStrategy(BaseStrategy):
    """
    【加权顺序分配策略】
    前端表现：按比例切块，整齐划一。
    数学原理：累积分布函数 (CDF) 的逆向应用。
    
    举例：100条数据，用户A(20%), B(30%), C(50%)。
    - 0-20条给A
    - 21-50条给B
    - 51-100条给C
    
    优点：简单直观，每个人分到的数据是连续的。
    缺点：如果数据本身有时间序列偏差（如前20条全是负样本），会导致用户A只标到负样本。
    """
    def __init__(self, dataset_size: int, weights: List[int]):
        if sum(weights) != 100:
            raise ValueError("Sum of weights must be 100")
        self.dataset_size = dataset_size
        self.weights = weights

    def assign(self) -> List[Assignment]:
        assignments = []
        # np.cumsum: 计算累积和。例：[20, 30, 50] -> [0, 20, 50, 100]
        # 这就像在切蛋糕，算出了每一刀切在什么位置
        cumsum = np.cumsum([0] + self.weights)
        # 将百分比位置映射到具体的数据索引上
        ratio = np.round(cumsum / 100 * self.dataset_size).astype(int)
        # zip(ratio, ratio[1:]): 生成区间 [(0, 20), (20, 50), (50, 100)]
        for user, (start, end) in enumerate(zip(ratio, ratio[1:])):  # Todo: use itertools.pairwise
            assignments.extend([Assignment(user=user, example=example) for example in range(start, end)])
        return assignments


class WeightedRandomStrategy(BaseStrategy):
    """
    【加权随机分配策略】
    前端表现：每个样本随机分给某人，概率由权重决定。
    数学原理：多项分布采样 (Multinomial Sampling)。
    
    举例：100条数据，用户A(20%)。
    - 每条数据都有20%的概率分给A。
    - 最终A可能分到18条，也可能22条（符合大数定律，均值趋近20条）。
    - 允许重复：如果不加控制，同一个样本理论上可能被多次选中（但在本逻辑中是遍历size生成，主要用于一次性分配）。
    
    优点：消除数据顺序带来的偏差。
    """
    def __init__(self, dataset_size: int, weights: List[int]):
        if sum(weights) != 100:
            raise ValueError("Sum of weights must be 100")
        self.dataset_size = dataset_size
        self.weights = weights

    def assign(self) -> List[Assignment]:
        # 将权重 [20, 80] 转换为概率 [0.2, 0.8]
        proba = np.array(self.weights) / 100
        # np.random.choice: 核心概率采样函数
        # size=dataset_size: 为每一条数据掷一次骰子，决定它归谁
        assignees = np.random.choice(range(len(self.weights)), size=self.dataset_size, p=proba)
        return [Assignment(user=user, example=example) for example, user in enumerate(assignees)]


class SamplingWithoutReplacementStrategy(BaseStrategy):
    """
    【不放回采样策略】
    前端表现：重叠分配，常用于多人交叉验证（Inter-Annotator Agreement）。
    数学原理：超几何分布思想 (Hypergeometric-like)，确切数量的随机抽取。
    
    举例：100条数据，用户A(50%), B(50%)。总权重100。
    - A随机分50条。
    - B随机分50条。
    - A和B的数据可能重叠，也可能完全不重叠。
    
    注意：这里 sum(weights) 可以超过100！
    例如 A(100%), B(100%) -> 每个人都标所有数据（完全交叉验证）。
    """
    def __init__(self, dataset_size: int, weights: List[int]):
        if not (0 <= sum(weights) <= 100 * len(weights)):
            raise ValueError("Sum of weights must be between 0 and 100 x number of members")
        self.dataset_size = dataset_size
        self.weights = weights

    def assign(self) -> List[Assignment]:
        assignments = []
        proba = np.array(self.weights) / 100
        for user, p in enumerate(proba):
            # 确定该用户必须分到多少条数据 (e.g. 100 * 0.5 = 50条)
            count = int(self.dataset_size * p)
            # random.sample: 不放回抽样。保证该用户拿到的50条数据互不相同。
            examples = random.sample(range(self.dataset_size), count)
            assignments.extend([Assignment(user=user, example=example) for example in examples])
        return assignments
