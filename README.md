# dndast

This library contains nodes that can be used to describe 5th edition D&D game mechanics as abstract syntax trees.

For example, a simple melee attack with a +4 to hit that deals 1d6 slashing damage on a hit and 2d6 slashing damage on a critical hit can be represented as follows,

```python
from dndast.nodes import *

tree = {
    'node': 'Attack',
    'targeting': {
        'node': 'Targeting',
        'range': '5 feet',
        'area': None,
        'max_targets': 1,
        'min_targets': 0,
    },
    'attack_roll': {
        'node': 'AttackRoll',
        'critical_hit_range': [20],
        'critical_miss_range': [1],
        'attack_bonus': 4,
        'armor_class': {
            'node': 'Reference',
            'value': 'target.armor_class',
        },
    },
    'results': {
        'critical miss': 0,
        'miss': 0,
        'hit': {'node': 'Damage', 'value': '1d6', 'type': 'slashing'},
        'critical hit': {'node': 'Damage', 'value': '2d6', 'type': 'slashing'},
    },
}
```

After converting this dictionary into a tree using the `dict_to_node` function, it can be represented graphically as a tree using the plotter tool, along with plotly.

```python
from dndast.plotter import plot_tree_diagram
import plotly.graph_objects as go

fig = go.Figure(
    layout=go.Layout(
        template='plotly_white',
        margin=dict(l=60, r=25, b=55, t=20, pad=4),
        showlegend=False,
        xaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False, ticks="", minor_ticks=""),
        yaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False, ticks="", minor_ticks=""),
        hovermode='closest',
    ),
)

tree = dict_to_node(tree)
fig = plot_tree_diagram(tree, fig=fig)

fig.update_layout(width=600, height=450)
fig.show()
```

![AST graph example](https://raw.githubusercontent.com/tomedunn/dnd5e_abstract_syntax_tree/refs/heads/main/assets/images/example-1.png)

Mechanics represented in this way can be evaluated using the interpreter tool along with a targets dictionary. In this case, since the range of our attack is 5 feet, we only need to define a melee target. And, since the only attribute we need from the target is its armor class, we only need to give it that attribute.

```python
from dndast.interpreter import Interpreter

TARGETS = {
    'maxtargets': 5,
    'melee_maxtargets': 2,
    'melee_target': {
        'armor_class': 18,
    },
    'ranged_targetarea': 100,
    'ranged_maxtargets': 4,
    'ranged_target': {},
}

interpreter = Interpreter(targets=TARGETS)
result = interpreter.evaluate(tree)

"""
| Outcome | Quantity | Probability |
|--------:|---------:|------------:|
|       0 |      468 |  65.000000% |
|       1 |       36 |   5.000000% |
|       2 |       37 |   5.138889% |
|       3 |       38 |   5.277778% |
|       4 |       39 |   5.416667% |
|       5 |       40 |   5.555556% |
|       6 |       41 |   5.694444% |
|       7 |        6 |   0.833333% |
|       8 |        5 |   0.694444% |
|       9 |        4 |   0.555556% |
|      10 |        3 |   0.416667% |
|      11 |        2 |   0.277778% |
|      12 |        1 |   0.138889% |
"""
```