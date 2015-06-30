
var sub  = jQuery.parseJSON( data );

$.each(sub, function(key, value) {
    console.log(key + ' ' + value);
});

for (var key in sub) {
    console.log(key + ' ' + data[key]);
}