const TEXT = {
    home_title: "Welcome to the Image Analysis User Guide",

    differential_view_title: "Differential View Explained",

    single_roi_view_title: "Single ROI View Explained",

    home_description: `
        <p><strong>ROI</strong> stands for <em>Region of Interest</em>.</p>

        <p>To use this program:</p>
        <ol>
            <li>Upload the videos in the specified order.</li>
            <li>Enter the starting wavelength.</li>
            <li>Click the <strong>"Analyze"</strong> button.</li>
        </ol>

        <p>Once the analysis is complete, you can explore the detected ROIs and results.</p>
    `,

    differential_description: `
        <p>In this view:</p>
        <ul>
            <li>The <strong>left panel</strong> shows the list of detected ROIs.</li>
            <li>The <strong>top right</strong> displays the current differential frame.</li>
        </ul>

        <p>Click on an ROI in the list to inspect it in detail.</p>

        <p>On the <strong>right side</strong>, the following controls are available:</p>
        <ul>
            <li>Show detected contours</li>
            <li>Export analyzed data as a CSV file</li>
        </ul>

        <p>Below these controls, you can start a new analysis.</p>

        <p>At the <strong>bottom right</strong>, a slider allows you to change the wavelength
        and view the corresponding differential frame.</p>
    `,

    single_roi_view_description: `
        <p>In this page, you can modify the parameters for a specific ROI and re-run the analysis.</p>

        <p>Click <strong>"Save"</strong> to return to the previous page with the updated ROI.</p>

        <p>In the <strong>top right</strong>, you can view:</p>
        <ul>
            <li>The ROI from the previous video</li>
            <li>The ROI from the next video</li>
            <li>The differential ROI</li>
        </ul>

    

        <p>In the <strong>bottom right</strong>, the intermediate pipeline steps
        are displayed with your modified parameters applied.</p>
    `
};

export default TEXT;