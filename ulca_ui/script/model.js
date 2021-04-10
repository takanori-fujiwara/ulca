export const svgDataTemplate = () => {
  return {
    domId: undefined,
    svg: undefined,
    svgArea: undefined,
    data: [],
    contentType: undefined,
    selectedX: undefined,
    selectedY: undefined
  }
};

export const allSvgData = {
  tgWeight: svgDataTemplate(),
  bgWeight: svgDataTemplate(),
  bwWeight: svgDataTemplate(),
  ratioBoundary: svgDataTemplate(),
  emb: svgDataTemplate(),
  compX: svgDataTemplate(),
  compY: svgDataTemplate(),
  compFeatName: svgDataTemplate(),
  labelToName: svgDataTemplate() // TODO: this doesn't need to contain svg
};

// change websocket URL based on your env
export const wsUrl = `ws://localhost:9000`;
export const wsInfo = {
  ws: undefined,
  dataKey: undefined,
  messageActions: {
    updateEmb: 0,
    optimizeWeights: 1,
    saveResult: 2,
    loadResult: 3,
    initialLoad: 4,
    addNewComp: 5
  }
};