import {
  pallette,
  percentColToD3Rgb
} from './colors.js';

import {
  genX,
  genY,
  genInvX,
  setCategoryLegend
} from './d3_utils.js';

// TODO: put these in a separate file (e.g., update.js)
import * as ev from './emb_view.js';
const embChart = ev.genChart();

export const genChart = () => {
  let svg = null;
  let bar = null;
  let barXAxis = null;
  let barYAxis = null;
  let mouseEventInfo = null;

  const chart = (allSvgData, wsInfo = null, init = true) => {
    const svgData = allSvgData.compFeatName;

    if (init) {
      svgData.svgArea.height =
        svgData.data.length * 30 < svgData.svgArea.height ?
        svgData.data.length * 30 :
        svgData.svgArea.height;

      svgData.svg.selectAll('*').remove();
      svg = svgData.svg.attr('viewBox',
        [0, 0, svgData.svgArea.width, svgData.svgArea.height]);
      bar = svg.append('g');
      barXAxis = svg.append('g').attr('class', 'xaxis');
      barYAxis = svg.append('g').attr('class', 'yaxis');
    }

    const data = svgData.data;
    const y = genY(null, svgData.svgArea, d3.range(data.length), d3.scaleBand().padding(0.3), false);

    if (mouseEventInfo === null) {
      mouseEventInfo = {};
      for (let i = 0; i < data.length; i++) {
        mouseEventInfo[i] = {
          'down': {
            'x': null,
            'y': null
          },
          'move': {
            'x': null,
            'y': null
          }
        };
      }
    }

    const shortenData = data.map(text => text.length > 20 ? text.substring(0, 20) + '...' : text);
    barYAxis
      .call(d3.axisRight(y).tickFormat(i => `${shortenData[i]}`).tickSize(0))
      .call(barYAxis => barYAxis.select('.domain').remove());
    // .call(barYAxis => barYAxis.selectAll('.tick text').call(wrap))

    barYAxis.selectAll('text')
      .data(shortenData)
      .attr('feat-id', (d, i) => i)
      .on('mouseover',
        function(event, d) {
          const i = d3.select(this).attr('feat-id');
          // TODO: move this in a separate file
          embChart(allSvgData, wsInfo, true, i);
        })
      .on("mouseout", () => {
        embChart(allSvgData, wsInfo, true, -1);
      });

    return svg.node();
  };

  return chart;
};