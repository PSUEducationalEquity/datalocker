
$(document).ready(function () {
  // //opens the users modal dialog
  //   var e = document.getElementById("states");
  //   var strUser = e.options[e.selectedIndex].value;
  //   $("#state-status").text(" "+strUser);




    $('select[id=states]').change(
      function(){
        var newText = $('option:selected',this).text();
          $('.state-status').text(" "+ newText);
      }
    );
});