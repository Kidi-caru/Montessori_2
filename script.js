/*====================================================
=            MONTESSORI INVENTARIO 3.0
====================================================*/

/*==========================
CONFIRMAR ELIMINACIÓN
==========================*/

function confirmarEliminar(){

    return confirm("¿Está seguro de eliminar este registro?");

}

/*==========================
VISTA PREVIA DE IMAGEN
==========================*/

function vistaPrevia(evento){

    const archivo = evento.target.files[0];

    if(!archivo) return;

    const lector = new FileReader();

    lector.onload=function(){

        let img=document.getElementById("preview");

        if(img){

            img.src=lector.result;

            img.style.display="block";

        }

    }

    lector.readAsDataURL(archivo);

}

/*==========================
BUSCADOR DE TABLAS
==========================*/

function buscarTabla(idInput,idTabla){

    let texto=document.getElementById(idInput).value.toLowerCase();

    let filas=document.querySelectorAll("#"+idTabla+" tbody tr");

    filas.forEach(function(fila){

        let contenido=fila.innerText.toLowerCase();

        fila.style.display=contenido.includes(texto) ? "" : "none";

    });

}

/*==========================
VALIDACIÓN DE FORMULARIOS
==========================*/

function validarFormulario(idFormulario){

    let formulario=document.getElementById(idFormulario);

    if(!formulario) return;

    formulario.addEventListener("submit",function(e){

        let campos=formulario.querySelectorAll("[required]");

        let valido=true;

        campos.forEach(function(campo){

            if(campo.value.trim()==""){

                campo.classList.add("is-invalid");

                valido=false;

            }else{

                campo.classList.remove("is-invalid");

            }

        });

        if(!valido){

            e.preventDefault();

            alert("Complete todos los campos obligatorios.");

        }

    });

}

/*==========================
CALCULAR STOCK
==========================*/

function verificarStock(stock){

    if(stock<=5){

        return "Bajo";

    }

    if(stock<=20){

        return "Medio";

    }

    return "Alto";

}

/*==========================
MENÚ RESPONSIVE
==========================*/

function abrirMenu(){

    let menu=document.querySelector(".sidebar");

    if(menu){

        menu.classList.toggle("mostrar");

    }

}

/*==========================
SCROLL SUAVE
==========================*/

window.addEventListener("load",function(){

    window.scrollTo({

        top:0,

        behavior:"smooth"

    });

});

/*==========================
MENSAJE AUTOMÁTICO
==========================*/

setTimeout(function(){

    let alerta=document.querySelector(".alert");

    if(alerta){

        alerta.style.display="none";

    }

},5000);

/*====================================================
=            SPACEVIEW 3.0
====================================================*/

let canvas = document.getElementById("canvasSpace");

if(canvas){

    let ctx = canvas.getContext("2d");

    function dibujarEspacio(
        largoEspacio,
        anchoEspacio,
        largoMueble,
        anchoMueble
    ){

        ctx.clearRect(0,0,canvas.width,canvas.height);

        let margen = 40;

        let escala = Math.min(

            (canvas.width-80)/largoEspacio,

            (canvas.height-80)/anchoEspacio

        );

        let espacioW = largoEspacio * escala;

        let espacioH = anchoEspacio * escala;

        let muebleW = largoMueble * escala;

        let muebleH = anchoMueble * escala;

        /* Espacio */

        ctx.fillStyle="#EEEEEE";

        ctx.fillRect(

            margen,

            margen,

            espacioW,

            espacioH

        );

        ctx.strokeStyle="#444";

        ctx.lineWidth=3;

        ctx.strokeRect(

            margen,

            margen,

            espacioW,

            espacioH

        );

        /* Mueble */

        ctx.fillStyle="#4CAF50";

        ctx.fillRect(

            margen+15,

            margen+15,

            muebleW,

            muebleH

        );

        ctx.strokeStyle="#2E7D32";

        ctx.strokeRect(

            margen+15,

            margen+15,

            muebleW,

            muebleH

        );

        /* Texto */

        ctx.fillStyle="#000";

        ctx.font="16px Arial";

        ctx.fillText(

            "Espacio",

            margen,

            margen-10

        );

        ctx.fillText(

            "Mueble",

            margen+20,

            margen+35

        );

    }

}

/*====================================================
CALCULAR SI CABE
====================================================*/

function calcularEspacio(){

    let espacioL = Number(document.getElementById("espacio_largo").value);

    let espacioA = Number(document.getElementById("espacio_ancho").value);

    let muebleL = Number(document.getElementById("mueble_largo").value);

    let muebleA = Number(document.getElementById("mueble_ancho").value);

    let resultado = document.getElementById("resultado");

    if(

        !espacioL ||

        !espacioA ||

        !muebleL ||

        !muebleA

    ){

        return;

    }

    let porcentaje =

    ((muebleL*muebleA)/(espacioL*espacioA))*100;

    porcentaje = porcentaje.toFixed(1);

    if(

        muebleL<=espacioL &&

        muebleA<=espacioA

    ){

        resultado.innerHTML=

        "✅ El mueble cabe.<br><br>Ocupa el <b>"+

        porcentaje+

        "%</b> del espacio.";

        resultado.className="alert alert-success";

    }

    else{

        resultado.innerHTML=

        "❌ El mueble NO cabe.";

        resultado.className="alert alert-danger";

    }

    if(typeof dibujarEspacio==="function"){

        dibujarEspacio(

            espacioL,

            espacioA,

            muebleL,

            muebleA

        );

    }

}

/*====================================================
ROTAR MUEBLE
====================================================*/

function rotarMueble(){

    let largo=document.getElementById("mueble_largo");

    let ancho=document.getElementById("mueble_ancho");

    let aux=largo.value;

    largo.value=ancho.value;

    ancho.value=aux;

    calcularEspacio();

}

/*====================================================
CALCULAR AUTOMÁTICAMENTE
====================================================*/

document.addEventListener("input",function(){

    if(

        document.getElementById("espacio_largo")

    ){

        calcularEspacio();

    }

});

/*====================================================
REINICIAR CANVAS
====================================================*/

function limpiarCanvas(){

    if(canvas){

        ctx.clearRect(

            0,

            0,

            canvas.width,

            canvas.height

        );

    }

}

/*====================================================
=            MONTESSORI INVENTARIO 3.0
=          SCRIPT FINAL
====================================================*/

/*==========================
VISTA PREVIA DE IMAGEN
==========================*/

const imagenInput = document.getElementById("imagen");

if(imagenInput){

    imagenInput.addEventListener("change",function(e){

        const archivo=e.target.files[0];

        if(!archivo) return;

        const lector=new FileReader();

        lector.onload=function(evento){

            let preview=document.getElementById("preview");

            if(preview){

                preview.src=evento.target.result;

                preview.style.display="block";

            }

        }

        lector.readAsDataURL(archivo);

    });

}

/*==========================
BUSCADOR EN TIEMPO REAL
==========================*/

const buscador=document.getElementById("buscar");

if(buscador){

    buscador.addEventListener("keyup",function(){

        let valor=this.value.toLowerCase();

        let filas=document.querySelectorAll("tbody tr");

        filas.forEach(function(fila){

            fila.style.display=

            fila.innerText.toLowerCase().includes(valor)

            ? ""

            : "none";

        });

    });

}

/*==========================
BOTÓN VOLVER ARRIBA
==========================*/

const botonTop=document.createElement("button");

botonTop.innerHTML="↑";

botonTop.className="boton-flotante";

document.body.appendChild(botonTop);

botonTop.style.display="none";

window.addEventListener("scroll",function(){

    if(window.scrollY>300){

        botonTop.style.display="flex";

    }else{

        botonTop.style.display="none";

    }

});

botonTop.addEventListener("click",function(){

    window.scrollTo({

        top:0,

        behavior:"smooth"

    });

});

/*==========================
LOADER
==========================*/

window.addEventListener("load",function(){

    let loader=document.getElementById("loader");

    if(loader){

        loader.style.display="none";

    }

});

/*==========================
IMPRESIÓN
==========================*/

function imprimirReporte(){

    window.print();

}

/*==========================
EXPORTAR TABLA A CSV
==========================*/

function exportarCSV(){

    let tabla=document.querySelector("table");

    if(!tabla){

        alert("No existe una tabla.");

        return;

    }

    let csv=[];

    let filas=tabla.querySelectorAll("tr");

    filas.forEach(function(fila){

        let datos=[];

        fila.querySelectorAll("th,td").forEach(function(col){

            datos.push(col.innerText);

        });

        csv.push(datos.join(","));

    });

    let archivo=new Blob([csv.join("\n")],{

        type:"text/csv"

    });

    let enlace=document.createElement("a");

    enlace.download="reporte.csv";

    enlace.href=URL.createObjectURL(archivo);

    enlace.click();

}


function animarNumero(id,valor){

    let elemento=document.getElementById(id);

    if(!elemento) return;

    let actual=0;

    let tiempo=setInterval(function(){

        actual++;

        elemento.innerHTML=actual;

        if(actual>=valor){

            clearInterval(tiempo);

        }

    },20);

}


function reloj(){

    let fecha=new Date();

    let hora=fecha.toLocaleTimeString();

    let reloj=document.getElementById("reloj");

    if(reloj){

        reloj.innerHTML=hora;

    }

}

setInterval(reloj,1000);


const tarjetas=document.querySelectorAll(".card");

const observador=new IntersectionObserver(function(entradas){

    entradas.forEach(function(entrada){

        if(entrada.isIntersecting){

            entrada.target.classList.add("fade");

        }

    });

});

tarjetas.forEach(function(card){

    observador.observe(card);

});


window.addEventListener("load",function(){

    console.log("Montessori Inventario 3.0 iniciado correctamente.");

});