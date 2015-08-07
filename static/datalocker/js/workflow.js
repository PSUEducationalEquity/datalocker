
$(document).ready(function () {
    $('#locker-options').hide();
    $('select[id=states]').change( function(){
        var newText = $('option:selected',this).text();
          $('.state-status').text(" "+ newText);
      }
    );
   $('#enable-workflow').change(function(){
    if (this.checked) {
        $('#locker-options').show();
    } else {
        $('#locker-options').hide();
    }
    });
});