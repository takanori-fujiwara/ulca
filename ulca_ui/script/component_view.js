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

export const genChart = (compName) => {
  let svg = null;
  let bar = null;
  let barXAxis = null;
  let barYAxis = null;
  let mouseEventInfo = null;

  const chart = (allSvgData, init = true) => {
    const svgData = allSvgData[compName];

    if (init) {
      svgData.svgArea.height =
        svgData.data.length * 30 < svgData.svgArea.height ?
        svgData.data.length * 30 :
        svgData.svgArea.height;
      svgData.svg.selectAll('*').remove();
      svg = svgData.svg.attr('viewBox',
        [0, 0, svgData.svgArea.width, svgData.svgArea.height]);
      svg.append('circle')
        .attr('class', 'subtitle')
        .attr('cx', svgData.svgArea.width / 2)
        .attr('cy', -10)
        .attr('r', 8)
        .attr('fill', '#ffffff')
        .attr('stroke', '#888888')
        .attr('stroke-width', 0.5)
        .attr('stroke-opacity', 1.0);
      svg.append('text')
        .attr('class', 'subtitle')
        .attr('x', svgData.svgArea.width / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-size', 12)
        .text(svgData.subtitle)
      svg.append('rect')
        .attr('class', 'chart-outline')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', svgData.svgArea.width)
        .attr('height', svgData.svgArea.height)
        .attr('fill', '#f3f3f3');
      bar = svg.append('g');
      barXAxis = svg.append('g').attr('class', 'xaxis');
      barYAxis = svg.append('g').attr('class', 'yaxis');
    }

    const data = svgData.data;
    const xDomain = [-1, 1];
    const x = genX(null, svgData.svgArea, xDomain);
    const y = genY(null, svgData.svgArea, d3.range(data.length), d3.scaleBand().padding(0.3), false);
    const invX = genInvX(null, svgData.svgArea, xDomain);

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

    barXAxis
      .attr('transform', `translate(0, ${svgData.svgArea.height})`)
      .call(d3.axisBottom(x).ticks(2).tickSize(0).tickFormat(d3.format(".0f")))
      .call(barXAxis => barXAxis.select('.domain').remove())
      .call(barXAxis => barXAxis.selectAll('.tick text')
        .attr('font-size', 8));
    barYAxis
      .attr('transform', `translate(${svgData.svgArea.width / 2}, 0)`)
      .call(d3.axisRight(y).tickSize(0).tickFormat(''))
      .call(barYAxis => barYAxis.select('.domain')
        .attr('stroke', '#cccccc')
        .attr('stroke-width', 1.0));

    const maxBarHeight = 20;
    bar.selectAll('rect')
      .data(data)
      .join(
        enter => enter.append('rect')
        .attr('x', d => Math.min(x(0), x(d)))
        .attr('y', (d, i) =>
          y(i) + (y.bandwidth() - Math.min(maxBarHeight, y.bandwidth())) / 2)
        .attr('height', d => Math.min(maxBarHeight, y.bandwidth()))
        .attr('width', d => Math.abs(x(d) - x(0)))
        .attr('fill', '#666666')
        .call(enter => enter
          .transition(svg.transition().duration(750))),
        update => update
        .call(update => update
          .transition(svg.transition().duration(750))
          .attr('x', d => Math.min(x(0), x(d)))
          .attr('y', (d, i) =>
            y(i) + (y.bandwidth() - Math.min(maxBarHeight, y.bandwidth())) / 2)
          .attr('height', d => Math.min(maxBarHeight, y.bandwidth()))
          .attr('width', d => {
            return Math.abs(x(d) - x(0))
          })
          .attr('fill', '#666666')),
        exit => exit
        .call(exit => exit
          .transition(svg.transition().duration(750))
          .remove())
      );

    return svg.node();
  };

  return chart;
};