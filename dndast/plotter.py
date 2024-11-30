import plotly.graph_objects as go
from igraph import Graph


NODE_COLORS = {
    'AttackNode':     'rgba(255,  98,  62, 1.0)', # red-ish
    'AttackRollNode': 'rgba(231,  98,  62, 1.0)', # red
    'DamageNode':     'rgba(171, 109, 172, 1.0)', # purple
    'EmptyNode':      'rgba(145, 161, 178, 1.0)', # grey-blue
    'ReferenceNode':  'rgba(122, 133,  59, 1.0)', # dirty-green
    'RollNode':       'rgba(127,  81,  62, 1.0)', # brown-red
    'SaveNode':       'rgba( 81, 165, 197, 1.0)', # teal-blue
    'SaveRollNode':   'rgba( 81, 165, 255, 1.0)', # blue-ish
    'SelectionNode':  'rgba(181, 158,  84, 1.0)', # tan
    'TargetingNode':  'rgba(100, 158,  84, 1.0)', # tan-ish
    'ValueNode':      'rgba( 80, 127,  98, 1.0)', # darker-green
}

def plot_tree_diagram(tree, **kwargs):
    if type(tree) is dict:
        dtree, nodes = convert_tree(tree)
    else:
        dtree, nodes = convert_tree(tree.to_dict())

    ids = list(set([x for v in dtree.values() for x in v] + [k for k in dtree.keys()]))
    nr_vertices = len(ids)

    graph = Graph.ListDict(dtree)
    lay = graph.layout('tree', root=[0])
    position = {k: lay[k] for k in range(nr_vertices)}
    #print(f'ids = {ids}')
    #print(f'positions = {len(position)}, nodes = {len(nodes)}')

    fig = kwargs.get('fig', go.Figure())

    # plot edges
    edges = [e.tuple for e in graph.es]
    Xe = []
    Ye = []
    for edge in edges:
        Xe += [position[edge[0]][0], position[edge[1]][0], None]
        Ye += [position[edge[0]][1], position[edge[1]][1], None]

    fig.add_trace(go.Scatter(
        x=Xe,
        y=Ye,
        mode='lines',
        line=dict(
            color=kwargs.get('edge_line_color', 'rgb(210,210,210)'), 
            width=kwargs.get('edge_line_width', 1),
        ),
        hoverinfo='none',
    ))

    # plot nodes
    Xn = [position[k][0] for k in range(len(position))]
    Yn = [position[k][1] for k in range(len(position))]
    dx, dy = node_size(Xn, Yn)
    #print(f'dx = {dx}; dy = {dy}')
    for i in range(len(position)):
        # add shape for node
        fig.add_shape(
            type="rect",
            x0=Xn[i]-dx, x1=Xn[i]+dx,
            y0=Yn[i]-dy, y1=Yn[i]+dy,
            line=dict(
                color=kwargs.get('node_line_color', 'rgba(250,250,250,1)'), 
                width=kwargs.get('node_line_width', 1),
            ),
            fillcolor=NODE_COLORS[nodes[i]['node']+'Node'],
            opacity=1.0,
        )

        # add hover text
        fig.add_trace(go.Scatter(
            x=[Xn[i]],
            y=[Yn[i]],
            mode='markers',
            marker=dict(
                color=NODE_COLORS[nodes[i]['node']+'Node'],
            ),
            opacity=0.0,
            text=[node_hovertext(nodes[i])],
            hoverinfo='text',
        ))

    # add annotations
    #print(f'x-range = {[min(Xn) - 1.5*dx, max(Xn) + 1.5*dx]}')
    #print(f'y-range = {[min(Yn) - 1.5*dy, max(Yn) + 1.5*dy]}')
    fig.update_layout(
        annotations=make_annotations(position, [n['node'] for n in nodes], **kwargs),
        xaxis=dict(range=[min(Xn) - 1.5*dx, max(Xn) + 1.5*dx]),
        yaxis=dict(range=[min(Yn) - 1.5*dy, max(Yn) + 1.5*dy]),
    )
    return fig


def node_size(Xn, Yn):
    Xmin = min(Xn)
    Xmax = max(Xn)
    Xcount = len(list(set(Xn)))
    if Xcount > 1:
        dx = 0.45*(Xmax - Xmin)/(Xcount-1)
    else:
        dx = 0.45*0.5
    
    Ymin = min(Yn)
    Ymax = max(Yn)
    Ycount = len(list(set(Yn)))
    if Ycount > 1:
        dy = 0.20*(Ymax - Ymin)/(Ycount-1)
    else:
        dy = 0.20*1.0
    
    return dx, dy


def make_annotations(pos, text, **kwargs):
    if len(text) != len(pos):
        raise ValueError('The lists pos and text must have the same len')
    
    annotations = []
    for k in range(len(pos)):
        annotations.append(
            dict(
                text=text[k],
                x=pos[k][0], 
                y=pos[k][1],
                xref='x1', 
                yref='y1',
                font=dict(
                    color=kwargs.get('annotation_font_color', 'rgba(250,250,250,1)'), 
                    size=kwargs.get('annotation_font_size', 10),
                ),
                showarrow=False,
            )
        )
    return annotations


def node_hovertext(node):
    hovertext = '<b>'+node['node']+'</b>'
    for k, v in node.items():
        if k == 'node': continue
        if type(v) is dict:
            if 'node' in v:
                hovertext += f'<br>{k}: ' + v['node'] + 'Node'
            else:
                hovertext += f'<br>{k}: {v}'
        else:
            hovertext += f'<br>{k}: {v}'
    return hovertext


def convert_tree(tree, i=0, ctree={}, nodes=[]):
    if i == 0:
        ctree = {}
        nodes = []
    
    iself = i
    ctree[iself] = []
    if i == 0:
        nodes = [tree.copy()]
    else:
        nodes += [tree.copy()]
    for k, v in tree.items():
        if type(v) != dict: continue

        if v.get('node', None):
            i += 1
            ctree[iself] += [i]
            ctree, nodes, i = convert_tree(v, i=i, ctree=ctree, nodes=nodes)
        else:
            for kk, vv in v.items():
                if type(vv) != dict: continue
                if vv.get('node', None):
                    i += 1
                    ctree[iself] += [i]
                    ctree, nodes, i = convert_tree(vv, i=i, ctree=ctree, nodes=nodes)
    if iself == 0:
        return ctree, nodes
    else:
        return ctree, nodes, i