
var BASE_URL = "http://127.0.0.1:5000/opera/v1"
var data = [];

function customEngine(input) {
    var operaIFrame = document.getElementById("opera").contentWindow.document;
    var expandedQuery = document.getElementById("expanded_query_result");

    if(expandedQuery != null) {
        expandedQuery.innerHTML = '';
        var textNode = document.createTextNode(data['expanded_query']);
        expandedQuery.appendChild(textNode);
    }
    
    let frameElement = document.getElementById("opera");
    let doc = frameElement.contentDocument;
    doc.body.innerHTML = doc.body.innerHTML + '<style>a {margin: 0px 0px 0px 0px;}</style>';
    
    operaIFrame.open();
    
    var out = "";
    console.log(data['results']);
    var i;

     for(i = 0; i < data['results'].length; i++) {
         out += '<a style="color:white"; href="' + data['results'][i].url + '">' +
         data['results'][i].title + '</a><br>' + "<p style='color:white'; >"+
         data['results'][i].content.substring(0,500) +"............"+"</p>";
    }
    operaIFrame.write(out);
    
    operaIFrame.close();
}

function queryToGoogleBing() {
    var input = document.getElementById("UserInput").value;
    document.getElementById("google").src = "https://www.google.com/search?igu=1&source=hp&ei=lheWXriYJ4PktQXN-LPgDA&q=" + input;
    document.getElementById("bing").src = "https://www.bing.com/search?q=" + input;
}

// function search() {
//     var input = document.getElementById("UserInput").value;
    
//     var page_rank = document.getElementById("page_rank").checked;
//     var hits = document.getElementById("hits").checked;
//     var flat_clustering = document.getElementById("flat_clustering").checked;
//     var single_HAC_clustering = document.getElementById("single_HAC_clustering").checked;
//     var complete_HAC_clustering = document.getElementById("complete_HAC_clustering").checked;
//     var association_qe = document.getElementById("association_qe").checked;
//     var metric_qe = document.getElementById("metric_qe").checked;
//     var scalar_qe = document.getElementById("scalar_qe").checked;
//     var type;
    
//     if (page_rank) {
//         type = "page_rank";
//     }
//     else if (hits) {
//         type = "hits";
//     }
//     else if (flat_clustering) {
//         type = "flat_clustering";
//     }
//     else if (single_HAC_clustering) {
//         type = "single_HAC_clustering";
//     }
//     else if (complete_HAC_clustering) {
//         type ="complete_HAC_clustering";
//     }
//     else if (association_qe) {
//         type ="association_qe";
//     }
//     else if (metric_qe) {
//         type ="metric_qe";
//     }
//     else if (scalar_qe) {
//         type ="scalar_qe";
//     }
    
    
//     $.get( BASE_URL, {"query": input, "type": type})
    
//     .done(function(resp) {
//         data = resp
//         customEngine(input);

//     })
//     .fail(function(e) {
        
//         console.log("error", e)
//     })
// }


function search() {
  var input = document.getElementById("UserInput").value;
 
  // Capture the selected options from each group
  var relevanceOption = document.querySelector(
    'input[name="relevanceType"]:checked'
  )
    ? document.querySelector('input[name="relevanceType"]:checked').value
    : null;
  var clusteringOption = document.querySelector(
    'input[name="clusteringType"]:checked'
  )
    ? document.querySelector('input[name="clusteringType"]:checked').value
    : null;
  var expansionOption = document.querySelector(
    'input[name="expansionType"]:checked'
  )
    ? document.querySelector('input[name="expansionType"]:checked').value
    : null;
 
  // Build the data object to send with the request
  var requestData = {
    query: input,
    relevance: relevanceOption,
    clustering: clusteringOption,
    expansion: expansionOption,
  };
  console.log("" + requestData)
 
  // Send the AJAX request
  $.get(BASE_URL, requestData)
    .done(function (resp) {
      data = resp;
      customEngine(input);
    })
    .fail(function (e) {
      console.log("error", e);
    });
}
