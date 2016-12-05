window.onload = function(){
    app.init()
}
var app ={
    init:function(){
        $('#getK').attr('disabled',true)
        $('#getResult').attr('disabled',true)
        $('.Y0_names').attr('disabled',false)
        $('.mol_mass').attr('disabled',false)
        app.factorStorage = localStorage;
        if(app.factorStorage.n>=3){
            $('#n').val(app.factorStorage.n*1)
        }
        if(app.factorStorage.data){
            $('#getK').attr('disabled',false)
            app.makeFactorResultTableWhenInit(app.factorStorage.data)
        }
        if(app.factorStorage.preData){
            $('#getResult').attr('disabled',false)
            app.makePreFactorResultTable(app.factorStorage.preData)
        }

        if(app.factorStorage.factorsCount){
            data.count = app.factorStorage.factorsCount
        }
        $('#clearFactors').click(function(){
            app.rmFactors()
        })
        $('#clearPreFactors').click(function(){
            app.rmPreFactors()
        })

        $('#inputFactors').click(function(){data.getFactors()})
        $('#inputPreFactors').click(function(){data.getPreFactors()})
        $('#getK').click(function(){
            $.ajax({
                type:'POST',
                url:'/getK',
                data:app.factorStorage,
                dataType:'json'
            })
        })
        var n = $('#n').val()
        $('#n').change(function(){
            app.factorStorage.clear();
            $('#getK').attr('disabled',true)
            $('#getResult').attr('disabled',true)
            app.makePreFactorResultTable('')
            app.makeFactorResultTableWhenInit('')
            n = $('#n').val()
            if ($('.Y0_trs').length > (n*1)){
                while ($('.Y0_trs').length > (n*1)){
                    $('#Y0_input tr:last').remove()
                }
            }
            else{

                app.makeY0Table($('.Y0_trs').length,n-$('.Y0_trs').length)
            }
            app.factorStorage.n = data.n=n
            canvas.init()
        })

        app.factorStorage.n = data.n=n
        app.makeY0Table(0,n)
        if(app.factorStorage.data){
             $('.Y0_names').attr('disabled',true)
            $('.mol_mass').attr('disabled',true)
        }
        data.init()
        canvas.init()

        if(app.factorStorage.Y0_names){
            data.Y0_names = app.factorStorage.Y0_names.split(',')
            canvas.writeText()
        }
        if(app.factorStorage.K_model){
            var mat =[]
            var rawMat = app.factorStorage.K_model.split(',')

          for (var i=0;i<data.n;i++){
            var row = rawMat.slice(i*data.n,(i+1)*data.n)
            mat.push(row)
        }
        data.K_model = mat
        app.initNet(mat)
        }

        mouse.init()

    },
    makeY0Table:function(base,n){
        for(var i=0;i<n;i++){
            $('#Y0_input').append("<tr class='Y0_trs'><td>"+(i+base+1)+"</td><td><input  type=\"text\" class ='Y0_names form-control'></td><td><input type=\"number\"  value=\"0\"  step=\"0.1\"  min=\"0\" class ='form-control   mol_mass'></td> <td><input type=\"number\"  value=\"0\" width='2000px' step=\"0.1\" max=\"1\" min=\"0\" class ='form-control   YO_values'></td><td><input type=\"number\"  value=\"0\"  step=\"0.1\" max=\"1\" min=\"0\" class ='form-control   Y_values'></td></tr>")
        }
    },
    makeFactorResultTable:function(d){
        $('#factorShow').text($('#factorShow').text()+data.count+'===========\n'
        +d+'\n')

    },
    makeFactorResultTableWhenInit:function(d){
        var d = d.split(', ')
        for (var i=1;i<d.length+1;i++){
              $('#factorShow').text($('#factorShow').text()+i+'===========\n'
            +d[i-1]+'\n')
        }
        if (d==''){
            $('#factorShow').text('')
        }


    },
    makePreFactorResultTable:function(d){
        $('#preFactorShow').text('待预测条件===========\n'
        +d)
        if (d==''){
            $('#preFactorShow').text('')
        }
    },
    initNet:function(mat){
       var ctx = canvas.ctx
       ctx.lineWidth = 2
       ctx.fillStyle = "#000000";
       ctx.strokeStyle = "#ffffff";
       for(var i=1;i<=data.n*1;i++){
           for (var j = 0;j<data.n*1;j++){

            if(mat[i-1][j]==1){
            console.log(mat)
                ctx.fillRect((i)*canvas.sqWidth, j*canvas.sqWidth, canvas.sqWidth, canvas.sqWidth);
                ctx.strokeRect((i)*canvas.sqWidth, j*canvas.sqWidth, canvas.sqWidth, canvas.sqWidth)

            }

           }
       }
    },
    rmFactors:function(){
        app.factorStorage.removeItem('data')
        $('#factorShow').text('')
        $('#getK').attr('disabled',true)
        $('.Y0_names').attr('disabled',false)
        $('.mol_mass').attr('disabled',false)
    },
    rmPreFactors:function(){
        app.factorStorage.removeItem('preData')
        $('#preFactorShow').text('')
        $('#getResult').attr('disabled',true)
    }

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

    },
    writeText:function(){
        var ctx = canvas.ctx
        var size = canvas.sqWidth/3
        ctx.clearRect(0,0,canvas.sqWidth,canvas.sqWidth*(data.n*1+1));
        ctx.clearRect(0,canvas.sqWidth*(data.n*1),canvas.sqWidth*(data.n*1+1),canvas.sqWidth);

        ctx.font=size+"px Georgia";

        for(var i=0;i<data.n*1;i++){
            ctx.fillText(data.Y0_names[i],canvas.sqWidth*0.4,canvas.sqWidth*(i+0.5),canvas.sqWidth-8);
            ctx.fillText(data.Y0_names[i],canvas.sqWidth*(i+1)+10,canvas.sqWidth*(data.n*1+0.2),canvas.sqWidth-8);

        }
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
        app.factorStorage.K_model = data.K_model
    }
}
var data = {
    n:3,
    count:0,
    init:function(){

        data.K_model=[]
        data.Y0_values=[]
        data.Y0_names=[]
        data.Y_values=[]
        data.t_resid=0
        data.T=0
        data.OR=0
        data.p=0
        data.nitro = 0
        data.aro = 0
        data.mol_mass=[]
        for (var i=0;i<data.n;i++){
            var row = []
            for (var j=0;j<data.n;j++){
               row.push(0)
            }
            data.K_model.push(row)
        }
    },
    getFactors:function(){
        data.init()
        $.each($('.YO_values'),function(k,v){
            data.Y0_values.push(v.value)
        })
        $.each($('.Y0_names'),function(k,v){
            data.Y0_names.push(v.value)
        })
        $.each($('.Y_values'),function(k,v){
            data.Y_values.push(v.value)
        })
        $.each($('.mol_mass'),function(k,v){
            data.mol_mass.push(v.value)
        })
        data.t_resid = $('#t_resid').val()
        data.T = $('#T').val()
        data.p = $('#p').val()
        data.nitro = $('#nitro').val()
        data.aro =$('#aro').val()
        data.OR = $('#OR').val()
        data.R = $('#R').val()
        canvas.writeText()
        data.count++
        var tempData = {
        Y0_names:data.Y0_names,
        Y0_values:data.Y0_values,
        t_resid:data.t_resid,
        T:data.T,
        p:data.p,
        OR:data.OR,
        R:data.R,
        Y_values:data.Y_values,
        nitro:data.nitro,
        aro:data.aro,
        mol_mass:data.mol_mass
        }
        $('.Y0_names').attr('disabled',true)
        $('.mol_mass').attr('disabled',true)
        app.makeFactorResultTable(JSON.stringify(tempData))
        if(app.factorStorage.data){
            app.factorStorage.data = JSON.stringify(tempData)+', '+app.factorStorage.data
        }
        else{
            app.factorStorage.data = JSON.stringify(tempData)
        }
        app.factorStorage.Y0_names =data.Y0_names
        app.factorStorage.K_model = data.K_model
        app.factorStorage.mol_mass = data.mol_mass
        $('#getK').attr('disabled',false)

    },
    getPreFactors:function(){
        data.init()
        $.each($('.YO_values'),function(k,v){
            data.Y0_values.push(v.value)
        })
        $.each($('.Y0_names'),function(k,v){
            data.Y0_names.push(v.value)
        })
        $.each($('.mol_mass'),function(k,v){
            data.mol_mass.push(v.value)
        })
        data.t_resid = $('#t_resid').val()
        data.T = $('#T').val()
        data.p = $('#p').val()
        data.OR = $('#OR').val()
        data.R = $('#R').val()
        data.nitro = $('#nitro').val()
        data.aro =$('#aro').val()
        canvas.writeText()
        data.count++
        var tempData = {
        Y0_names:data.Y0_names,
        Y0_values:data.Y0_values,
        t_resid:data.t_resid,
        T:data.T,
        p:data.p,
        OR:data.OR,
        R:data.R,
        nitro:data.nitro,
        aro:data.aro,
        mol_mass:data.mol_mass
        }
        $('.Y0_names').attr('disabled',true)
        app.makePreFactorResultTable(JSON.stringify(tempData))
        app.factorStorage.preData = JSON.stringify(tempData)
        app.factorStorage.factorsCount = data.count
        app.factorStorage.Y0_names =data.Y0_names
        app.factorStorage.K_model = data.K_model
        app.factorStorage.mol_mass = data.mol_mass

        $('#getResult').attr('disabled',false)
    }
}