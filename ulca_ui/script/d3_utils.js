import {
  colormap,
  percentColToD3Rgb
} from './colors.js';

const calcContainerWidth = name => +d3.select(name).style('width').slice(0, -2)
const calcContainerHeight = name => +d3.select(name).style('height').slice(0, -2)
const calcCellWidth = (width, colNames) => width / colNames.length;
const calcCellHeight = (height, rowNames) => height / rowNames.length;
const calcCellSize = (width, height, colNames, rowNames, widthMax, heightMax) => [Math.min(calcCellWidth(width, colNames), widthMax), Math.min(calcCellHeight(height, rowNames), heightMax)];

const prepareSvgArea = (windowWidth, windowHeight, margin) => {
  return {
    width: windowWidth - margin.left - margin.right,
    height: windowHeight - margin.top - margin.bottom,
    margin: margin
  }
}

const prepareSvg = (id, svgArea) => {
  d3.select(id).selectAll('*').remove();
  const svg = d3.select(id)
    .append('svg')
    .attr('width', svgArea.width + svgArea.margin.left + svgArea.margin.right)
    .attr('height', svgArea.height + svgArea.margin.top + svgArea.margin.bottom)
    .append('g')
    .attr('transform',
      'translate(' + svgArea.margin.left + ',' + svgArea.margin.top + ')');

  return svg;
}

export const initSvgInfo = (targetView, margin) => {
  const sd = targetView.svgData;
  const domId = targetView.domId;

  sd.svgArea = prepareSvgArea(
    calcContainerWidth(`#${domId}`),
    calcContainerHeight(`#${domId}`), margin || {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    })
  sd.svg = prepareSvg(`#${domId}`, sd.svgArea);
  sd.domId = targetView.domId;
};

// axes, scaling
export const genX = (data, svgArea, domain = null, scaler = d3.scaleLinear()) => {
  if (domain === null) {
    domain = d3.extent(data);
  }
  return scaler.domain(domain).range([0, svgArea.width]);
};

export const genInvX = (data, svgArea, domain = null, scaler = d3.scaleLinear()) => {
  if (domain === null) {
    domain = d3.extent(data);
  }
  return scaler.domain([0, svgArea.width]).range(domain);
};

export const genY = (data, svgArea, domain = null, scaler = d3.scaleLinear(), goUp = true) => {
  if (domain === null) {
    domain = d3.extent(data);
  }
  return goUp ?
    scaler.domain(domain).range([svgArea.height, 0]) :
    scaler.domain(domain).range([0, svgArea.height]);
};

export const genInvY = (data, svgArea, domain = null, scaler = d3.scaleLinear()) => {
  if (domain === null) {
    domain = d3.extent(data);
  }
  return scaler.domain([svgArea.height, 0]).range(domain);
};

// for legend
export const setCategoryLegend = (svgId, legends, shape) => {
  d3.select(svgId).selectAll('*').remove();

  if (!shape) {
    shape = '*';
  }
  const legendArea = d3.select(svgId).append('g');
  const areaHeight = calcContainerHeight(svgId);
  const nLegends = legends.length;
  for (const [i, legend] of legends.entries()) {
    if (shape === "*") {
      legendArea.append('circle')
        .attr('r', 5)
        .attr('cx', 8)
        .attr('cy', 10 + 15 * i)
        .style('fill', legend.fill);
    } else if (shape === "-") {
      legendArea.append('rect')
        .attr('width', 10)
        .attr('height', 2)
        .attr('x', 4)
        .attr('y', 10 + 15 * i)
        .style('fill', legend.fill);
    }
    legendArea.append('text')
      .attr('x', 16)
      .attr('y', 10 + 15 * i)
      .text(legend.text)
      .attr('dominant-baseline', 'central')
      .style('font-size', 10)
      .style('fill', '#444444');
  }
}

export const setColormapLegend = (svgId, colormapInfo, legendsInfo) => {
  d3.select(svgId).selectAll('*').remove();

  const svgW = calcContainerWidth(svgId);
  const svgH = calcContainerHeight(svgId);

  const colors = colormap[colormapInfo.key];
  const colormapH = 10;
  const colormapW = 100;
  const unitW = colormapW / colors.length;

  const legendArea = d3.select(svgId).append('g');
  legendArea
    .append('rect')
    .attr('x', 2)
    .attr('y', 3)
    .attr('width', svgW - 1)
    .attr('height', svgH - 5)
    .attr('stroke-width', 1)
    .attr('fill', '#555555')
    .attr('opacity', 0.1);

  legendArea.selectAll('rect')
    .data(colors)
    .enter()
    .append('rect')
    .attr('x', (d, idx) => {
      return 10 + idx * unitW
    })
    .attr('y', svgH - 25)
    .attr('width', unitW)
    .attr('height', colormapH)
    .attr('stroke-width', 1)
    .attr('stroke', d => percentColToD3Rgb(d))
    .attr('fill', d => percentColToD3Rgb(d));
  legendArea.append('text')
    .attr('x', 10 + colormapW / 2)
    .attr('y', svgH - 27)
    .attr('text-anchor', 'middle')
    .style('fill', '#444444')
    .style('font-size', 10)
    .text(colormapInfo.title);
  legendArea.append('text')
    .attr('x', 10)
    .attr('y', svgH - 5)
    .attr('text-anchor', 'middle')
    .style('fill', '#444444')
    .style('font-size', 10)
    .text('min');
  legendArea.append('text')
    .attr('x', colormapW)
    .attr('y', svgH - 5)
    .attr('text-anchor', 'left')
    .style('fill', '#444444')
    .style('font-size', 10)
    .text('max');

  const nLegends = legendsInfo.length;
  for (const [i, legend] of legendsInfo.entries()) {
    legendArea.append('circle')
      .attr('class', legend.classname)
      .attr('r', legend.size)
      .attr('cx', 13)
      .attr('cy', 35 - 9 - 15 * (nLegends - 1 - i) + legend.size / 2)
      .style('fill', legend.fill)
      .style('stroke', legend.stroke);
    legendArea.append('text')
      .attr('class', legend.classname)
      .attr('x', 21)
      .attr('y', 35 - 7 - 15 * (nLegends - 1 - i) + legend.size / 2)
      .text(legend.text)
      .style('font-size', 10)
      .style('fill', '#444444');
  }
}

export const setAxisLegend = (svgId, xlabel, ylabel) => {
  d3.select(svgId).selectAll('*').remove();

  const svgW = calcContainerWidth(svgId);
  const svgH = calcContainerHeight(svgId);

  const legendArea = d3.select(svgId).append('g');

  legendArea.append('svg:defs').append('svg:marker')
    .attr('id', 'arrowhead')
    .attr('markerHeight', 5)
    .attr('markerWidth', 5)
    .attr('markerUnits', 'strokeWidth')
    .attr('orient', 'auto')
    .attr('refX', 0)
    .attr('refY', 0)
    .attr('viewBox', '-5 -5 10 10')
    .append('svg:path')
    .attr('d', 'M 0,0 m -5,-5 L 5,0 L -5,5 Z')
    .attr('fill', '#666666');
  legendArea.append('circle')
    .attr('cx', svgW / 2 + 3)
    .attr('cy', svgH - 6)
    .attr('r', 6)
    .attr('fill', '#ffffff')
    .attr('stroke', '#888888')
    .attr('stroke-width', 0.5)
    .attr('stroke-opacity', 1.0);
  legendArea.append('text')
    .attr('x', svgW / 2 + 3)
    .attr('y', svgH - 6)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'central')
    .style('font-size', 10)
    .text(xlabel);
  legendArea.append('circle')
    .attr('transform', 'rotate(-90)')
    .attr('cx', -svgW / 2 + 3)
    .attr('cy', 6)
    .attr('r', 6)
    .attr('fill', '#ffffff')
    .attr('stroke', '#888888')
    .attr('stroke-width', 0.5)
    .attr('stroke-opacity', 1.0);
  legendArea.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -svgW / 2 + 3)
    .attr('y', 5)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'central')
    .style('font-size', 10)
    .text(ylabel);
  legendArea.append('line')
    .attr('x1', 13)
    .attr('y1', svgH - 13)
    .attr('x2', svgW - 5)
    .attr('y2', svgH - 13)
    .attr('stroke-width', 1)
    .attr('stroke', '#666666')
    .attr("marker-end", "url(#arrowhead)");
  legendArea.append('line')
    .attr('x1', 13)
    .attr('y1', svgH - 13)
    .attr('x2', 13)
    .attr('y2', 5)
    .attr('stroke-width', 1)
    .attr('stroke', '#666666')
    .attr("marker-end", "url(#arrowhead)");
}

export const setTitle = (svgId, title) => {
  d3.select(svgId).selectAll('*').remove();

  const svgW = calcContainerWidth(svgId);
  const svgH = calcContainerHeight(svgId);

  const titleArea = d3.select(svgId).append('g');
  titleArea
    .append('text')
    .attr('x', svgW / 2)
    .attr('y', svgH - 2)
    .attr('text-anchor', 'middle')
    .style('fill', '#444444')
    .style('font-size', 10)
    .text(title);
}