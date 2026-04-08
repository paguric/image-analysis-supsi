export function computeWaveLength(startingWL, finalWL, currentFrame, frameCount) {
    
    let start = Number(startingWL);
    let end = Number(finalWL);
    let current = Number(currentFrame);
    let total = Number(frameCount);


    return start +
        (current - 1) *
        ((end - start) / (total - 1));
}