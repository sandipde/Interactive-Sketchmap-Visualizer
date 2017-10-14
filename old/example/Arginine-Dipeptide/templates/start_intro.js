function startIntro(){
  var intro = introJs();
  intro.setOption('tooltipPosition', 'auto');
  intro.setOption('showProgress', true)
    intro.setOptions({
      steps: [
        { 
          intro: "<h3 class='w3-center w3-blue-grey' style='width:300px ; text-align:center '> What is Sketchmap ? </h3> <br> <p style='text-align:center; width:300px;'>Sketch-map is a non-linear dimensionality reduction algorithm that is particularly well suited for examining high-dimensionality data that is routinely produced in atomistic simulations. It transforms the connectivity between a set of high dimensionality data points in 2-dimension while putting higher importance to proximity matching. While the similarity between a pair of atomic structures can be measured in various ways, we used SOAP-REMatch kernel, developed in our group for this purpose.</p>"
        },
        {
          element: document.querySelector('#step1'),
          intro: "<p style='width:300px ; text-align:justify'>This is your interactive sketchmap panel. You can pan, zoom  and select the points. Each point on the plot represents an atomic configuration. If two structures are similar the points are close in the map. Clustering of points signifies a common structural motif. </p>",
      //  position: 'top'
        },
        
        {
          element: document.querySelectorAll('#step2')[0],
          intro: "<p style='width:300px; text-align:justify'> You can visualize the atomic structure here by selecting a point on the map with your mouse </p>",
          position: 'bottom'
        },
        {
          element: document.querySelectorAll('#step3')[0],
          intro: "<p style='width:300px; text-align:justify'>By clicking the analyse button you can open the displayed structure in a pop up window whereyou can use bigger display and additional tools for structural analysis. </p>",
          position: 'top'
        },
        {
          element: document.querySelectorAll('#step4')[0],
          intro: "<p style='width:300px; text-align:justify'>The hold button can be used to hold the displayed structure in the smaller display. This can be useful when comparing two structures from the map.</p>",
          position: 'top'
        },
        {
          element: '#step5',
          intro: "<p style='width:300px; text-align:justify'> You can also download a html file containing essential feature of the interactive map for offline usage. That's all you need to know for now. Have fun with Sketchmap !  </p>"
        }
      ]
    });
    intro.start();
}
