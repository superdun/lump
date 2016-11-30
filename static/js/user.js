window.onload = function(){
    app.init()
}
var app ={
    init:function(){

        var n = $('#n').val()
        $('#n').change(function(){
            n = $('#n').val()
            if ($('.Y0_trs').length > (n*1)){
                while ($('.Y0_trs').length > (n*1)){
                    $('#Y0_input tr:last').remove()
                }
            }
            else{

                app.makeY0Table($('.Y0_trs').length,n-$('.Y0_trs').length)
            }

        })
        app.makeY0Table(0,n)
    },
    makeY0Table:function(base,n){
        for(var i=0;i<n;i++){
            $('#Y0_input').append("<tr class='Y0_trs'><td>"+(i+base+1)+"</td><td><input  type=\"text\" class ='Y0_names form-control' value='a'></td><td><input type=\"number\"  value=\"0.0001\" width='2000px' step=\"0.1\" max=\"1\" min=\"0\" class ='form-control   YO_values'></td></tr>")
        }
    }
}