# Instructions for readme_images
The images in this directory `FedFundsPlot/readme_images/` are used in the main repository [`README.md`](README.md). However, one image is only used for the GitHub social preview image. GitHub suggests that this image should be 1280x640px for best display. The Bokeh image produced by the code is 1630x1030px. We do the following to resize the image.

1. Open the image in Adobe Photoshop: **File** > **Open**
2. Adjust the canvas size: **Image** > **Canvas Size**. Because the 1630x1030px image is taller than the optimal 1280x640px GitHub size, we first adjust the canvas size. We have to add some width. So here adjust the width to 2060px [`1030 * 2` or `1030 * (1280 / 640)`] and keep the height at 1030px.
3. Adjust the image size: **Image** > **Image Size**. Now adjust the image size to the GitHub optimal 1280x640px. The dimesions will be correct and nothing will be stretched.
4. Save the image as [`fedfunds_gitfig.png`](readme_images/fedfunds_gitfig.png).
5. Upload the image [`fedfunds_gitfig.png`](readme_images/fedfunds_gitfig.png) as the GitHub social preview image by clicking on the [**Settings**](https://github.com/OpenSourceEcon/FedFundsPlot/settings) button in the upper-right of the main page of the repository and uploading the formatted image [`fedfunds_gitfig.png`](readme_images/fedfunds_gitfig.png) in the **Social preview** section.
