export async function imageLoader({ setImageLoadingState, 
                                    setError, 
                                    setImageUrl, 
                                    imageGetter, 
                                    roiNumber, 
                                    frameNumber }) {

    setImageLoadingState(true);
    setError(false);

    try {

        const url = await imageGetter(roiNumber, frameNumber);

        setImageUrl(url);

    } catch (err) {
        console.log("An error occurred while loading images:", err)
    } finally {
        setImageLoadingState(false);
    }   
}