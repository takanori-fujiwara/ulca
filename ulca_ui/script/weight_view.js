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

export const genChart = (weightType, xDomainMaxLimit = 1) => {
  let svg = null;
  let bar = null;
  let barXAxis = null;
  let barYAxis = null;
  let barRangeSelector = null;
  let barPointSelector = null;
  let mouseEventInfo = null;

  const chart = (allSvgData, wsInfo = null, init = true) => {
    const svgData = allSvgData[weightType];

    if (init) {
      svgData.svg.selectAll('*').remove();
      svg = svgData.svg.attr('viewBox',
        [0, 0, svgData.svgArea.width, svgData.svgArea.height]);
      bar = svg.append('g');
      barXAxis = svg.append('g').attr('class', 'xaxis');
      barYAxis = svg.append('g').attr('class', 'yaxis');
      barPointSelector = svg.append('g');
      barRangeSelector = svg.append('g');

      svg.append('text')
        .attr('class', 'subtitle')
        .attr('x', -53)
        .attr('y', -8)
        .attr('font-size', 12)
        .text(svgData.subtitle);
    }

    const data = svgData.data;
    const maxVal = data.reduce((acc, d) => acc > d.val ? acc : d.val, -Number.MAX_VALUE);
    const xDomain = [0, Math.max(xDomainMaxLimit, maxVal)];
    const x = genX(null, svgData.svgArea, xDomain);
    const y = genY(null, svgData.svgArea, d3.range(data.length), d3.scaleBand().padding(0.3), false);
    const invX = genInvX(null, svgData.svgArea, xDomain);

    if (mouseEventInfo === null) {
      mouseEventInfo = {};
      for (const d of data) {
        mouseEventInfo[d.label] = {
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

    barXAxis
      .attr("transform", `translate(0, ${svgData.svgArea.height})`)
      .transition().duration(init ? 0 : 750)
      .call(d3.axisBottom(x).ticks(3).tickSizeOuter(0).tickFormat(d3.format(".1f")));
    // barXAxis.transition().duration(750);

    barYAxis.transition().duration(init ? 0 : 750)
      .call(d3.axisLeft(y)
        .tickFormat(i => allSvgData.labelToName.data[data[i].label])
        .tickSizeOuter(0));

    const maxBarHeight = 20;
    bar.selectAll('rect')
      .data(data)
      .join(
        enter => enter.append('rect')
        .attr('x', d => x(0))
        .attr('y', (d, i) =>
          y(i) + (y.bandwidth() - Math.min(maxBarHeight, y.bandwidth())) / 2)
        .attr('height', d => Math.min(maxBarHeight, y.bandwidth()))
        .attr('width', d => Math.max(0, x(d.val)))
        .attr('stroke', '#444444')
        .attr('stroke-width', 0.5)
        .attr('stroke-opacity', 1.0)
        .attr('fill', d =>
          percentColToD3Rgb(pallette[d.label] || [0.2, 0.2, 0.2]))
        .call(enter => enter
          .transition(svg.transition().duration(750))),
        update => update
        .call(update => update
          .transition(svg.transition().duration(750))
          .attr('x', d => x(0))
          .attr('y', (d, i) =>
            y(i) + (y.bandwidth() - Math.min(maxBarHeight, y.bandwidth())) / 2)
          .attr('height', d => Math.min(maxBarHeight, y.bandwidth()))
          .attr('width', d => {
            return Math.max(0, x(d.val))
          })
          .attr('fill', d =>
            percentColToD3Rgb(pallette[d.label] || [0.2, 0.2, 0.2]))),
        exit => exit
        .call(exit => exit
          .transition(svg.transition().duration(750))
          .remove())
      );

    // allows selection of weights by clicking
    barPointSelector.selectAll('rect')
      .data(data)
      .join(
        enter => enter.append('rect')
        .attr('x', d => x(0))
        .attr('y', (d, i) =>
          y(i) + (y.bandwidth() - Math.min(maxBarHeight, y.bandwidth())) / 2)
        .attr('height', d => Math.min(maxBarHeight, y.bandwidth()))
        .attr('width', svgData.svgArea.width)
        .attr('fill', '#ffffff')
        .attr('opacity', 0.0)
        .attr('cursor', 'pointer')
        .call(d3.drag()
          .on('start', (event, d) => {
            mouseEventInfo[d.label].down.x = event.x;
            mouseEventInfo[d.label].down.y = event.y;
            mouseEventInfo[d.label].move.x = event.x;
            mouseEventInfo[d.label].move.y = event.y;
          })
          .on('drag', (event, d) => {
            mouseEventInfo[d.label].move.x = event.x;
            mouseEventInfo[d.label].move.y = event.y;
          })
          .on('end', (event, d) => {
            mouseEventInfo[d.label].move.x = event.x;
            mouseEventInfo[d.label].move.y = event.y;
          })
          .on('start.update drag.update end.update', (e, d) => changeRange(e.type)))
      );

    // allows selection of weights by using sliders
    const selectorW = 3;
    barRangeSelector.selectAll('rect')
      .data(data)
      .join(
        enter => enter.append('rect')
        .attr('x', d => Math.max(0, x(d.val)) - selectorW * 0.5)
        .attr('y', (d, i) =>
          y(i) + (y.bandwidth() - Math.min(maxBarHeight, y.bandwidth())) / 2 + 2)
        .attr('height', d => Math.min(maxBarHeight, y.bandwidth()) - 4)
        .attr('width', selectorW)
        .attr('stroke', '#444444')
        .attr('stroke-width', 1)
        .attr('stroke-opacity', 1.0)
        .attr('fill', '#ffffff')
        .attr('opacity', 1)
        .attr('cursor', 'col-resize')
        .call(d3.drag()
          .on('start', (event, d) => {
            mouseEventInfo[d.label].down.x = event.x;
            mouseEventInfo[d.label].down.y = event.y;
            mouseEventInfo[d.label].move.x = event.x;
            mouseEventInfo[d.label].move.y = event.y;
          })
          .on('drag', (event, d) => {
            mouseEventInfo[d.label].move.x = event.x;
            mouseEventInfo[d.label].move.y = event.y;
          })
          .on('end', (event, d) => {
            mouseEventInfo[d.label].move.x = event.x;
            mouseEventInfo[d.label].move.y = event.y;
          })
          .on('start.update drag.update end.update', (e, d) => changeRange(e.type)))
        .call(enter => enter
          .transition(svg.transition().duration(750))),
        update => update
        .call(update => update
          .transition(svg.transition().duration(750)).attr('x', d => x(0))
          .attr('x', d => Math.max(0, x(d.val)) - selectorW * 0.5)
          .attr('y', (d, i) =>
            y(i) + (y.bandwidth() - Math.min(maxBarHeight, y.bandwidth())) / 2 + 2)
          .attr('height', d => Math.min(maxBarHeight, y.bandwidth()) - 4)),
        exit => exit
        .call(exit => exit
          .transition(svg.transition().duration(750))
          .remove())
      );

    // mouse events
    const changeRange = (eventType) => {
      for (const d of data) {
        if (mouseEventInfo[d.label].move.x !== null) {
          d.val = invX(Math.max(0, mouseEventInfo[d.label].move.x));
          d.val = d.val <= xDomainMaxLimit ? d.val : xDomainMaxLimit;
          // reset info to null
          mouseEventInfo[d.label].move.x = null;
        }
      }

      bar.selectAll('rect')
        .data(data)
        .attr('width', d => Math.max(0, x(d.val)));

      barRangeSelector.selectAll('rect')
        .data(data)
        .attr('x', d => Math.max(0, x(d.val)) - selectorW * 0.5);

      if (eventType === 'end') {
        requestEmbedding();
      }
    };

    const requestEmbedding = () => {
      const content = {
        'data': {
          'weights': {},
          'bounds': allSvgData.ratioBoundary.data,
          'emb': allSvgData.emb.data
        }
      };

      for (const key of Object.keys(allSvgData)) {
        const svgData = allSvgData[key];
        const contentType = svgData.contentType;
        if (contentType === 'w_tg' || contentType === 'w_bg' || contentType === 'w_bw') {
          // 'w_tg' => need to be 'tg'
          const wType = contentType.split('_')[1]
          content.data.weights[wType] = [];
          const data = svgData.data;
          for (const d of data) {
            content.data.weights[wType].push({
              'label': d.label,
              'val': d.val
            });
          }
        }
      }

      if (wsInfo !== null) {
        wsInfo.ws.send(JSON.stringify({
          action: wsInfo.messageActions.updateEmb,
          content: content
        }));
      }
    };

    return svg.node();
  };

  return chart;
};