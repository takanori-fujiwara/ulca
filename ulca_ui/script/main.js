import * as m from './model.js';
import * as util from './d3_utils.js';
import * as wv from './weight_view.js';
import * as ev from './emb_view.js';
import * as cv from './component_view.js';
import * as fnv from './feat_name_view.js';

m.wsInfo.ws = new WebSocket(m.wsUrl);
const tgWeightChart = wv.genChart('tgWeight');
const bgWeightChart = wv.genChart('bgWeight');
const bwWeightChart = wv.genChart('bwWeight');
let ratioBoundChart = wv.genChart('ratioBoundary', 10);
const embChart = ev.genChart();
const compXChart = cv.genChart('compX');
const compYChart = cv.genChart('compY');
const compFeatNameChart = fnv.genChart();

const init = (content) => {
  util.initSvgInfo({
    'svgData': m.allSvgData.tgWeight,
    'domId': 'tg_weight_svg'
  }, {
    top: 25,
    right: 30,
    bottom: 25,
    left: 60
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.bgWeight,
    'domId': 'bg_weight_svg'
  }, {
    top: 25,
    right: 30,
    bottom: 25,
    left: 60
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.bwWeight,
    'domId': 'bw_weight_svg'
  }, {
    top: 25,
    right: 30,
    bottom: 25,
    left: 60
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.ratioBoundary,
    'domId': 'ratio_bound_svg'
  }, {
    top: 25,
    right: 30,
    bottom: 25,
    left: 60
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.emb,
    'domId': 'emb_svg'
  }, {
    top: 50,
    right: 50,
    bottom: 50,
    left: 50
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.compX,
    'domId': 'comp_x_svg'
  }, {
    top: 25,
    right: 5,
    bottom: 40,
    left: 10
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.compY,
    'domId': 'comp_y_svg'
  }, {
    top: 25,
    right: 2,
    bottom: 40,
    left: 10
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.compFeatName,
    'domId': 'comp_feat_name_svg'
  }, {
    top: 25,
    right: 0,
    bottom: 40,
    left: 0
  });

  m.allSvgData.tgWeight.subtitle = 'Target weight';
  m.allSvgData.tgWeight.contentType = 'w_tg';
  m.allSvgData.tgWeight.data = content.weights.tg;

  m.allSvgData.bgWeight.subtitle = 'Background weight';
  m.allSvgData.bgWeight.contentType = 'w_bg';
  m.allSvgData.bgWeight.data = content.weights.bg;

  m.allSvgData.bwWeight.subtitle = 'Between-class weight';
  m.allSvgData.bwWeight.contentType = 'w_bw';
  m.allSvgData.bwWeight.data = content.weights.bw;

  m.allSvgData.ratioBoundary.subtitle = 'Other parameters';
  m.allSvgData.ratioBoundary.contentType = 'bounds';
  m.allSvgData.ratioBoundary.data = content.bounds;
  ratioBoundChart = wv.genChart('ratioBoundary', content.max_upper_bound);

  m.allSvgData.emb.contentType = 'emb';
  m.allSvgData.emb.data = content.emb;

  m.allSvgData.compX.subtitle = 'x';
  m.allSvgData.compX.contentType = 'compX';
  m.allSvgData.compX.data = content.components.x;
  m.allSvgData.compY.subtitle = 'y';
  m.allSvgData.compY.contentType = 'compY';
  m.allSvgData.compY.data = content.components.y;
  m.allSvgData.compFeatName.subtitle = 'Feature name';
  m.allSvgData.compFeatName.contentType = 'compFeatName';
  m.allSvgData.compFeatName.data = content.components.feat_names;

  m.allSvgData.labelToName.data = content.label_to_name;

  tgWeightChart(m.allSvgData, m.wsInfo);
  bgWeightChart(m.allSvgData, m.wsInfo);
  bwWeightChart(m.allSvgData, m.wsInfo);
  ratioBoundChart(m.allSvgData, m.wsInfo);
  embChart(m.allSvgData, m.wsInfo);
  compXChart(m.allSvgData);
  compYChart(m.allSvgData);
  compFeatNameChart(m.allSvgData, m.wsInfo);
}

m.wsInfo.ws.onmessage = wsEvent => {
  const data = JSON.parse(wsEvent.data);
  const content = data.content;
  const action = data.action;
  m.allSvgData.tgWeight.data.length = 0;
  m.allSvgData.bgWeight.data.length = 0;
  m.allSvgData.bwWeight.data.length = 0;
  m.allSvgData.ratioBoundary.data.length = 0;
  m.allSvgData.emb.data.length = 0;

  if (action === m.wsInfo.messageActions.initialLoad) {
    init(content);
    document.querySelector('#data_names').addEventListener('change', () => {
      const dataName = document.querySelector('#data_names').value;
      const content = {};
      content.name = dataName;
      m.wsInfo.ws.send(JSON.stringify({
        action: m.wsInfo.messageActions.loadResult,
        content: content
      }));
    });

    document.querySelector('#save_button').addEventListener('click', () => {
      const newDataName = document.querySelector('#new_data_name').value;

      if (m.wsInfo !== null) {
        const content = {};
        content.name = newDataName;

        m.wsInfo.ws.send(JSON.stringify({
          action: m.wsInfo.messageActions.saveResult,
          content: content
        }));
      }
    });
  } else if (action === m.wsInfo.messageActions.saveResult) {
    document.querySelector('#save_button').innerHTML =
      '<span style="font-weight: bold; color: #c53a32;">Done</span>';
    setTimeout(() => {
      document.querySelector('#save_button').innerHTML = 'Save'
    }, 1000);

    const dataNameSelect = document.querySelector('#data_names');
    dataNameSelect.options.length = 0;

    for (const name of content.dataNames) {
      const option = document.createElement('option');
      option.text = name;
      option.value = name;
      dataNameSelect.add(option, 0)
      dataNameSelect.selectedIndex = 0;
    }
  } else if (action === m.wsInfo.messageActions.loadResult) {
    init(content);
  } else {
    for (const d of content.weights.tg) {
      m.allSvgData.tgWeight.data.push(d);
    }
    for (const d of content.weights.bg) {
      m.allSvgData.bgWeight.data.push(d);
    }
    for (const d of content.weights.bw) {
      m.allSvgData.bwWeight.data.push(d);
    }
    for (const d of content.bounds) {
      m.allSvgData.ratioBoundary.data.push(d);
    }
    for (const d of content.emb) {
      m.allSvgData.emb.data.push(d);
    };
    m.allSvgData.compX.data = content.components.x;
    m.allSvgData.compY.data = content.components.y;
    m.allSvgData.compFeatName.data = content.components.feat_names;
    tgWeightChart(m.allSvgData, m.wsInfo, false);
    bgWeightChart(m.allSvgData, m.wsInfo, false);
    bwWeightChart(m.allSvgData, m.wsInfo, false);
    ratioBoundChart(m.allSvgData, m.wsInfo, false);
    embChart(m.allSvgData, m.wsInfo, false);

    // TODO: this part is not clean. Do refactoring later.
    let newCompExisted = false;
    for (const key of Object.keys(m.allSvgData)) {
      const strings = key.split('comp')
      if (strings.length > 1) {
        if (strings[1] !== 'X' && strings[1] !== 'Y' && strings[1] !== 'FeatName') {
          d3.select(`#comp_${strings[1]}_svg`).remove();
          newCompExisted = true;
        }
      }
    }
    const compsArea = d3.select('#comps').node().getBoundingClientRect();
    d3.selectAll('.comp').style('width', `${compsArea.width / 2}px`);

    if (newCompExisted) {
      util.initSvgInfo({
        'svgData': m.allSvgData.compX,
        'domId': `comp_x_svg`
      }, {
        top: 25,
        right: 2,
        bottom: 40,
        left: 10
      });

      util.initSvgInfo({
        'svgData': m.allSvgData.compY,
        'domId': `comp_y_svg`
      }, {
        top: 25,
        right: 2,
        bottom: 40,
        left: 10
      });
      //////////
      compXChart(m.allSvgData, true);
      compYChart(m.allSvgData, true);
      compFeatNameChart(m.allSvgData, m.wsInfo, false);
    } else {
      compXChart(m.allSvgData, false);
      compYChart(m.allSvgData, false);
      compFeatNameChart(m.allSvgData, m.wsInfo, false);
    }
  }
}

// TODO: avoid recompuing confidence area info when applying resize
window.onresize = (e) => {
  util.initSvgInfo({
    'svgData': m.allSvgData.emb,
    'domId': 'emb_svg'
  }, {
    top: 50,
    right: 50,
    bottom: 50,
    left: 50
  });
  util.initSvgInfo({
    'svgData': m.allSvgData.tgWeight,
    'domId': 'tg_weight_svg'
  }, {
    top: 45,
    right: 30,
    bottom: 45,
    left: 60
  });
  util.initSvgInfo({
    'svgData': m.allSvgData.bgWeight,
    'domId': 'bg_weight_svg'
  }, {
    top: 45,
    right: 30,
    bottom: 45,
    left: 60
  });
  util.initSvgInfo({
    'svgData': m.allSvgData.bwWeight,
    'domId': 'bw_weight_svg'
  }, {
    top: 45,
    right: 30,
    bottom: 45,
    left: 60
  });
  util.initSvgInfo({
    'svgData': m.allSvgData.ratioBoundary,
    'domId': 'ratio_bound_svg'
  }, {
    top: 45,
    right: 30,
    bottom: 45,
    left: 60
  });
  util.initSvgInfo({
    'svgData': m.allSvgData.compX,
    'domId': 'comp_x_svg'
  }, {
    top: 50,
    right: 5,
    bottom: 40,
    left: 10
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.compY,
    'domId': 'comp_y_svg'
  }, {
    top: 50,
    right: 2,
    bottom: 40,
    left: 10
  });

  util.initSvgInfo({
    'svgData': m.allSvgData.compFeatName,
    'domId': 'comp_feat_name_svg'
  }, {
    top: 50,
    right: 0,
    bottom: 40,
    left: 0
  });

  tgWeightChart(m.allSvgData, m.wsInfo);
  bgWeightChart(m.allSvgData, m.wsInfo);
  bwWeightChart(m.allSvgData, m.wsInfo);
  ratioBoundChart(m.allSvgData, m.wsInfo);
  embChart(m.allSvgData, m.wsInfo);
  compXChart(m.allSvgData);
  compYChart(m.allSvgData);
  compFeatNameChart(m.allSvgData, m.wsInfo);
};