import {
  pallette,
  percentColToD3Rgb
} from './colors.js';

import {
  genX,
  genY,
  genInvX,
  genInvY,
  setCategoryLegend,
  setAxisLegend,
  initSvgInfo
} from './d3_utils.js';

import {
  svgDataTemplate
} from './model.js';

import * as cv from './component_view.js';

const compBasicStats = (data, uniqLabels) => {
  const stats = {};
  for (const l of uniqLabels) {
    stats[l] = {
      'n': 0,
      'sumX': 0,
      'sumY': 0,
      'meanX': 0,
      'meanY': 0,
      'varX': 0,
      'varY': 0,
      'varXY': 0,
      'sdX': 0,
      'sdY': 0
    };
  }
  for (const d of data) {
    stats[d.label].n += 1;
    stats[d.label].sumX += d.x;
    stats[d.label].sumY += d.y;
  }

  for (const l of uniqLabels) {
    stats[l].meanX = stats[l].sumX / stats[l].n;
    stats[l].meanY = stats[l].sumY / stats[l].n;
  }

  for (const d of data) {
    const diffX = d.x - stats[d.label].meanX;
    const diffY = d.y - stats[d.label].meanY;
    stats[d.label].varX += diffX * diffX;
    stats[d.label].varY += diffY * diffY;
    stats[d.label].varXY += diffX * diffY;
  }

  for (const l of uniqLabels) {
    stats[l].varX /= stats[l].n;
    stats[l].varY /= stats[l].n;
    stats[l].varXY /= stats[l].n;
    stats[l].sdX = Math.sqrt(Math.max(0, stats[l].varX));
    stats[l].sdY = Math.sqrt(Math.max(0, stats[l].varY));
  }

  return stats;
};

const compConfAreaInfo = (stat, confIntPer = 50) => {
  // Ref: https://www.xarg.org/2018/04/how-to-plot-a-covariance-error-ellipse/

  // 2 degrees of freedom chi square values
  const chiSq = -2 * Math.log(1 - confIntPer / 100);

  return {
    'meanX': stat.meanX,
    'meanY': stat.meanY,
    'confX': Math.sqrt(chiSq) * stat.sdX,
    'confY': Math.sqrt(chiSq) * stat.sdY,
    'slope': Math.sqrt((stat.varX - stat.varY) ** 2 + 4 * stat.varXY ** 2) / stat.varXY
  };
};


const genComputeNewComponent = (invX, invY, compX, compY) => {
  const computeNewComponent = (x1, y1, x2, y2) => {
    const x1_ = invX(x1);
    const y1_ = invY(y1);
    const x2_ = invX(x2);
    const y2_ = invY(y2);
    const vecX = x2_ - x1_;
    const vecY = y2_ - y1_;
    const mag = Math.sqrt(vecX * vecX + vecY * vecY);

    return compX.map((compXi, i) =>
      mag == 0 ? 0 : (vecX * compXi + vecY * compY[i]) / mag);
  };
  return computeNewComponent;
}

const genDrawNewComp = (compDrawAreaSvg, computeNewComponent, allSvgData, wsInfo) => {
  const eventInfo = {
    'nNewComps': 0,
    'mouseDownPos': {
      x: null,
      y: null
    },
    'newComps': []
  };

  compDrawAreaSvg.append('svg:marker')
    .attr('id', d => 'marker_arrow')
    .attr('markerHeight', 10)
    .attr('markerWidth', 10)
    .attr('markerUnits', 'strokeWidth')
    .attr('orient', 'auto')
    .attr('refX', 0)
    .attr('refY', 0)
    .attr('viewBox', '-5 -5 10 10')
    .append('svg:path')
    .attr('d', 'M 0,0 m -5,-5 L 5,0 L -5,5 Z')
    .style('fill', '#888888');

  const drawNewComp = () => {
    compDrawAreaSvg
      .call(d3.drag()
        .on('start', (event, d) => {
          eventInfo.newComps.push({
            'labelCircle': null,
            'labelText': null,
            'line': null,
            'startSelection': null,
            'endSelection': null,
            'removed': false
          });
          const nNewComps = eventInfo.newComps.length;

          eventInfo.mouseDownPos.x = event.x;
          eventInfo.mouseDownPos.y = event.y;

          eventInfo.newComps[nNewComps - 1].line =
            compDrawAreaSvg.append('line')
            .style('stroke', '#888888');
          eventInfo.newComps[nNewComps - 1].endSelection =
            compDrawAreaSvg.append('circle')
            .attr('r', 8)
            .attr('fill', '#ffffff')
            .attr('opacity', 0);

          eventInfo.newComps[nNewComps - 1].labelCircle =
            compDrawAreaSvg.append('circle')
            .attr('cx', event.x)
            .attr('cy', event.y)
            .attr('r', 8)
            .attr('fill', '#ffffff')
            .attr('stroke', '#888888')
            .attr('stroke-width', 0.5)
            .attr('stroke-opacity', 1.0);
          eventInfo.newComps[nNewComps - 1].labelText =
            compDrawAreaSvg.append('text')
            .attr('x', event.x)
            .attr('y', event.y)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'central')
            .attr('font-size', 12)
            .text(nNewComps);
          eventInfo.newComps[nNewComps - 1].startSelection =
            compDrawAreaSvg.append('circle')
            .attr('cx', event.x)
            .attr('cy', event.y)
            .attr('r', 8)
            .attr('fill', '#ffffff')
            .attr('opacity', 0)
        })
        .on('drag', (event, d) => {
          const nNewComps = eventInfo.newComps.length;
          eventInfo.newComps[nNewComps - 1].line
            .attr('x1', eventInfo.mouseDownPos.x)
            .attr('y1', eventInfo.mouseDownPos.y)
            .attr('x2', event.x - 5)
            .attr('y2', event.y - 5)
            .attr('marker-end', 'url(#marker_arrow)');
        })
        .on('end', (event, d) => {

        })
        .on('end.update', event => {
          const nNewComps = eventInfo.newComps.length;

          eventInfo.newComps[nNewComps - 1].endSelection
            .attr('cx', event.x - 5)
            .attr('cy', event.y - 5)

          // TODO: this part should be handled in main or update
          const newCompVec = computeNewComponent(
            eventInfo.newComps[nNewComps - 1].startSelection.attr('cx'),
            eventInfo.newComps[nNewComps - 1].startSelection.attr('cy'),
            eventInfo.newComps[nNewComps - 1].endSelection.attr('cx'),
            eventInfo.newComps[nNewComps - 1].endSelection.attr('cy'));
          if (wsInfo !== null) {
            wsInfo.ws.send(JSON.stringify({
              action: wsInfo.messageActions.addNewComp,
              content: {
                'key': nNewComps,
                'component': newCompVec
              }
            }));
          }

          const updateAllCompViews = () => {
            const compsArea = d3.select('#comps').node().getBoundingClientRect();

            for (let i = 0; i < nNewComps; i++) {
              if (eventInfo.newComps[i].removed) {
                d3.select(`#comp_${i + 1}_svg`).remove();
              }
            }
            d3.select(`#comp_${nNewComps}_svg`).remove();
            d3.select('#comps').insert('div')
              .attr('id', `comp_${nNewComps}_svg`)
              .attr('class', 'comp');

            const nRemovedComps = eventInfo.newComps.reduce((acc, elm) => elm.removed ? acc + 1 : acc, 0);

            d3.selectAll('.comp').style('width', `${compsArea.width / (nNewComps - nRemovedComps + 2)}px`);

            allSvgData[`comp${nNewComps}`] = svgDataTemplate();
            allSvgData[`comp${nNewComps}`].subtitle = `${nNewComps}`;
            allSvgData[`comp${nNewComps}`].contentType = `comp${nNewComps}`;
            allSvgData[`comp${nNewComps}`].data = newCompVec;

            initSvgInfo({
              'svgData': allSvgData.compX,
              'domId': `comp_x_svg`
            }, {
              top: 25,
              right: 2,
              bottom: 40,
              left: 10
            });

            initSvgInfo({
              'svgData': allSvgData.compY,
              'domId': `comp_y_svg`
            }, {
              top: 25,
              right: 2,
              bottom: 40,
              left: 10
            });

            for (let i = 0; i < nNewComps; i++) {
              if (!eventInfo.newComps[i].removed) {
                initSvgInfo({
                  'svgData': allSvgData[`comp${i + 1}`],
                  'domId': `comp_${i + 1}_svg`
                }, {
                  top: 25,
                  right: 2,
                  bottom: 40,
                  left: 10
                })
              }
            };

            cv.genChart(`compX`)(allSvgData);
            cv.genChart(`compY`)(allSvgData);
            for (let i = 0; i < nNewComps; i++) {
              if (!eventInfo.newComps[i].removed) {
                cv.genChart(`comp${i + 1}`)(allSvgData);
              }
            }
          };

          updateAllCompViews();
          //////

          for (let i = 0; i < eventInfo.newComps.length; i++) {
            eventInfo.newComps[i].startSelection
              .attr('cursor', 'move')
              // TODO: a way to remove comp should be more explicit
              .on('dblclick', event => {
                eventInfo.newComps[i].labelCircle.remove();
                eventInfo.newComps[i].labelText.remove();
                eventInfo.newComps[i].startSelection.remove();
                eventInfo.newComps[i].line.remove();
                eventInfo.newComps[i].removed = true;
                updateAllCompViews();
              })
              .call(d3.drag()
                .on('start.update drag.update end.update', event => {
                  eventInfo.newComps[i].labelCircle
                    .attr('cx', event.x)
                    .attr('cy', event.y);
                  eventInfo.newComps[i].labelText
                    .attr('x', event.x)
                    .attr('y', event.y);
                  eventInfo.newComps[i].startSelection
                    .attr('cx', event.x)
                    .attr('cy', event.y);
                  eventInfo.newComps[i].line
                    .attr('x1', event.x)
                    .attr('y1', event.y);
                }));
            eventInfo.newComps[i].endSelection
              .attr('cursor', 'move')
              .call(d3.drag()
                .on('start.update drag.update end.update', event => {
                  eventInfo.newComps[i].endSelection
                    .attr('cx', event.x)
                    .attr('cy', event.y);
                  eventInfo.newComps[i].line
                    .attr('x2', event.x)
                    .attr('y2', event.y);
                }));
          }
        }));
  }
  return drawNewComp;
}

const genFeatValToSize = (data, featIdx = -1, minSize = 2, maxSize = 6) => {
  let featValToSize = (val) => (minSize + maxSize) * 0.5;
  if (featIdx >= 0) {
    const maxVal = data.reduce((acc, d) =>
      acc > d.feat_vals[featIdx] ? acc : d.feat_vals[featIdx], -Number.MAX_VALUE);
    const minVal = data.reduce((acc, d) =>
      acc < d.feat_vals[featIdx] ? acc : d.feat_vals[featIdx], Number.MAX_VALUE);
    if (maxVal - minVal > 0) {
      featValToSize = (val) =>
        minSize + (maxSize - minSize) * (val - minVal) / (maxVal - minVal);
    }
  }
  return featValToSize;
};

export const genChart = () => {
  let svg = null;
  let compDrawAreaSvg = null;
  let dot = null;
  let confAreaVis = null;
  let confAreaOut = null;
  let confAreaMiddle = null;
  let confAreaIn = null;
  let infoEllipses = null;

  const chart = (allSvgData, wsInfo = null, init = true, featIdx = -1) => {
    const svgData = allSvgData.emb;

    if (init) {
      svgData.svg.selectAll('*').remove();
      svg = svgData.svg.attr('viewBox',
        [0, 0, svgData.svgArea.width, svgData.svgArea.height]);
      compDrawAreaSvg = svg.append('g');
      confAreaVis = svg.append('g');
      confAreaOut = svg.append('g');
      confAreaMiddle = svg.append('g');
      confAreaIn = svg.append('g');
      dot = svg.append('g');
    }
    if (compDrawAreaSvg) {
      compDrawAreaSvg.selectAll('*').remove();
    }
    infoEllipses = null; ////

    const data = svgData.data;

    const xMin = data.reduce((acc, d) => acc < d.x ? acc : d.x, Number.MAX_VALUE);
    const xMax = data.reduce((acc, d) => acc > d.x ? acc : d.x, -Number.MAX_VALUE);
    const yMin = data.reduce((acc, d) => acc < d.y ? acc : d.y, Number.MAX_VALUE);
    const yMax = data.reduce((acc, d) => acc > d.y ? acc : d.y, -Number.MAX_VALUE);
    const range = Math.max(xMax - xMin, yMax - yMin);
    const xDomain = [(xMax + xMin - range) / 2, (xMax + xMin + range) / 2];
    const yDomain = [(yMax + yMin - range) / 2, (yMax + yMin + range) / 2];
    const x = genX(null, svgData.svgArea, xDomain);
    const y = genY(null, svgData.svgArea, yDomain);
    const invX = genInvX(null, svgData.svgArea, xDomain);
    const invY = genInvY(null, svgData.svgArea, yDomain);

    // const x = genX(data.map(d => d.x), svgData.svgArea);
    // const y = genY(data.map(d => d.y), svgData.svgArea);
    // const invX = genInvX(data.map(d => d.x), svgData.svgArea);
    // const invY = genInvY(data.map(d => d.y), svgData.svgArea);

    // area for adding new n_components
    compDrawAreaSvg.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', svgData.svgArea.width)
      .attr('height', svgData.svgArea.height)
      .attr('fill', 'white')
      .attr('opacity', 0);

    const computeNewComponent = genComputeNewComponent(
      invX, invY, allSvgData.compX.data, allSvgData.compY.data);
    const drawNewComp = genDrawNewComp(
      compDrawAreaSvg, computeNewComponent, allSvgData, wsInfo);
    compDrawAreaSvg.call(drawNewComp);

    const featValToSize = genFeatValToSize(data, featIdx);

    // draw scatterplot
    dot.selectAll('circle')
      .data(data)
      .join(
        enter => enter.append('circle')
        .attr('dot-id', (d, i) => i)
        .attr('r', (d) => featValToSize(featIdx >= 0 ? d.feat_vals[featIdx] : 0))
        .attr('stroke', '#444444')
        .attr('stroke-width', 0.5)
        .attr('stroke-opacity', 1.0)
        .attr('cx', d => x(d.x))
        .attr('cy', d => y(d.y))
        .attr('fill', d =>
          percentColToD3Rgb(pallette[d.label]))
        .call(enter => enter
          .transition(svg.transition().duration(750)))
        .on('mouseover', function(event, d) {
          const i = d3.select(this).attr('dot-id');
          svg.append('text')
            .attr('id', 'popup')
            .attr('x', x(d.x) - 10)
            .attr('y', y(d.y) - 5)
            .text(`id: ${i}, (x, y) = (${d.x.toFixed(2)}, ${d.y.toFixed(2)})`);
        })
        .on('mouseout', () => svg.select('#popup').remove()),
        update => update
        .call(update => update
          .transition(svg.transition().duration(750))
          .attr('cx', d => x(d.x))
          .attr('cy', d => y(d.y))
          .attr('fill', d =>
            percentColToD3Rgb(pallette[d.label]))),
        exit => exit
        .call(exit => exit
          .transition(svg.transition().duration(750))
          .remove())
      );

    // prepare confidence interval info
    const uniqLabels = [...data.reduce((acc, d) => acc.add(d.label), new Set())];

    const stats = compBasicStats(data, uniqLabels);
    const infoConfAreas = uniqLabels.map(l => compConfAreaInfo(stats[l]));

    if (!infoEllipses) {
      infoEllipses = uniqLabels.map((l, i) => {
        return {
          'label': l,
          'cx': x(infoConfAreas[i].meanX),
          'cy': y(infoConfAreas[i].meanY),
          'rx': x(infoConfAreas[i].confX) - x(0),
          'ry': y(0) - y(infoConfAreas[i].confY),
          'fill': percentColToD3Rgb(pallette[l]),
          'slope': infoConfAreas[i].slope,
          'mouse': {
            'down': {
              'x': null,
              'y': null
            },
            'move': {
              'x': null,
              'y': null
            }
          }
        };
      });
    }

    const confAreas = [{
      'obj': confAreaVis, // vis
      'sizeScale': 1,
      'sizeDiff': 0,
      'fillOpacity': 0.2,
      'cursor': 'default',
      'call': () => {}
    }, {
      'obj': confAreaOut, // outline area for scaling
      'sizeScale': 1,
      'sizeDiff': 3,
      'fillOpacity': 0.0,
      'cursor': 'grab',
      'call': d3.drag()
        .on('start', (event, d) => {
          d.mouse.down.x = event.x;
          d.mouse.down.y = event.y;
          d.mouse.move.x = event.x;
          d.mouse.move.y = event.y;
        })
        .on('drag', function(event, d) {
          d.mouse.move.x = event.x;
          d.mouse.move.y = event.y;
          d3.select(this).attr('cursor', 'grabbing');
        })
        .on('end', function(event, d) {
          d.mouse.move.x = event.x;
          d.mouse.move.y = event.y;
          d3.select(this).attr('cursor', 'grab');
        })
        .on('start.update drag.update end.update', (event, d) => scaleConfArea(event.type, d.label))
    }, {
      'obj': confAreaMiddle, // no interaction area
      'sizeScale': 1,
      'sizeDiff': -3,
      'fillOpacity': 0.0,
      'cursor': 'default',
      'call': () => {}
    }, {
      'obj': confAreaIn, // center area for panning
      'sizeScale': 0.3,
      'sizeDiff': 0,
      'fillOpacity': 0.0,
      'cursor': 'move',
      'call': d3.drag()
        .on('start', (event, d) => {})
        .on('drag', (event, d) => (d.cx = event.x, d.cy = event.y))
        .on('end', (event, d) => {})
        .on('start.update drag.update end.update', (event, d) => moveConfArea(event.type, d.label))
    }]

    // draw confidence intervals
    for (const ci of confAreas) {
      ci.obj.selectAll('ellipse')
        .data(infoEllipses)
        .join(
          enter => enter.append('ellipse')
          .attr('class', d => `conf-interv${d.label}`)
          .attr('cx', d => d.cx)
          .attr('cy', d => d.cy)
          .attr('rx', d => Math.max(0, d.rx * ci.sizeScale + ci.sizeDiff))
          .attr('ry', d => Math.max(0, d.ry * ci.sizeScale + ci.sizeDiff))
          .attr('fill', d => d.fill)
          .attr('fill-opacity', ci.fillOpacity)
          .attr('transform', d => {
            const angle = 90 - Math.atan2(d.slope, 1) * (180 / Math.PI);
            return `rotate(${angle > 90 ? angle - 180 : angle}, ${d.cx}, ${d.cy})`;
          })
          .attr('cursor', ci.cursor)
          .call(ci.call)
          .call(enter => enter
            .transition(svg.transition().duration(750))),
          update => update
          .call(update => update
            .transition(svg.transition().duration(750))
            .attr('cx', d => d.cx)
            .attr('cy', d => d.cy)
            .attr('rx', d => Math.max(0, d.rx * ci.sizeScale + ci.sizeDiff))
            .attr('ry', d => Math.max(0, d.ry * ci.sizeScale + ci.sizeDiff))
            .attr('fill', d => d.fill)
            .attr('fill-opacity', ci.fillOpacity)
            .attr('transform', d => {
              const angle = 90 - Math.atan2(d.slope, 1) * (180 / Math.PI);
              return `rotate(${angle > 90 ? angle - 180 : angle}, ${d.cx}, ${d.cy})`;
            })),
          exit => exit
          .call(exit => exit
            .transition(svg.transition().duration(750))
            .remove())
        );
    }

    // draw legends
    const legends = uniqLabels.map(label => {
      return {
        'text': allSvgData.labelToName.data[label],
        'fill': percentColToD3Rgb(pallette[label])
      }
    });
    setCategoryLegend('#emb_view_legend', legends, '*');
    setAxisLegend('#emb_view_axis_legend', 'x', 'y');

    // mouse events
    const moveConfArea = (eventType, updatedLabel) => {
      for (const ci of confAreas) {
        ci.obj.selectAll('ellipse')
          .data(infoEllipses)
          .attr('cx', d => d.cx)
          .attr('cy', d => d.cy)
          .attr('transform', d => {
            const angle = 90 - Math.atan2(d.slope, 1) * (180 / Math.PI);
            return `rotate(${angle > 90 ? angle - 180 : angle}, ${d.cx}, ${d.cy})`;
          });
      }
      if (eventType === 'end') {
        requestOptimization('move', updatedLabel);
      }
    };

    const scaleConfArea = (eventType, updatedLabel) => {
      for (const ci of confAreas) {
        ci.obj.selectAll('ellipse')
          .data(infoEllipses)
          .attr('rx', d => {
            const scale = !(d.mouse.move.x && d.mouse.move.y) ? 1.0 :
              Math.sqrt((d.mouse.move.x - d.cx) ** 2 + (d.mouse.move.y - d.cy) ** 2) /
              Math.sqrt((d.mouse.down.x - d.cx) ** 2 + (d.mouse.down.y - d.cy) ** 2);
            return d.rx * scale * ci.sizeScale + ci.sizeDiff;
          })
          .attr('ry', d => {
            const scale = !(d.mouse.move.x && d.mouse.move.y) ? 1.0 :
              Math.sqrt((d.mouse.move.x - d.cx) ** 2 + (d.mouse.move.y - d.cy) ** 2) /
              Math.sqrt((d.mouse.down.x - d.cx) ** 2 + (d.mouse.down.y - d.cy) ** 2);
            return d.ry * scale * ci.sizeScale + ci.sizeDiff;
          });
      }

      // only when drag is ended, update d.rx and d.ry
      if (eventType == 'end') {
        for (const d of infoEllipses) {
          const scale = !(d.mouse.move.x && d.mouse.move.y) ? 1.0 :
            Math.sqrt((d.mouse.move.x - d.cx) ** 2 + (d.mouse.move.y - d.cy) ** 2) /
            Math.sqrt((d.mouse.down.x - d.cx) ** 2 + (d.mouse.down.y - d.cy) ** 2);
          d.rx *= scale;
          d.ry *= scale;
          d.mouse.move.x = null;
          d.mouse.move.y = null;
          d.mouse.down.x = null;
          d.mouse.down.y = null;
        };
        requestOptimization('scale', updatedLabel);
      }
    }

    const requestOptimization = (interactionType, updatedLabel) => {
      const content = {
        'data': {
          'emb': allSvgData.emb.data,
          'weights': {},
          'bounds': allSvgData.ratioBoundary.data,
          'interaction': interactionType,
          'updated_label': updatedLabel,
          'ellipses': []
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

      for (const info of infoEllipses) {
        content.data.ellipses.push({
          'label': info.label,
          'cx': invX(info.cx),
          'cy': invY(info.cy),
          'rx': invX(info.rx + x(0)),
          'ry': invY(y(0) - info.ry)
        });
      }

      if (wsInfo !== null) {
        wsInfo.ws.send(JSON.stringify({
          action: wsInfo.messageActions.optimizeWeights,
          content: content
        }));
      }
    };

    return svg.node();
  };

  return chart;
};