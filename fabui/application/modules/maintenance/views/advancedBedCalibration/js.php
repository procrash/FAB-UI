<script type="text/javascript">

/*
	var ticker_url = '';
	var interval_ticker;
	
	
	$(function () {
		
		$(".do-engage").on('click', do_engage);
		interval_ticker   = setInterval(ticker, 500);
		
		
	});
	
	
	
	function ticker(){
		
	    if(ticker_url != ''){
	        
	         $.get( ticker_url , function( data ) {
	           
	            if(data != ''){
	            	
	            	waitContent(data);
	              
	            }
	       }).fail(function(){ 
	           
	        });
	    }
	}
	
	
	
	function do_engage(){
		
		openWait('Engaging in process');
		
		var now = jQuery.now();
		ticker_url = '/temp/4axis_engage_' + now + '.trace'; 
		
		
		$.ajax({
			type: "POST",
			url : "<?php echo module_url('settings').'ajax/4axis_engage.php' ?>",
			data : {time: now},
			dataType: "json"
		}).done(function( data ) {
			
			
			closeWait();
			ticker_url = '';
			
			
		});
		
		
		
	}
	
*/

 var paper;
 var width = 531;
 var height = 531;
 
 var upperLeftScrew;
 var lowerLeftScrew;

 var upperRightScrew;
 var lowerRightScrew;

 var upperLeftSelected = false;
 var upperRightSelected = false;

 var lowerLeftSelected = false;
 var lowerRightSelected = false;
 
var selectedColor = "#fff";
var selectedFill ="#f00";

var unselectedColor = "#fff";
var unselectedFill = "#f00";

var mouseOverColor = "#000000";
var mouseOverFill = "#f00";

var onClick = function(event) {    
    
    var x = event.offsetX;
    var y = event.offsetY;
        
    var spacing = 50;
    var pos = {x: x, y: y, cx: x, cy: y}; // lazy routine: for both rects and circles

    // Upper left
    if (x<width/2-spacing && y<width/2-spacing) {
     upperLeftSelected=!upperLeftSelected;      
    } 

    // Upper Right
    if (x>width/2+spacing && y<width/2-spacing) {
     upperRightSelected = !upperRightSelected;      
    } 
    
    // Lower left
    if (x<width/2-spacing && y>width/2+spacing) {
     lowerLeftSelected = !lowerLeftSelected; 
    } 

    // Lower Right
    if (x>width/2+spacing && y>width/2+spacing) {
     lowerRightSelected = !lowerRightSelected;      
    } 
    
    updateVisibility();
    onMouseMove(event);    
};

function updateVisibility() {
    // Hide all elements which are currently not selected
    if (!upperLeftSelected)  {
        upperLeftScrew.hide().attr("stroke", unselectedColor); 
    }
    else { 
        upperLeftScrew.attr("stroke", selectedColor); 
    }
    
    if (!upperRightSelected) {
        upperRightScrew.hide().attr("stroke", unselectedColor); 
    } 
    else {
     upperRightScrew.attr("stroke", selectedColor);  
    }
    
    if (!lowerLeftSelected)  {
        lowerLeftScrew.hide().attr("stroke", unselectedColor); 
    }
    else {
        lowerLeftScrew.attr("stroke", selectedColor);      
    }
    
    if (!lowerRightSelected) {
        lowerRightScrew.hide().attr("stroke", unselectedColor);  
    }
    else {
        lowerRightScrew.attr("stroke", selectedColor);  
    
    }
}
 
var onMouseMove = function (event) {    
    
    var x = event.offsetX;
    var y = event.offsetY;
        
    var spacing = 50;
    var pos = {x: x, y: y, cx: x, cy: y}; // lazy routine: for both rects and circles

    updateVisibility();
        
    // Upper left
    if (x<width/2-spacing && y<width/2-spacing) {
     upperLeftScrew.show();      
     upperLeftScrew.attr({"stroke": mouseOverColor, "fill" : mouseOverFill});
    } 

    // Upper Right
    if (x>width/2+spacing && y<width/2-spacing) {
     upperRightScrew.show();    
     upperRightScrew.attr({"stroke": mouseOverColor, "fill" : mouseOverFill});  
    } 

    // Lower left
    if (x<width/2-spacing && y>width/2+spacing) {
     lowerLeftScrew.show();
     lowerLeftScrew.attr({"stroke": mouseOverColor, "fill" : mouseOverFill});      
    } 

    // Lower Right
    if (x>width/2+spacing && y>width/2+spacing) {
     lowerRightScrew.show();      
     lowerRightScrew.attr({"stroke": mouseOverColor, "fill" : mouseOverFill});
    } 
        
        
        
};


    var t;
    
    Raphael.fn.ball = function (x, y, r, hue) {
    hue = hue || 0;
    return this.set(
        this.ellipse(x, y + r - r / 5, r, r / 2).attr({fill: "rhsb(" + hue + ", 1, .25)-hsb(" + hue + ", 1, .25)", stroke: "none", opacity: 0}),
        this.ellipse(x, y, r, r).attr({fill: "r(.5,.9)hsb(" + hue + ", 1, .75)-hsb(" + hue + ", .5, .25)", stroke: "none"}),
        this.ellipse(x, y, r - r / 5, r - r / 20).attr({stroke: "none", fill: "r(.5,.1)#ccc-#ccc", opacity: 0})
    );
    
    
};

    
    function initialize() {
        // Creates canvas 320 × 200 at 10, 50
        paper = Raphael("drawingArea");
        var image = paper.image("bed.png", 10, 10, 521, 521);
        
        t = paper.text(width/2, height/2, "Select screws to calibrate").attr({
"font-family":"Arial","font-size":"30px", "font-weight": "normal", 
fill: "#ffffff", stroke:"black", "stroke-width": "1px",
"text-anchor" : "center" , "font-style": "normal"});


        upperLeftScrew  = paper.circle(60, 26, 8).attr({"fill": "#f00", "stroke" : "#fff"}).hide();
        lowerLeftScrew  = paper.circle(60, 531-17, 8).attr({"fill": "#f00", "stroke" : "#fff"}).hide();

        upperRightScrew = paper.circle(531-50, 26, 8).attr({"fill": "#f00", "stroke" : "#fff"}).hide();
        lowerRightScrew = paper.circle(531-50, 531-17, 8).attr({"fill": "#f00", "stroke" : "#fff"}).hide();


        // Event Handlers...
        image.mousemove(onMouseMove);
        image.click(onClick);
        


//         var R = Raphael("holder"), x = 310, y = 180, r = 150;
         //paper.ball(20, 20, 20, Math.random());


        // Creates circle at x = 50, y = 40, with radius 10
        //var circle = paper.circle(50, 40, 10);
        // Sets the fill attribute of the circle to red (#f00)
        //circle.attr("fill", "#f00");
        
        // Sets the stroke attribute of the circle to white
        //circle.attr("stroke", "#fff");
    }

</script>
