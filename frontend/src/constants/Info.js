const TEXT = {
    home_title: "Welcome to the Image Analysis User Guide",

    differential_view_title: "Differential View Explained",

    single_roi_view_title: "Single ROI View Explained",

    home_description: `
        <p><strong>ROI</strong> stands for <em>Region of Interest</em>.</p>

        <p>To use this program correctly:</p>
        <ol>
            <li>Upload the videos in the order indicated in the upload box.</li>
            <li>Enter the starting wavelength.</li>
            <li>Click the <strong>"Analyze"</strong> button.</li>
        </ol>

        <p>Once the analysis is complete, you will be able to explore the detected ROIs and results.</p>
    `,

    differential_description: `
        <p>In this view:</p>
        <ul>
            <li>On the <strong>left</strong>, you will find the list of detected ROIs.</li>
            <li>On the <strong>top right</strong>, the current differential frame is displayed.</li>
        </ul>

        <p>By clicking on an ROI in the list, you can inspect it in more detail.</p>

        <p>On the <strong>right side</strong>, you will find several controls:</p>
        <ul>
            <li>Show detected contours</li>
            <li>Export the analyzed data as a CSV file</li>
            <li>Export the current global parameterization</li>
            <li>Import settings from a previously saved parameterization</li>
        </ul>

        <p>Below these controls, you can start a new analysis.</p>

        <p>At the <strong>bottom right</strong>, a slider allows you to change the wavelength and 
        view the corresponding differential frame.</p>
    `,

    single_roi_view_description: `
        <p>In this page, you can modify the parameters for a specific ROI and re-run the analysis.</p>

        <p>Clicking <strong>"Save"</strong> will return you to the previous page with the updated ROI.</p>

        <p>In the <strong>top right</strong>, you can view:</p>
        <ul>
            <li>The ROI from the previous video</li>
            <li>The ROI from the next video</li>
            <li>The differential ROI</li>
        </ul>

        <p>In the <strong>bottom left</strong>, you will see the current intermediate pipeline steps.</p>

        <p>In the <strong>bottom right</strong>, the pipeline steps are shown again, 
        but with your modified parameters applied.</p>
    `
};

export default TEXT;