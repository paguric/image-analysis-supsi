export async function loadDifferentialImage({
    currentFrame,
    isLoadingFunction,
    differentialFrameGetter,
    oldDiffUrl,
    setDifferentialUrl,
    showContours,
    showContoursToggleFunction,
}) {
    isLoadingFunction(true);

    try {
        const url = await differentialFrameGetter(currentFrame);
        if (oldDiffUrl.current)
            URL.revokeObjectURL(oldDiffUrl.current);
        oldDiffUrl.current = url;
        setDifferentialUrl(url);
        showContoursToggleFunction(showContours);
    } finally {
        isLoadingFunction(false);
    }
}