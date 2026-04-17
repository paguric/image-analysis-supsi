const TEXT = {

    high_pass_filter_title: "High Pass Filter",

    high_pass_filter: `
        Increasing this value improves the sensitivity of object detection.
        The result of this operation can be observed in the first step
        of the pipeline.
        This value must be odd.
    `,

    clahe_title: "Local Contrast",

    clahe: `
                <p>
                    This step applies <i>CLAHE (Contrast Limited Adaptive Histogram Equalization)</i>
                    to enhance the local contrast of the image.
                </p>

                <p>
                    Unlike global contrast adjustment, CLAHE works on small regions of the image,
                    improving visibility in areas with low contrast while preventing over-amplification
                    of noise.
                </p>

                <ol>
                    <li>
                        <strong>CLAHE Grid Dimension</strong>
                        <p>
                            Defines the size of the local regions (tiles) used for contrast enhancement.
                            Smaller values increase local detail but may also amplify noise, while larger
                            values produce smoother results.
                        </p>
                    </li>

                    <li>
                        <strong>CLAHE Local Contrast</strong>
                        <p>
                            Controls the contrast amplification limit. Higher values increase contrast
                            more aggressively, while lower values produce a more subtle enhancement.
                        </p>
                    </li>
                </ol>
            `,



    canny_title: "Canny Edge Detection",

    canny: `
        It allows detecting object edges using first-order partial derivatives
        (image gradient).

        Adjusting the <i>Canny Low Threshold</i> defines the minimum threshold
        for accepting a gradient.

        Adjusting the <i>Canny High Threshold</i> defines the threshold above which
        a pixel is considered definitely part of an edge.
    `,

    morphological_title: "Morphological Transformation",

    morphological: `
        <ol>
            <li>
                <strong>Morph Transformation Window Size</strong>
                <p>
                    Changing this parameter affects the size of the pixel window
                    being considered. A larger window helps better close the edges
                    detected in the previous step.
                    This value must be odd.
                </p>
            </li>

            <li>
                <strong>Morph Transformation Number of Iterations</strong>
                <p>
                    This parameter specifies how many times the
                    <i>morphological closing</i> operation is applied.
                </p>
            </li>
        </ol>
    `

};

export default TEXT;