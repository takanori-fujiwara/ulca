import copy
import json
import threading
import webbrowser
import numpy as np
import pandas as pd
from enum import IntEnum
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

from IPython.display import IFrame
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from scipy.spatial.distance import pdist

from ulca_ui.utils.weight_opt import optimize_cost
from ulca_ui.utils.geom_trans import find_best_rotate


class Info():
    def __init__(self):
        self.verbose = False
        self.dr = None
        self.X = None
        self.y = None
        self.w_tg = None
        self.w_bg = None
        self.w_bw = None
        self.alpha = None
        self.max_alpha = None
        self.Covs = None
        self.w_area = {'move': 0.5, 'scale': 0.5},
        self.w_dist = {'move': 0.5, 'scale': 0.5}
        self.weight_opt_max_iter = 0
        self.feat_names = None
        self.y_to_name = None
        self.new_comp = {}

    def _output_as_json(self):
        n_feats, n_comps = self.dr.M.shape

        # output Z, y, weights as json
        weights = {'tg': None, 'bg': None, 'bw': None}

        weights['tg'] = [{
            'label': int(key),
            'val': float(self.w_tg[key])
        } for key in self.w_tg]

        weights['bg'] = [{
            'label': int(key),
            'val': float(self.w_bg[key])
        } for key in self.w_bg]

        weights['bw'] = [{
            'label': int(key),
            'val': float(self.w_bw[key])
        } for key in self.w_bw]

        label_to_name = {'alpha': 'Trade-off'}
        for key in self.y_to_name:
            label_to_name[int(key)] = str(self.y_to_name[key])

        Z = self.dr.transform(self.X)
        df_emb = pd.DataFrame({
            'x': Z[:, 0],
            'y': Z[:, 1],
            'label': self.y,
            'feat_vals': self.X.tolist()
        })
        emb = json.loads(df_emb.to_json(orient='records'))

        data = {
            'weights': weights,
            'bounds': [{
                'label': 'alpha',
                'val': float(self.alpha)
            }],
            'max_upper_bound': float(self.max_alpha),
            'emb': emb,
            'components': {
                'x': list(self.dr.M[:, 0]),
                'y':
                list(self.dr.M[:, 1] if n_comps >= 2 else np.zeros((n_feats))),
                'feat_names': list(self.feat_names)
            },
            'label_to_name': label_to_name
        }

        return data


info = Info()
saved_info = {}


class Message(IntEnum):
    updateEmb = 0
    optimizeWeights = 1
    saveResult = 2
    loadResult = 3
    initialLoad = 4
    addNewComp = 5

    @property
    def key(self):
        if self == Message.updateEmb:
            return 'updateEmb'
        elif self == Message.optimizeWeights:
            return 'optimizeWeights'
        elif self == Message.saveResult:
            return 'saveResult'
        elif self == Message.loadResult:
            return 'loadResult'
        elif self == Message.initialLoad:
            return 'initialLoad'
        elif self == Message.addNewComp:
            return 'addNewComp'

    @property
    def label(self):
        if self == Message.updateEmb:
            return 'updateEmb'
        elif self == Message.optimizeWeights:
            return 'optimizeWeights'
        elif self == Message.saveResult:
            return 'saveResult'
        elif self == Message.loadResult:
            return 'loadResult'
        elif self == Message.initialLoad:
            return 'initialLoad'
        elif self == Message.addNewComp:
            return 'addNewComp'


class WsHandler(WebSocket):
    def _update_emb(self, content):
        # read from records and take only x and y positions
        Z_prev = np.array(
            pd.DataFrame.from_records(content['data']['emb'])[['x', 'y']])
        for key in content['data']['weights']:
            for w in content['data']['weights'][key]:
                getattr(info, f'w_{key}')[w['label']] = w['val']

        for bound in content['data']['bounds']:
            if bound['label'] == 'alpha':
                info.alpha = bound['val']

        info.dr = info.dr.fit(info.X,
                              y=info.y,
                              w_tg=info.w_tg,
                              w_bg=info.w_bg,
                              w_bw=info.w_bw,
                              Covs=info.Covs,
                              alpha=info.alpha)
        Z = info.dr.transform(info.X)

        if Z_prev.shape[0] > 0:
            R = find_best_rotate(Z_prev, Z)
            info.dr.update_projector(info.dr.M @ R)
            Z = info.dr.transform(info.X)

        df_emb = pd.DataFrame({
            'x': Z[:, 0],
            'y': Z[:, 1],
            'label': info.y,
            'feat_vals': info.X.tolist()
        })
        emb = json.loads(df_emb.to_json(orient='records'))

        n_feats, n_comps = info.dr.M.shape
        comps = {
            'x': list(info.dr.M[:, 0]),
            'y': list(info.dr.M[:,
                                1] if n_comps >= 2 else np.zeros((n_feats))),
            'feat_names': list(info.feat_names)
        }
        data = {
            'weights': content['data']['weights'],
            'bounds': [{
                'label': 'alpha',
                'val': float(info.alpha)
            }],
            'max_upper_bound': float(info.max_alpha),
            'emb': emb,
            'components': comps
        }

        return json.dumps({'action': Message.updateEmb, 'content': data})

    def _optimize_weights(self, content):
        with_alpha = True

        # read from records and take only x and y positions
        Z_prev = np.array(
            pd.DataFrame.from_records(content['data']['emb'])[['x', 'y']])

        for key in content['data']['weights']:
            for w in content['data']['weights'][key]:
                getattr(info, f'w_{key}')[w['label']] = w['val']

        initial_weights = list(info.w_tg.values()) + list(
            info.w_bg.values()) + list(info.w_bw.values())
        updated_label = content['data']['updated_label']

        w_area = info.w_area[content['data']['interaction']]
        w_dist = info.w_dist[content['data']['interaction']]

        areas = {}
        n_labels = len(content['data']['ellipses'])
        ellipse_centers = np.zeros((n_labels, 2))
        for i, ellipse in enumerate(content['data']['ellipses']):
            label = ellipse['label']
            # se_ratio[label] = np.abs(ellipse['rx']) + np.abs(ellipse['ry'])
            # skip using pi
            areas[label] = np.abs(ellipse['rx']) * np.abs(ellipse['ry'])
            ellipse_centers[i, 0] = ellipse['cx']
            ellipse_centers[i, 1] = ellipse['cy']
        center_dists = pdist(ellipse_centers)

        new_weights, cost = optimize_cost(
            dr=info.dr,
            initial_weights=initial_weights,
            updated_label=updated_label,
            ideal_areas=areas,
            ideal_dists=center_dists,
            X=info.X,
            y=info.y,
            with_alpha=with_alpha,
            alpha=info.alpha,
            Covs=info.Covs,
            w_area=w_area,
            w_dist=w_dist,
            Z_prev=Z_prev,
            apply_geom_trans=True,
            n_components=2,
            method='COBYLA',
            options={'maxiter': info.weight_opt_max_iter})

        new_w_tg = {}
        new_w_bg = {}
        new_w_bw = {}
        for i, label in enumerate(info.w_tg):
            new_w_tg[label] = new_weights[i]
        for i, label in enumerate(info.w_bg):
            new_w_bg[label] = new_weights[i + n_labels]
        for i, label in enumerate(info.w_bw):
            new_w_bw[label] = new_weights[i + n_labels * 2]
        if with_alpha:
            info.alpha = new_weights[-1]

        info.w_tg = new_w_tg
        info.w_bg = new_w_bg
        info.w_bw = new_w_bw
        info.dr = info.dr.fit(info.X,
                              y=info.y,
                              w_tg=new_w_tg,
                              w_bg=new_w_bg,
                              w_bw=new_w_bw,
                              Covs=info.Covs,
                              alpha=info.alpha)
        Z = info.dr.transform(info.X)

        if Z_prev.shape[0] > 0:
            R = find_best_rotate(Z_prev, Z)
            info.dr.update_projector(info.dr.M @ R)
            Z = info.dr.transform(info.X)

        df_emb = pd.DataFrame({
            'x': Z[:, 0],
            'y': Z[:, 1],
            'label': info.y,
            'feat_vals': info.X.tolist()
        })
        emb = json.loads(df_emb.to_json(orient='records'))

        n_feats, n_comps = info.dr.M.shape
        comps = {
            'x': list(info.dr.M[:, 0]),
            'y': list(info.dr.M[:,
                                1] if n_comps >= 2 else np.zeros((n_feats))),
            'feat_names': list(info.feat_names)
        }

        weights = {'tg': None, 'bg': None, 'bw': None}
        weights['tg'] = [{
            'label': int(key),
            'val': float(new_w_tg[key])
        } for key in new_w_tg]
        weights['bg'] = [{
            'label': int(key),
            'val': float(new_w_bg[key])
        } for key in new_w_bg]
        weights['bw'] = [{
            'label': int(key),
            'val': float(new_w_bw[key])
        } for key in new_w_bw]

        data = {
            'weights': weights,
            'bounds': [{
                'label': 'alpha',
                'val': float(info.alpha)
            }],
            'max_upper_bound': float(info.max_alpha),
            'emb': emb,
            'components': comps
        }

        return json.dumps({'action': Message.optimizeWeights, 'content': data})

    def _save_result(self, content):
        saved_info[content['name']] = copy.deepcopy(info)

        return json.dumps({
            'action': Message.saveResult,
            'content': {
                'dataNames': list(saved_info)
            }
        })

    def _load_result(self, content):
        info = copy.deepcopy(saved_info[content['name']])
        data = info._output_as_json()

        return json.dumps({'action': Message.loadResult, 'content': data})

    def _initial_load(self):
        data = info._output_as_json()

        return json.dumps({'action': Message.initialLoad, 'content': data})

    def _add_new_component(self, content):
        info.new_comp[content['key']] = content['component']

    def handleMessage(self):
        m = json.loads(self.data)
        m_action = m['action']

        if m_action == Message.updateEmb:
            self.sendMessage(self._update_emb(m['content']))
        elif m_action == Message.optimizeWeights:
            self.sendMessage(self._optimize_weights(m['content']))
        elif m_action == Message.saveResult:
            self.sendMessage(self._save_result(m['content']))
        elif m_action == Message.loadResult:
            self.sendMessage(self._load_result(m['content']))
        elif m_action == Message.addNewComp:
            self._add_new_component(m['content'])
        else:
            if info.verbose:
                print('received action:', m_action)

    def handleConnected(self):
        if info.verbose:
            print(self.address, 'connected')
        self.sendMessage(self._initial_load())

    def handleClose(self):
        if info.verbose:
            print(self.address, 'closed')


class Singleton(object):
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class Plot(Singleton):
    def __init__(self, http_port=8000, ws_port=9000):
        # use singleton and the condition below to avoid conflict due to
        # usage of the same html server address
        if len(vars(self)) == 0:
            self.http_port = http_port
            self.html_server = None
            self.html_server_thread = None
            self.ws_port = ws_port
            self.ws_server = None
            self.ws_server_thread = None

    def plot_emb(self,
                 dr,
                 X,
                 y,
                 w_tg={},
                 w_bg={},
                 w_bw={},
                 Covs={},
                 alpha=None,
                 max_alpha=10,
                 feat_names=None,
                 y_to_name={},
                 w_area={
                     'move': 0.2,
                     'scale': 0.8
                 },
                 w_dist={
                     'move': 0.8,
                     'scale': 0.2
                 },
                 weight_opt_max_iter=50,
                 inline_mode=True):

        # start html server thread
        class HTTPHandler(SimpleHTTPRequestHandler):
            def __init__(self, request, client_address, server):
                self.directory = Path(__file__).parent
                super().__init__(request,
                                 client_address,
                                 server,
                                 directory=self.directory)

            def log_message(self, format, *args):
                # This is to avoid outputting log messages in notebook
                None

        # start html server thread
        if self.html_server is None:
            try:
                self.html_server = HTTPServer(('localhost', self.http_port),
                                              HTTPHandler)
            except:
                print(
                    'shutdown jupyter kernel using UI before starting to use UI in a new notebook'
                )
                return

            self.html_server_thread = threading.Thread(
                target=self.html_server.serve_forever)
            self.html_server_thread.daemon = True
            self.html_server_thread.start()

        # start websocket server thread
        if self.ws_server is None:
            try:
                self.ws_server = SimpleWebSocketServer('', self.ws_port,
                                                       WsHandler)
            except:
                print(
                    'shutdown jupyter kernel using UI before starting to use UI in a new notebook'
                )
                return

            self.ws_server_thread = threading.Thread(
                target=self.ws_server.serveforever)
            self.ws_server_thread.daemon = True
            self.ws_server_thread.start()

        if w_tg == {}:
            for label in np.unique(y):
                w_tg[label] = 0
        if w_bg == {}:
            for label in np.unique(y):
                w_bg[label] = 1
        if w_bw == {}:
            for label in np.unique(y):
                w_bw[label] = 1
        if feat_names is None:
            feat_names = list(range(X.shape[1]))
        if y_to_name == {}:
            for label in np.unique(y):
                y_to_name[label] = f'Label {label}'
        if alpha is None:
            alpha = 1 / dr.get_final_cost()

        info.dr = dr
        info.X = X
        info.y = y
        info.w_tg = w_tg
        info.w_bg = w_bg
        info.w_bw = w_bw
        info.alpha = alpha
        info.max_alpha = max_alpha
        info.Covs = Covs
        info.w_area = w_area
        info.w_dist = w_dist
        info.feat_names = feat_names
        info.y_to_name = y_to_name
        info.weight_opt_max_iter = weight_opt_max_iter

        if len(saved_info) == 0:
            saved_info['-'] = copy.deepcopy(info)

        # load local webpage
        url = f'http://localhost:{self.http_port}/'
        view = IFrame(src=url, width='100%',
                      height='500px') if inline_mode else webbrowser.open(url)

        return view

    def current_info(self):
        return info

    def saved_info(self):
        return saved_info
