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
            data.n=n
            canvas.init()
        })
        app.makeY0Table(0,n)
        data.n=n
        data.init()
        canvas.init()
        mouse.init()

    },
    makeY0Table:function(base,n){
        for(var i=0;i<n;i++){
            $('#Y0_input').append("<tr class='Y0_trs'><td>"+(i+base+1)+"</td><td><input  type=\"text\" class ='Y0_names form-control' value='a'></td><td><input type=\"number\"  value=\"0.0001\" width='2000px' step=\"0.1\" max=\"1\" min=\"0\" class ='form-control   YO_values'></td></tr>")
        }
    },

}

var canvas ={
    init:function(){
       var width = $('#canvasContainer').width()
       $('#canvas').attr({width:width+'px',height:width+'px'})
       canvas.ctx=document.getElementById('canvas').getContext("2d")
       var ctx = canvas.ctx
       canvas.sqWidth = width/(data.n*1+1)
       for(var i=1;i<=data.n*1;i++){
           for (var j = 0;j<data.n*1;j++){
            ctx.fillStyle = "#000000";
            ctx.strokeStyle = "#000000";
            ctx.lineWidth = 2
            //ctx.fillRect(width*i/(data.n*1+1), width*j/(data.n*1+1), width/(data.n*1+1), width/(data.n*1+1));
            ctx.strokeRect(width*i/(data.n*1+1), width*j/(data.n*1+1), width/(data.n*1+1), width/(data.n*1+1))
           }

       }
    },
    changeColor:function(x,y,status){
            var ctx = canvas.ctx

            ctx.fillStyle = "#ffffff";
            ctx.strokeStyle = "#000000";
            ctx.lineWidth = 2
            if (status =='checkin'){
            ctx.fillStyle = "#000000";
            ctx.strokeStyle = "#ffffff";
            }
            ctx.fillRect(x, y, canvas.sqWidth, canvas.sqWidth);
            ctx.strokeRect(x, y, canvas.sqWidth, canvas.sqWidth)

    }

}
var mouse = {
    init:function(){
        $('#canvas').click(function(e){
            var xx = event.pageX;
            var yy = event.pageY;
            var px = $('#canvas').offset().left
            var py = $('#canvas').offset().top
            mouse.getStartPoint(xx-px,yy-py)
        })
    },
    getStartPoint:function(x,y){
        if(!(x<canvas.sqWidth || y>canvas.sqWidth*(data.n*1))){
            var sqx = x-(x%canvas.sqWidth)
            var sqy = y-(y%canvas.sqWidth)
            var nx = Math.round(sqx/canvas.sqWidth)-1
            var ny = Math.round(sqy/canvas.sqWidth)

            if(data.K_model[nx][ny] == 0){
                data.K_model[nx][ny] = 1
                canvas.changeColor(sqx,sqy,'checkin')
            }
            else{
                data.K_model[nx][ny] = 0
                canvas.changeColor(sqx,sqy,'checkout')
            }
        }
    }
}
var data = {
    n:3,
    K_model:[],
    init:function(){
        for (var i=0;i<data.n;i++){
            var row = []
            for (var j=0;j<data.n;j++){
               row.push(0)
            }
            data.K_model.push(row)
        }
    },
    getFactors:function(){
    }
}